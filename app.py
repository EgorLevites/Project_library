import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.utils import secure_filename

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key_here'

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'media')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the database and JWT manager
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')
    active = db.Column(db.Boolean, nullable=False, default=True)
    loaned_books = db.relationship('LoanedBooks', backref='user', lazy=True)

# Books model
class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)  # Should be 1 or 2
    available = db.Column(db.Boolean, nullable=False, default=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    filename = db.Column(db.String(200), nullable=True)
    loaned_books = db.relationship('LoanedBooks', backref='book', lazy=True)

# LoanedBooks model
class LoanedBooks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Decorator to require admin access
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        if not user or user.role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    age = data.get('age')
    role = data.get('role', 'user')
    admin_password = data.get('admin_password')

    # Check if the email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400

    # Verify admin password if role is admin
    if role == 'admin' and admin_password != '7732/16':
        return jsonify({'message': 'Invalid admin password'}), 403

    password_hash = generate_password_hash(password)
    new_user = User(email=email, password_hash=password_hash, full_name=full_name, age=age, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registered successfully'}), 201

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    # Verify user credentials
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=email)
    return jsonify({'access_token': access_token}), 200

# Route to add a book (admin only)
@app.route('/add_book', methods=['POST'])
@jwt_required()
@admin_required
def add_book():
    data = request.form.get('data')
    
    if not data:
        return jsonify({"message": "Invalid data"}), 400

    try:
        data = json.loads(data)
    except ValueError:
        return jsonify({"message": "Invalid JSON"}), 400

    # Check for required fields
    if 'name' not in data or 'author' not in data or 'year_published' not in data or 'type' not in data:
        return jsonify({"message": "Missing data"}), 400

    name = data.get('name')
    author = data.get('author')
    year_published = data.get('year_published')
    type = data.get('type')

    # Check if the book already exists and is active
    existing_book = Books.query.filter_by(name=name, author=author, year_published=year_published).first()
    if existing_book:
        if existing_book.active:
            return jsonify({'message': 'Book already exists'}), 400
        else:
            # If the book exists but is inactive, set it to active
            existing_book.active = True
            db.session.commit()
            return jsonify({'message': 'Book reactivated successfully'}), 200

    # Handle image upload
    image = request.files.get('image')
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = 'default.jpeg'

    # Add a new book entry
    new_book = Books(
        name=name,
        author=author,
        year_published=year_published,
        type=type,
        filename=filename
    )
    db.session.add(new_book)
    db.session.commit()

    return jsonify({'message': 'Book added successfully'}), 201

# Route to loan a book
@app.route('/loan_book/<int:book_id>', methods=['POST'])
@jwt_required()
def loan_book(book_id):
    current_user = get_jwt_identity()
    book = Books.query.get(book_id)
    user = User.query.filter_by(email=current_user).first()

    if not book:
        return jsonify({'message': 'Book not found'}), 404

    if not book.available:
        return jsonify({'message': 'Book is not available'}), 400

    if not book.active:
        return jsonify({'message': 'Book is not active'}), 400

    loan_date = datetime.utcnow()
    return_date = loan_date + timedelta(days=10) if book.type == 1 else loan_date + timedelta(days=30)
    
    loaned_book = LoanedBooks(user_id=user.id, book_id=book.id, loan_date=loan_date, return_date=return_date)
    db.session.add(loaned_book)
    db.session.commit()

    # Update book availability
    book.available = False
    db.session.commit()

    return jsonify({'message': 'Book loaned successfully', 'return_date': return_date.strftime('%Y-%m-%d')}), 201

# Route to return a book
@app.route('/return_book/<int:loaned_book_id>', methods=['POST'])
@jwt_required()
def return_book(loaned_book_id):
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    loaned_book = LoanedBooks.query.filter_by(book_id=loaned_book_id, active=True).first()
    
    if not loaned_book:
        return jsonify({'message': 'Active loaned book entry not found'}), 404

    if loaned_book.user_id != user.id:
        return jsonify({'message': 'You did not loan this book'}), 403

    book = Books.query.get(loaned_book.book_id)
    
    if not book:
        return jsonify({'message': 'Book not found'}), 404

    book.available = True
    loaned_book.active = False
    db.session.commit()

    return jsonify({'message': 'Book returned successfully'}), 200

# Route to remove a book (admin only)
@app.route('/remove_book/<int:book_id>', methods=['POST'])
@jwt_required()
@admin_required
def remove_book(book_id):
    book = Books.query.get(book_id)
    
    if not book:
        return jsonify({'message': 'Book not found'}), 404
    
    if not book.available:
        return jsonify({'message': 'This book is loaned!'}), 400

    book.active = False
    db.session.commit()

    return jsonify({'message': 'Book removed successfully'}), 200

# Route to display active books
@app.route('/display_active_books', methods=['GET'])
def display_active_books():
    books = Books.query.filter_by(active=True).all()
    
    if not books:
        return jsonify({'message': 'No active books found'}), 404

    books_list = []
    for book in books:
        books_list.append({
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'type': book.type,
            'available': book.available,
            'active': book.active
        })

    return jsonify(books_list), 200

# Route to display all active users (admin only)
@app.route('/display_all_users', methods=['GET'])
@jwt_required()
@admin_required
def display_all_users():
    users = User.query.filter_by(active=True).all()
    
    if not users:
        return jsonify({'message': 'No active users found'}), 404

    users_list = []
    for user in users:
        users_list.append({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'age': user.age,
            'role': user.role,
            'active': user.active
        })

    return jsonify(users_list), 200

# Route to display all active loaned books (admin only)
@app.route('/display_active_loaned_books', methods=['GET'])
@jwt_required()
@admin_required
def display_active_loaned_books():
    loaned_books = LoanedBooks.query.filter_by(active=True).all()
    
    if not loaned_books:
        return jsonify({'message': 'No active loaned books found'}), 404

    loaned_books_list = []
    for loaned_book in loaned_books:
        book = Books.query.get(loaned_book.book_id)
        user = User.query.get(loaned_book.user_id)

        loaned_books_list.append({
            'id': loaned_book.id,
            'user_id': loaned_book.user_id,
            'user_name': user.full_name,
            'book_id': loaned_book.book_id,
            'book_name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'loan_date': loaned_book.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
            'return_date': loaned_book.return_date.strftime('%Y-%m-%d %H:%M:%S'),
            'active': loaned_book.active
        })

    return jsonify(loaned_books_list), 200

# Route to display all late loans (admin only)
@app.route('/display_late_loans', methods=['GET'])
@jwt_required()
@admin_required
def display_late_loans():
    current_time = datetime.utcnow()
    late_loans = LoanedBooks.query.filter(LoanedBooks.return_date < current_time, LoanedBooks.active == True).all()
    
    if not late_loans:
        return jsonify({'message': 'No late loans found'}), 404

    late_loans_list = []
    for loaned_book in late_loans:
        book = Books.query.get(loaned_book.book_id)
        user = User.query.get(loaned_book.user_id)

        late_loans_list.append({
            'id': loaned_book.id,
            'user_id': loaned_book.user_id,
            'user_name': user.full_name,
            'book_id': loaned_book.book_id,
            'book_name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'loan_date': loaned_book.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
            'return_date': loaned_book.return_date.strftime('%Y-%m-%d %H:%M:%S'),
            'active': loaned_book.active
        })

    return jsonify(late_loans_list), 200

# Route to get the current user's information
@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'email': user.email,
        'role': user.role,
        'full_name': user.full_name,
        'age': user.age
    }), 200

# Route to get all active books
@app.route('/books', methods=['GET'])
def get_books():
    books = Books.query.filter_by(active=True).all()
    books_list = []
    for book in books:
        books_list.append({
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'filename': book.filename,
            'available': book.available
        })
    return jsonify(books_list), 200

# Route to get all books loaned by the current user
@app.route('/user_books', methods=['GET'])
@jwt_required()
def get_user_books():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    books = Books.query.filter_by(active=True).all()
    books_list = []
    for book in books:
        loaned_book = LoanedBooks.query.filter_by(user_id=user.id, book_id=book.id, active=True).first()
        books_list.append({
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'filename': book.filename,
            'available': book.available,
            'loaned_by_user': loaned_book is not None
        })
    return jsonify(books_list), 200

# Route to serve images
@app.route('/media/<filename>')
def media(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
