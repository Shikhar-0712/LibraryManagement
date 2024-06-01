from datetime import datetime
from flask import current_app as app , jsonify , request, render_template, send_file
from celery.result import AsyncResult
from flask_security import auth_required, roles_required, current_user, login_user,logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_restful import marshal,fields
from .models import User, Book, BookIssuance, Feedback, db
from applications.sec import datastore
from .sec import datastore
import uuid
from sqlalchemy import or_
from datetime import timedelta


def revoke_access_book():
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    issued_books = db.session.query(BookIssuance.id, BookIssuance.book_id).filter(
        BookIssuance.issued_at <= seven_days_ago
    ).all()
    for issue_id, book_id in issued_books:
        book = Book.query.get_or_404(book_id)
        issuance = BookIssuance.query.filter_by(id=issue_id).first()
        if issuance:
            db.session.delete(issuance)
            db.session.commit()
            book.quantity += 1
            db.session.commit()
    return "OK" 

@app.get('/')
def home(): 
    revoke_access_book()
    return render_template('index.html')

@app.get('/admin')
@auth_required('token')
@roles_required('admin')
def admin(): 
    return " welcome admin"

@app.get('/activate/librarian/<int:librarian_id>')
@auth_required('token')
@roles_required('admin')
def activate_librarian(librarian_id): 
    librarian=User.query.get(librarian_id)
    if not librarian or "librarian" not in librarian.roles:
        return jsonify({"message":"librarian not found"}), 404
    librarian.active=True
    db.session.commit()
    return jsonify({"message":"librarian activated"})


