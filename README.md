******Omnify Booking API******

A Django REST API to manage fitness classes and user bookings, built with secure token-based authentication. Users can view available classes, book classes, and view their own booking history.

****Project Structure****

OMNIFY/
├── db.sqlite3
├── Dockerfile
├── entrypoint.sh
├── manage.py
├── requirements.txt
├── run_commands.txt
├── booking_activity.log
├── fitness_studio/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── studio/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
└── venv_fitness_api/  ← (local Python virtual environment)


**models.py**
Defines the core database models

**serializers.py**
Converts model instances into JSON for API responses and validates incoming data for FitnessClass and Booking.

**views.py**
Contains all API logic

  -Lists available classes (ClassListView)

  -Allows authenticated users to book a class (BookClassView)

  -Shows all bookings made by the logged-in user (UserBookingsView)

  -Includes authentication views (signup_view, login_view)

**utils.py**
Includes helper function token_email_match() to ensure the email in the request matches the authenticated token’s user email. This prevents misuse of tokens for other users.

**urls.py**
Maps all API endpoints like **/api/classes**,** /api/book**, **/api/bookings**,** /api/signup**, **/api/login** to their respective view functions/classes.

**tests.py**
Contains unit tests for:


**settings.py**
Handles Django project settings including REST framework, CORS, Token Authentication, installed apps, and database configuration.

**Dockerfile**
Creates a Docker image for the app, specifying the environment setup and run command.

**db.sqlite3**
The SQLite database file storing user data, classes, and bookings. This is mounted into the Docker container during development.

**User Flow**

**1.User Signup**

  -The user sends their name, email, and password.

  -The server creates a new user and returns an authentication token.

**2.User Login**

  -The user sends their email and password.

  -If valid, the server returns the same authentication token.

**3.View Available Classes**

  -The user makes a GET /api/classes request with their token.

  -Only upcoming classes are returned.

  -The server ensures the email in the request (if provided) matches the token's email.

**4.Book a Class**

  -The user sends a POST /api/book request with the class ID and their name.

  -The server records the booking using the email tied to the token (ignores any external email input).

  -Available slots are reduced by 1.

**5.View My Bookings**

  -The user sends a GET /api/bookings request.

  -The server returns all bookings made using that token’s email.

  -Any email in query parameters is ignored to ensure security.

**Features**

  User Signup & Login with Token Authentication

  View all available fitness classes (date, instructor, slots)

  Book a class (authenticated user only; one’s own email only)

  Prevent booking beyond capacity

  View your own bookings

  Admin panel support for class management

**How to Run This Project with Docker**

  **Step 1: Clone the Repository**

    git clone https://github.com/your-username/omnify-booking-api.git
    cd omnify-booking-api
  
  **Step 2: Build the Docker Image**
  
    docker build -t omnify-app .
  
  **Step 3: Run the Container with DB Volume Binding**
  
    docker run -v $(pwd)/db.sqlite3:/app/db.sqlite3 -p 8000:8000 omnify-app

**🔐 Signup**

POST /api/signup
Registers a new user.

 Request Body:

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "strongpassword123"
}

Success Response:
{
  "message": "Signup successful",
  "token": "ab12cd34ef56..."
}

Error Response:
{
  "error": "Email already exists"
}


**🔐 Login**

POST /api/login
Logs in the user and returns a token.

Request Body:

{
  "email": "john@example.com",
  "password": "strongpassword123"
}


Success Response:

{
  "message": "Login successful",
  "token": "ab12cd34ef56..."
}

Error Response:
{
  "error": "Invalid credentials"
}


**📅 Get All Upcoming Fitness Classes**

Method: GET
URL: /api/classes?email=john@example.com
Returns a list of upcoming fitness classes.

Headers:

Authorization: Token ab12cd34ef56...

Request Params:
email: Must match the authenticated user's email
Example: ?email=john@example.com

Success Response:
[
  {
    "id": 1,
    "name": "Yoga",
    "instructor": "Alice",
    "date_time": "2025-06-25T10:00:00Z",
    "available_slots": 3,
    "total_slots": 5
  },
  ...
]

 Error Response:

 {
  "error": "Email does not match token."
}


**📝 Book a Class**

Method: POST
URL: /api/book
Books a fitness class using the logged-in user's token.

Headers:
Authorization: Token ab12cd34ef56...

Request Body:

{
  "class_id": 1,
  "client_name": "John"
}


Success Response:
{
  "message": "Booking successful."
}

Error Responses:

{
  "error": "Class not found."
}

{
  "error": "No available slots."
}

{
  "error": "Missing required fields."
}


**📋 Get User Bookings**

Method: GET
URL: /api/bookings
Fetches bookings of the currently logged-in user.

Headers:
Authorization: Token ab12cd34ef56...
Success Response:

[
  {
    "id": 1,
    "fitness_class": {
      "name": "Yoga",
      "instructor": "Alice",
      "date_time": "2025-06-25T10:00:00Z"
    },
    "client_name": "John",
    "client_email": "john@example.com"
  },
  ...
]






