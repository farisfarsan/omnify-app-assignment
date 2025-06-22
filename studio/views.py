from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.timezone import now, localtime
from django.shortcuts import render, redirect
from django.contrib import messages
import logging
import json

from .models import FitnessClass, Booking
from .serializers import FitnessClassSerializer, BookingSerializer

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
        # pass request so serializer can access query params
        return {"request": self.request}

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        logger.info(f"GET /classes/ response: {response.data}")
        return response
# ------------------ API: Book Class ------------------
class BookClassView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated] 
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

# ------------------ API: View User Bookings ------------------
class UserBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated] 
    
    def get_queryset(self):
        email = self.request.query_params.get('email', '').strip()
        timezone = self.request.query_params.get('timezone', '').strip()
        logger.info(f"GET /bookings/ for email={email} /for timezone={timezone}")
        if not email:
            return Booking.objects.none()
        return Booking.objects.filter(client_email=email)
    
    def get_serializer_context(self):
        # pass request so serializer can access query params
        return {"request": self.request}

    def list(self, request, *args, **kwargs):
        email = self.request.query_params.get('email', '').strip()
        if not email:
            logger.warning("GET /bookings/ failed: missing email parameter.")
            return Response({'error': 'Email parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)

# ------------------ API: Signup ------------------
@csrf_exempt
@api_view(['POST'])
def signup_view(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, password=password)
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
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'message': 'Login successful', 'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

# ------------------ HTML View: Class List ------------------
def class_list_page(request):
    classes = FitnessClass.objects.all().order_by('date_time')
    return render(request, 'class_list_page.html', {'classes': classes})

# ------------------ HTML View: User Bookings ------------------
def user_bookings_page(request):
    email = request.GET.get('email', '').strip()
    bookings = Booking.objects.filter(client_email=email) if email else []

    # Convert datetime to localtime for display
    for booking in bookings:
        booking.fitness_class.date_time = localtime(booking.fitness_class.date_time)

    return render(request, 'user_bookings_page.html', {'bookings': bookings})

# ------------------ HTML View: Book Form ------------------
def book_form(request):
    classes = FitnessClass.objects.filter(date_time__gte=now()).order_by('date_time')

    if request.method == "POST":
        class_id = request.POST.get("class_id")
        client_name = request.POST.get("client_name")
        client_email = request.POST.get("client_email")

        try:
            fitness_class = FitnessClass.objects.get(id=class_id)
            if fitness_class.available_slots <= 0:
                messages.error(request, "No available slots for this class.")
            else:
                Booking.objects.create(
                    fitness_class=fitness_class,
                    client_name=client_name,
                    client_email=client_email
                )
                fitness_class.available_slots -= 1
                fitness_class.save()
                messages.success(request, "Booking successful!")
                return redirect('book-form')
        except FitnessClass.DoesNotExist:
            messages.error(request, "Selected class does not exist.")

    return render(request, "book_form.html", {"classes": classes})