@app.post('/register')
def register_user():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    
    if not email or not username or not password:
        return jsonify({"message": "Email, username, and password are required."}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists."}), 400
    
    hashed_password = generate_password_hash(password)  
    datastore.create_user(email=email, username=username, password=hashed_password, roles=["user"], active=True)
    db.session.commit()

    return jsonify({"message": "User created successfully."}), 201

@app.post('/user-login')
def user_login():
    data=request.get_json()
    email=data.get('email')
    if not email:
        return jsonify({"message":"email is required"}), 400
    
    user=datastore.find_user(email=email)

    if not user:
        return jsonify({"message":"user not found"}), 404
   
    if check_password_hash(user.password, data.get('password')):
        login_user(user)
        db.session.commit()
        if user.id == 1: 
            role = "admin"
        elif user.id == 2: 
            role = "librarian" 
        else:
            role = "user"  
        
        return jsonify({"token": user.get_auth_token(), "email": user.email, "roles": role})
    
    else:
        return jsonify({"message":"wrong password"}), 400


user_fields = {
    "id":fields.Integer,
    "email":fields.String,
    "active":fields.Boolean  
}      


@app.get('/users')
@auth_required("token")
@roles_required("admin")
def all_users():
    users = User.query.all()
    if len(users) == 0:
        return jsonify({"message": "No User Found"}), 404
    return marshal(users, user_fields)


@app.post('/issue-book/<int:book_id>')
@auth_required("token")  
def issue_book(book_id):
    if not current_user.is_authenticated:
        return jsonify({"message": "User is not authenticated."}), 401

    user_id = current_user.id
    user = User.query.get_or_404(user_id)
    book = Book.query.get_or_404(book_id)

    issued_books_count = BookIssuance.query.filter_by(user_id=user_id, returned_at=None).count()

    if issued_books_count >= 5:
        return jsonify({"message": "You have already issued the maximum number of books (5)."}), 400

    if book.quantity <= 0:
        return jsonify({"message": "Requested book is not available for issuance."}), 400

    book.quantity -= 1
    issuance = BookIssuance(user_id=user.id, book_id=book.id)
    db.session.add(issuance)
    db.session.commit()

    return jsonify({"message": "Book issued successfully."}), 200

@app.get('/librarian/books-issued')
@auth_required("token")
@roles_required("librarian")
def get_books_issued_by_librarian():
    if not current_user.is_authenticated:
        return jsonify({"message": "User is not authenticated."}), 401

    # user_id = current_user.id
    # user = User.query.get_or_404(user_id)

    books_issued = db.session.query(BookIssuance, Book, User) \
        .join(Book) \
        .join(User, User.id == BookIssuance.user_id) \
        .filter(or_(BookIssuance.returned_at == None, BookIssuance.returned_at > datetime.now())) \
        .all()

    books_data = []
    for issuance, book, user in books_issued:
        book_data = {
            "id": issuance.id,
            "bookId": book.id,
            "name": book.name,
            "content": book.content,
            "author": book.author,
            "quantity": book.quantity,
            "date_issue": issuance.issued_at.strftime("%Y-%m-%d") if issuance.issued_at else None,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }
        books_data.append(book_data)

    return jsonify(books_data), 200


@app.post('/user/book-return/<int:book_id>')
@auth_required("token")
def return_book(book_id):
    if not current_user.is_authenticated:
        return jsonify({"message": "User is not authenticated."}), 401

    user_id = current_user.id
    user = User.query.get_or_404(user_id)
    book = Book.query.get_or_404(book_id)

    issuance = BookIssuance.query.filter_by(user_id=user_id, book_id=book_id, returned_at=None).first()
    if issuance:
        issuance.returned_at = datetime.now()  
        db.session.commit()
        book.quantity += 1
        db.session.commit()
        return jsonify({"message": "Book returned successfully."}), 200
    else:
        return jsonify({"message": "Book not found or already returned."}), 404

@app.get('/librarian/revoke-access-book/<int:issued_book_id>/<int:book_id>')
@auth_required("token")
@roles_required("librarian")
def revoke_access(issued_book_id,book_id):
    if not current_user.is_authenticated:
        return jsonify({"message": "User is not authenticated."}), 401

    user_id = current_user.id
    book = Book.query.get_or_404(book_id)

    issuance = BookIssuance.query.filter_by(id=issued_book_id).first()
    if issuance:
        db.session.delete(issuance)
        db.session.commit()

        book.quantity += 1
        db.session.commit()
        return jsonify({"message": "Revoked Accessed Successfully"}), 200
    else:
        return jsonify({"message": "Book not found or already returned."}), 404



@app.get('/user/books-issued')
@auth_required("token")
def get_books_issued_by_user():
    if not current_user.is_authenticated:
        return jsonify({"message": "User is not authenticated."}), 401

    user_id = current_user.id
    user = User.query.get_or_404(user_id)

    books_issued = db.session.query(BookIssuance, Book) \
        .join(Book) \
        .filter(BookIssuance.user_id == user.id) \
        .filter(or_(BookIssuance.returned_at == None, BookIssuance.returned_at > datetime.now()), BookIssuance.issued_at != None) \
        .all()

    books_data = []
    for issuance, book in books_issued:
        book_data = {
            "id": book.id,
            "name": book.name,
            "content": book.content,
            "author": book.author,
            "quantity": book.quantity,
            "date_issue": issuance.issued_at.strftime("%Y-%m-%d") if issuance.issued_at else None,
        }
        books_data.append(book_data)

    return jsonify(books_data), 200

@app.get('/librarian/books-issued/<int:issuance_id>/accept')
@auth_required("token")
@roles_required("librarian")
def accept_book_issuance(issuance_id):
    if not current_user.is_authenticated:
        return jsonify({"message": "User is not authenticated."}), 401

    issuance = BookIssuance.query.get_or_404(issuance_id)
    
    if issuance.issued_at is not None:
        return jsonify({"message": "Book issuance already accepted."}), 400

    issuance.issued_at = datetime.now()
    db.session.commit()

    return jsonify({"message": "Book issuance accepted successfully."}), 200        
    
@app.route('/api/feedback', methods=['POST'])
@auth_required("token")
def submit_feedback():
    data = request.json
    book_id = data.get('book_id')
    text = data.get('text')
    rating = data.get('rating')

    if not current_user.is_authenticated:
        return jsonify({"message": "User is not authenticated."}), 401

    user_id = current_user.id

    if not all([user_id, book_id, text]):
        return jsonify({'error': 'Missing data in request'}), 400

    feedback = Feedback(user_id=user_id, book_id=book_id, text=text,rating=rating)
    db.session.add(feedback)
    db.session.commit()

    return jsonify({'message': 'Feedback submitted successfully'}), 200

@app.get('/librarian/feedbacks')
@auth_required("token")
@roles_required("librarian")
def get_all_feedbacks():
    if not current_user.is_authenticated:
        return jsonify({"message": "User is not authenticated."}), 401

    feedbacks = db.session.query(Feedback, Book, User) \
        .join(Book) \
        .join(User) \
        .all()

    feedbacks_data = []
    for feedback, book, user in feedbacks:
        feedback_data = {
            "id": feedback.id,
            "book_id": book.id,
            "book_name": book.name,
            "user_id": user.id,
            "user_name": user.username,
            "text": feedback.text,
            "rating":feedback.rating,
            "created_at": feedback.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        feedbacks_data.append(feedback_data)

    return jsonify(feedbacks_data), 200

