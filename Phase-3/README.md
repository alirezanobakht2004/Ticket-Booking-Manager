# Ticket Booking Manager - README.md

---

## Overview

This project implements a backend server for a ticket booking system with user authentication, ticket search, reservation management, and city information. The APIs support user registration, login via OTP, profile updates, ticket search and details, and ticket reservation with expiration handling.

---

## Setup and Run the Kannada Server

1. **Prerequisites:**

   - Python 3.8+
   - Redis server installed and running
   - MySQL or compatible database configured
   - Required Python packages installed (`pip install -r requirements.txt`)

2. **Configure environment:**

   - Edit `config.py` to set database connection parameters.
   - Configure Redis connection details (host, port, password if any).

3. **Run the server:**

   ```bash
   python app.py
   ```

   The server will run on `http://127.0.0.1:5000` by default with debug mode enabled.

---

## Redis Database Connection and Configuration

- Redis is used for caching search results and session-related data.
- Ensure Redis server is running locally or remotely.
- Connection parameters are set in the configuration file (e.g., `config.py`):

  ```python
  REDIS_HOST = 'localhost'
  REDIS_PORT = 6379
  REDIS_DB = 0
  REDIS_PASSWORD = None  # if applicable
  ```

- The application connects to Redis using these parameters via a Redis client.

---

## API List with Descriptions

### 1. Authentication APIs

#### Request OTP

- **Method:** POST  
- **URL:** `/api/auth/login/request-otp`  
- **Headers:** `Content-Type: application/json`  
- **Body:**

  ```json
  {
    "email": "user1@example.com"
  }
  ```

- **Response:** Sends OTP to the user’s email or phone.

#### Verify OTP

- **Method:** POST  
- **URL:** `/api/auth/login/verify-otp`  
- **Headers:** `Content-Type: application/json`  
- **Body:**

  ```json
  {
    "email": "user1@example.com",
    "otp": "278895"
  }
  ```

- **Response:** Returns JWT token on successful verification.

#### User Signup

- **Method:** POST  
- **URL:** `/api/auth/signup`  
- **Headers:** `Content-Type: application/json`  
- **Body:**

  ```json
  {
    "first_name": "Ali",
    "last_name": "Rezaei",
    "email": "ali.rezaei@example.com",
    "phone_number": "09123456789",
    "city": "Tehran",
    "password": "SuperSecret123"
  }
  ```

- **Response:** Confirmation of user registration.

#### Update Profile

- **Method:** POST  
- **URL:** `/api/auth/profile/update`  
- **Headers:**  
  - `Content-Type: application/json`  
  - `Authorization: Bearer `  
- **Body:**

  ```json
  {
    "first_name": "Asoi",
    "last_name": "Rei",
    "email": "kkkkali.reza@example.com",
    "phone_number": "0913456789",
    "city": "Tehran"
  }
  ```

- **Response:** Success or error message.

---

### 2. City API

#### Get Cities

- **Method:** GET  
- **URL:** `/api/cities`  
- **Headers:** `Content-Type: application/json`  
- **Response:** List of available cities.

---

### 3. Ticket APIs

#### Search Tickets

- **Method:** GET  
- **URL:** `/api/tickets/search`  
- **Headers:** `Content-Type: application/json`  
- **Query Parameters (example):**

  ```
  origin_id=28&destination_id=45&travel_date=2025-05-10
  ```

  or with filters:

  ```
  origin_id=1&destination_id=2&travel_date=2025-06-15&vehicle_type=plane&min_price=100&max_price=500&company_name=Air&departure_start=08:00&departure_end=20:00&travel_class=1
  ```

- **Response:** List of matching tickets.

#### Ticket Details

- **Method:** GET  
- **URL:** `/api/tickets/details/`  
- **Headers:** `Content-Type: application/json`  
- **Response:** Detailed information of the specified ticket.

---

### 4. Reservation APIs

#### Reserve Ticket

- **Method:** POST  
- **URL:** `/api/reservations/reserve`  
- **Headers:**  
  - `Content-Type: application/json`  
  - `Authorization: Bearer `  
- **Body:**

  ```json
  {
    "ticket_id": 123,
    "quantity": 2,
    "reservation_time": 10  // optional, duration in minutes
  }
  ```

- **Response:** Reservation confirmation with reservation ID.

#### Get Active Reservations

- **Method:** GET  
- **URL:** `/api/reservations/active`  
- **Headers:** `Authorization: Bearer `  
- **Response:** List of currently active reservations.

#### Get Reservation History

- **Method:** GET  
- **URL:** `/api/reservations/history`  
- **Headers:** `Authorization: Bearer `  
- **Response:** List of all past reservations.

---

## How to Test APIs

### Using Postman

1. Import or create requests for each API endpoint.
2. Set the required headers (`Content-Type` and `Authorization` where needed).
3. Provide request body or query parameters as specified.
4. Send requests and verify responses.
5. Use environment variables to store JWT tokens for authenticated requests.

### Using Curl

Example to request OTP:

```bash
curl -X POST http://localhost:5000/api/auth/login/request-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "user1@example.com"}'
```

Example to reserve a ticket:

```bash
curl -X POST http://localhost:5000/api/reservations/reserve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer " \
  -d '{"ticket_id": 123, "quantity": 2, "reservation_time": 10}'
```

---

## Notes

- All authenticated endpoints require a valid JWT token in the `Authorization` header.
- Reservation validity is time-limited (default 10 minutes) and reservations expire automatically.
- Use the ticket search API to find tickets before reserving.
- Ensure Redis and database servers are running and configured correctly before starting the app.

---

