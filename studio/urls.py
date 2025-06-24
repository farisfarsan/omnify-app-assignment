from django.urls import path
from .views import (
    ClassListView,
    BookClassView,
    UserBookingsView,
    signup_view,
    login_view
)

urlpatterns = [
    path('api/classes', ClassListView.as_view(), name='class-list'),
    path('api/book', BookClassView.as_view(), name='book-class'),
    path('api/bookings', UserBookingsView.as_view(), name='user-bookings'),
    path('api/signup', signup_view, name='signup'),
    path('api/login', login_view, name='login'),
]
