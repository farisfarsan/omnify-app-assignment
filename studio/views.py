from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from studio.utils import token_email_match
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.timezone import now, localtime
import logging
import json
from .models import FitnessClass, Booking
from .serializers import FitnessClassSerializer, BookingSerializer
from django.db import transaction
# ------------------ Logging Setup ------------------

logging.basicConfig(
    filename='booking_activity.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ------------------ API: Class List ------------------

class ClassListView(generics.ListAPIView):
    queryset = FitnessClass.objects.filter(date_time__gte=now()).order_by('date_time')
    serializer_class = FitnessClassSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}

    def list(self, request, *args, **kwargs):
        valid, error_response = token_email_match(request)
        if not valid:
            logger.warning(f"GET /classes/ blocked: token user = {request.user.email}")
            return error_response

        response = super().list(request, *args, **kwargs)
        logger.info(f"GET /classes/ by {request.user.email} response: {response.data}")
        return response

# ------------------ API: Book Class ------------------
class BookClassView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        class_id = request.data.get('class_id')
        client_name = request.data.get('client_name')

        if not (class_id and client_name):
            logger.warning("Booking failed: Missing required fields.")
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        
        if client_name.strip().lower() != request.user.first_name.strip().lower():
            logger.warning(f"Booking blocked: name mismatch for token user {request.user.email}")
            return Response({'error': 'Client name must match your registered name.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            
            fitness_class = FitnessClass.objects.select_for_update().get(id=class_id)

            if fitness_class.available_slots <= 0:
                logger.info(f"Booking failed: No available slots for class {fitness_class.name}.")
                return Response({'error': 'No available slots.'}, status=status.HTTP_400_BAD_REQUEST)

          
            Booking.objects.create(
                fitness_class=fitness_class,
                client_name=client_name,
                client_email=request.user.email
            )

            fitness_class.available_slots -= 1
            fitness_class.save()

            logger.info(f"Booking successful: {client_name} booked {fitness_class.name} at {localtime(fitness_class.date_time)}")
            return Response({'message': 'Booking successful.'}, status=status.HTTP_201_CREATED)

        except FitnessClass.DoesNotExist:
            return Response({'error': 'Class not found.'}, status=status.HTTP_404_NOT_FOUND)

# ------------------ API: View User Bookings ------------------

class UserBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_email = self.request.user.email
        logger.info(f"GET /bookings for authenticated user: {user_email}")
        return Booking.objects.filter(client_email=user_email)

    def get_serializer_context(self):
        return {"request": self.request}

    def list(self, request, *args, **kwargs):
        if 'email' in request.query_params:
            logger.warning(
                f"Blocked request: Attempt to override email using query param. Token belongs to {request.user.email}"
            )
            return Response(
                {"error": "Passing 'email' in query params is not allowed."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().list(request, *args, **kwargs)

# ------------------ API: Signup ------------------

@csrf_exempt
@api_view(['POST'])
def signup_view(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not (name and email and password):
            return Response({'error': 'All fields are required (name, email, password).'}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=400)

        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'message': 'Signup successful', 'token': token.key})
    
    except Exception as e:
        return Response({'error': str(e)}, status=400)

# ------------------ API: Login ------------------

@csrf_exempt
@api_view(['POST'])
def login_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        if not (email and password):
            return Response({'error': 'Email and password are required.'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=401)

        user = authenticate(username=user.username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'message': 'Login successful', 'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)
    
    except Exception as e:
        return Response({'error': str(e)}, status=400)