
# Library Management System

This is a Flask-based web application for managing a library. It includes user registration, login, book management, and loan management functionalities.

## Features

- User registration and login with JWT-based authentication
- Admin and user roles with different access controls
- Add, loan, return, and remove books
- Display active books, users, and loaned books
- Upload and serve book cover images

## Requirements

- Python 3.x
- Flask
- Flask SQLAlchemy
- Flask JWT Extended
- Werkzeug
- Flask CORS

## Setup

1. Clone the repository
2. Install the required packages
3. Run the application

### Clone the repository

```bash
git clone https://github.com/yourusername/library-management-system.git
cd library-management-system
```

### Install the required packages

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000/`.

## API Endpoints

### User Registration

- **URL**: `/register`
- **Method**: `POST`
- **Request**: 
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "age": 25,
    "role": "user"  // Optional, default is "user"
  }
  ```
- **Response**: 
  ```json
  {
    "message": "Registered successfully"
  }
  ```

### User Login

- **URL**: `/login`
- **Method**: `POST`
- **Request**: 
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**: 
  ```json
  {
    "access_token": "your_jwt_token"
  }
  ```

### Add Book (Admin Only)

- **URL**: `/add_book`
- **Method**: `POST`
- **Headers**: 
  ```json
  {
    "Authorization": "Bearer your_jwt_token"
  }
  ```
- **Request**: Form data with fields `data` and `image` (optional)
  - `data`: JSON string with keys `name`, `author`, `year_published`, `type`
  - `image`: Book cover image file (optional)
- **Response**: 
  ```json
  {
    "message": "Book added successfully"
  }
  ```

### Loan Book

- **URL**: `/loan_book/<book_id>`
- **Method**: `POST`
- **Headers**: 
  ```json
  {
    "Authorization": "Bearer your_jwt_token"
  }
  ```
- **Response**: 
  ```json
  {
    "message": "Book loaned successfully",
    "return_date": "2023-01-10"
  }
  ```

### Return Book

- **URL**: `/return_book/<loaned_book_id>`
- **Method**: `POST`
- **Headers**: 
  ```json
  {
    "Authorization": "Bearer your_jwt_token"
  }
  ```
- **Response**: 
  ```json
  {
    "message": "Book returned successfully"
  }
  ```

### Remove Book (Admin Only)

- **URL**: `/remove_book/<book_id>`
- **Method**: `POST`
- **Headers**: 
  ```json
  {
    "Authorization": "Bearer your_jwt_token"
  }
  ```
- **Response**: 
  ```json
  {
    "message": "Book removed successfully"
  }
  ```

### Display Active Books

- **URL**: `/display_active_books`
- **Method**: `GET`
- **Response**: 
  ```json
  [
    {
      "id": 1,
      "name": "Book Title",
      "author": "Author Name",
      "year_published": 2020,
      "type": 1,
      "available": true,
      "active": true
    }
  ]
  ```

### Display All Users (Admin Only)

- **URL**: `/display_all_users`
- **Method**: `GET`
- **Headers**: 
  ```json
  {
    "Authorization": "Bearer your_jwt_token"
  }
  ```
- **Response**: 
  ```json
  [
    {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "age": 25,
      "role": "user",
      "active": true
    }
  ]
  ```

### Display Active Loaned Books (Admin Only)

- **URL**: `/display_active_loaned_books`
- **Method**: `GET`
- **Headers**: 
  ```json
  {
    "Authorization": "Bearer your_jwt_token"
  }
  ```
- **Response**: 
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "user_name": "John Doe",
      "book_id": 1,
      "book_name": "Book Title",
      "author": "Author Name",
      "year_published": 2020,
      "loan_date": "2023-01-01 00:00:00",
      "return_date": "2023-01-10 00:00:00",
      "active": true
    }
  ]
  ```

### Display Late Loans (Admin Only)

- **URL**: `/display_late_loans`
- **Method**: `GET`
- **Headers**: 
  ```json
  {
    "Authorization": "Bearer your_jwt_token"
  }
  ```
- **Response**: 
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "user_name": "John Doe",
      "book_id": 1,
      "book_name": "Book Title",
      "author": "Author Name",
      "year_published": 2020,
      "loan_date": "2023-01-01 00:00:00",
      "return_date": "2023-01-10 00:00:00",
      "active": true
    }
  ]
  ```

### Get Current User Info

- **URL**: `/user`
- **Method**: `GET`
- **Headers**: 
  ```json
  {
    "Authorization": "Bearer your_jwt_token"
  }
  ```
- **Response**: 
  ```json
  {
    "email": "user@example.com",
    "role": "user",
    "full_name": "John Doe",
    "age": 25
  }
  ```

### Get All Active Books

- **URL**: `/books`
- **Method**: `GET`
- **Response**: 
  ```json
  [
    {
      "id": 1,
      "name": "Book Title",
      "author": "Author Name",
      "year_published": 2020,
      "filename": "book_cover.jpg",
      "available": true
    }
  ]
  ```

### Get User's Loaned Books

- **URL**: `/user_books`
- **Method**: `GET`
- **Headers**: 
  ```json
  {
    "Authorization": "Bearer your_jwt_token"
  }
  ```
- **Response**: 
  ```json
  [
    {
      "id": 1,
      "name": "Book Title",
      "author": "Author Name",
      "year_published": 2020,
      "filename": "book_cover.jpg",
      "available": true,
      "loaned_by_user": true
    }
  ]
  ```

### Serve Images

- **URL**: `/media/<filename>`
- **Method**: `GET`
- **Response**: Serves the requested image file

## License

This project is licensed under the MIT License. See the LICENSE file for details.
