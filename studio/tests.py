from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from .models import FitnessClass, Booking


class BookingAPITestCase(TestCase):
    def setUp(self):
        # ──  user and auth-token ──────────────────────────────────────────
        self.user = User.objects.create_user(
            username="faris@example.com",
            email="faris@example.com",
            password="secret123",
            first_name="Faris"
        )
        self.token = Token.objects.create(user=self.user)
        self.auth = {"HTTP_AUTHORIZATION": f"Token {self.token.key}"}

        # ── test fitness class ──────────────────────────────────────────
        self.fitness_class = FitnessClass.objects.create(
            name="Test Yoga",
            date_time=make_aware(datetime(2025, 6, 25, 10, 0)),
            instructor="Test Instructor",
            total_slots=5,
            available_slots=5
        )

    # ─────────────────────────────────────────────────────────────────────────────
    # 1) GET /api/classes  
    # ─────────────────────────────────────────────────────────────────────────────
    def test_get_classes_success(self):
        url = "/api/classes?email=faris@example.com"
        response = self.client.get(url, **self.auth)
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.json()[0])

    def test_get_classes_email_mismatch(self):
        url = "/api/classes?email=someoneelse@example.com"
        response = self.client.get(url, **self.auth)
        self.assertEqual(response.status_code, 403)
        self.assertIn("Email does not match token", response.json()["error"])

    # ─────────────────────────────────────────────────────────────────────────────
    # 2) POST /api/book  
    # ─────────────────────────────────────────────────────────────────────────────
    def test_successful_booking(self):
        url = "/api/book"
        payload = {
            "class_id": self.fitness_class.id,
            "client_name": "Faris"
        }
        response = self.client.post(url, payload, content_type="application/json", **self.auth)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(Booking.objects.first().client_email, "faris@example.com")

    def test_booking_missing_fields(self):
        url = "/api/book"
        payload = {
            "class_id": self.fitness_class.id        
        }
        response = self.client.post(url, payload, content_type="application/json", **self.auth)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_overbooking(self):
        self.fitness_class.available_slots = 0
        self.fitness_class.save()

        url = "/api/book"
        payload = {
            "class_id": self.fitness_class.id,
            "client_name": "Faris"
        }
        response = self.client.post(url, payload, content_type="application/json", **self.auth)
        self.assertEqual(response.status_code, 400)
        self.assertIn("No available slots", response.json()["error"])

    # ─────────────────────────────────────────────────────────────────────────────
    # 3) GET /api/bookings
    # ─────────────────────────────────────────────────────────────────────────────
    def test_get_own_bookings(self):
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="Faris",
            client_email="faris@example.com"
        )
        response = self.client.get("/api/bookings", **self.auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_bookings_with_email_param_blocked(self):
        response = self.client.get("/api/bookings?email=faris@example.com", **self.auth)
        self.assertEqual(response.status_code, 403)
        self.assertIn("email", response.json()["error"])
