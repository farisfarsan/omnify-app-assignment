from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils.timezone import now, localtime
from .models import FitnessClass, Booking
from .serializers import FitnessClassSerializer, BookingSerializer
import logging

# Set up logging to file
logging.basicConfig(
    filename='booking_activity.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# ------------------ GET /classes ------------------
class ClassListView(generics.ListAPIView):
    queryset = FitnessClass.objects.filter(date_time__gte=now()).order_by('date_time')
    serializer_class = FitnessClassSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        logger.info(f"GET /classes/ response: {response.data}")
        return response


# ------------------ POST /book ------------------
class BookClassView(generics.CreateAPIView):
    serializer_class = BookingSerializer

    def post(self, request, *args, **kwargs):
        class_id = request.data.get('class_id')
        client_name = request.data.get('client_name')
        client_email = request.data.get('client_email')

        if not (class_id and client_name and client_email):
            logger.warning("Booking failed: Missing required fields.")
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            fitness_class = FitnessClass.objects.get(id=class_id)
        except FitnessClass.DoesNotExist:
            logger.warning(f"Booking failed: Class with id {class_id} not found.")
            return Response({'error': 'Class not found.'}, status=status.HTTP_404_NOT_FOUND)

        if fitness_class.available_slots <= 0:
            logger.info(f"Booking failed: No available slots for class {fitness_class.name}.")
            return Response({'error': 'No available slots.'}, status=status.HTTP_400_BAD_REQUEST)

        Booking.objects.create(
            fitness_class=fitness_class,
            client_name=client_name,
            client_email=client_email
        )

        fitness_class.available_slots -= 1
        fitness_class.save()

        logger.info(f"Booking successful: {client_name} booked {fitness_class.name} at {localtime(fitness_class.date_time)}")
        return Response({'message': 'Booking successful.'}, status=status.HTTP_201_CREATED)


# ------------------ GET /bookings?email=user@example.com ------------------
class UserBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        email = self.request.query_params.get('email', '').strip()
        logger.info(f"GET /bookings/ for email={email}")
        if not email:
            return Booking.objects.none()
        return Booking.objects.filter(client_email=email)

    def list(self, request, *args, **kwargs):
        email = self.request.query_params.get('email', '').strip()
        if not email:
            logger.warning("GET /bookings/ failed: missing email parameter.")
            return Response({'error': 'Email parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)


# ------------------ POST /signup ------------------
class SignupView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        token = Token.objects.create(user=user)

        logger.info(f"New user signed up: {username}")
        return Response({'message': 'User created successfully', 'token': token.key}, status=status.HTTP_201_CREATED)


# ------------------ POST /login ------------------
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        logger.info(f"User logged in: {username}")
        return Response({'message': 'Login successful', 'token': token.key}, status=status.HTTP_200_OK)
