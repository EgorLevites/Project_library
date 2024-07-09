# Online Library Management System

## Introduction
This project is an online library management system built using Flask for the backend and JavaScript for the frontend. It allows users to register, login, and manage books, including adding new books (admin only), loaning books, and returning books. Admin users have additional capabilities such as managing users, viewing all loaned books, and viewing late loans.

## Features
- User Registration and Login
- Admin and User Roles
- Book Management (Add, Remove, Loan, Return)
- View User Profile
- View All Active Users (Admin only)
- View All Loaned Books (Admin only)
- View Late Loans (Admin only)

## Prerequisites
- Python 3.6+
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- Werkzeug

## Setup and Installation
1. **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate
    ```

3. **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Run the application:**
    ```sh
    python app.py
    ```

5. **Access the application:**
    Open your browser and go to `http://127.0.0.1:5000`.

## File Structure
- `app.py`: Main Flask application file containing all the routes and logic.
- `templates/`: Directory containing HTML templates.
- `static/`: Directory containing static files (CSS, JavaScript, images).
- `media/`: Directory where uploaded book images are stored.

## API Endpoints
### User Authentication
- `POST /register`: Register a new user.
- `POST /login`: Login a user.

### Book Management
- `POST /add_book`: Add a new book (Admin only).
- `POST /loan_book/<int:book_id>`: Loan a book.
- `POST /return_book/<int:loaned_book_id>`: Return a loaned book.
- `POST /remove_book/<int:book_id>`: Remove a book (Admin only).

### User and Loan Management (Admin only)
- `GET /display_all_users`: Display all active users.
- `GET /display_active_loaned_books`: Display all active loaned books.
- `GET /display_late_loans`: Display all late loans.

### User Information
- `GET /user`: Get the current user's information.
- `GET /books`: Get all active books.
- `GET /user_books`: Get all books loaned by the current user.

### Media
- `GET /media/<filename>`: Serve media files (book images).

## Notes
- Admin password for registration is `7732/16`.
- Allowed image file extensions for book uploads: `png`, `jpg`, `jpeg`, `gif`.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
