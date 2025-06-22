from django.urls import path
from .views import (
    ClassListView,
    BookClassView,
    UserBookingsView,
    signup_view,
    login_view,
    class_list_page,
    user_bookings_page,
    book_form,
)

urlpatterns = [
    # HTML views
    path('', class_list_page, name='class-list-page'),
    

    # API views
    path('api/classes/', ClassListView.as_view(), name='class-list-api'),
    path('api/book/', BookClassView.as_view(), name='book-class-api'),
    path('api/bookings/', UserBookingsView.as_view(), name='user-bookings-api'),
    path('api/signup/', signup_view, name='signup-api'),
    path('api/login/', login_view, name='login-api'),
]
