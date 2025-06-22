from django.urls import path
from django.views.generic import TemplateView
from . import views  # ✅ Import views to use views.book_form

from .views import (
    ClassListView,
    BookClassView,
    UserBookingsView,
    signup_view,
    login_view,
    class_list_page,
    user_bookings_page,
    book_form  # ✅ Explicit import (optional, since already imported above)
)

urlpatterns = [
    # Static pages
    path('', TemplateView.as_view(template_name="home.html"), name="home"),
    path('dashboard/', TemplateView.as_view(template_name="dashboard.html"), name="dashboard"),

    # API endpoints
    path('api/classes/', ClassListView.as_view(), name='class-list-api'),
    path('api/book/', BookClassView.as_view(), name='book-class-api'),
    path('api/bookings/', UserBookingsView.as_view(), name='user-bookings-api'),

    # User-facing HTML views
    path('classes/', class_list_page, name='class-list-page'),
    path('book-form/', views.book_form, name='book-form'),  # ✅ Only keep this one for dynamic form
    path('bookings/', user_bookings_page, name='user-bookings-page'),

    # Auth views
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
]
