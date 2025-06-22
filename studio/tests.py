from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from datetime import datetime
from .models import FitnessClass, Booking

class BookingAPITestCase(TestCase):
    def setUp(self):
        self.fitness_class = FitnessClass.objects.create(
            name="Test Yoga",
            date_time=make_aware(datetime(2025, 6, 25, 10, 0)),
            instructor="Test Instructor",
            total_slots=5,
            available_slots=5
        )

    def test_get_classes(self):
        response = self.client.get('/classes/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.json()[0])

    def test_successful_booking(self):
        response = self.client.post('/book/', {
            "class_id": self.fitness_class.id,
            "client_name": "Test User",
            "client_email": "testuser@example.com"
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Booking.objects.count(), 1)

    def test_booking_missing_fields(self):
        response = self.client.post('/book/', {
            "class_id": self.fitness_class.id,
            "client_name": "Test User"
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_overbooking(self):
        self.fitness_class.available_slots = 0
        self.fitness_class.save()
        response = self.client.post('/book/', {
            "class_id": self.fitness_class.id,
            "client_name": "Test User",
            "client_email": "testuser@example.com"
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('No available slots', response.json()['error'])

    def test_get_bookings_by_email(self):
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="Test User",
            client_email="testuser@example.com"
        )
        response = self.client.get('/bookings/?email=testuser@example.com')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
