from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev.db"
db.init_app(app)

class RolesUsers(db.Model):
    __tablename__='roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))

class User(db.Model , UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80), unique=False)
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), nullable=False)
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)
    roles=db.relationship('Role' , secondary='roles_users' , backref=db.backref('users' , lazy=True))

class Role(db.Model , RoleMixin):
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True )
    name = db.Column(db.String(255) , nullable=False)
    date_created=db.Column(db.Date , nullable=True)
    description = db.Column(db.String(255) , nullable=False)
    books=db.relationship('Book' , backref=db.backref('section' , lazy=True))

    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255) , nullable=False)
    content = db.Column(db.String(255) , nullable=False)
    author = db.Column(db.String(255) , nullable=False)
    quantity = db.Column(db.Integer , nullable=False , default=1)
    date_issue=db.Column(db.Date , nullable=True)
    return_date=db.Column(db.Date , nullable=True)
    section_id = db.Column(db.Integer , db.ForeignKey('section.id') , nullable=False)


class BookIssuance(db.Model):
    __tablename__ = 'book_issuance'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    issued_at = db.Column(db.DateTime, nullable=True)
    returned_at = db.Column(db.DateTime, default=None)
    user = db.relationship('User', backref=db.backref('books_issued', lazy=True))
    book = db.relationship('Book', backref=db.backref('users_issued_to', lazy=True))
    def __repr__(self):
        return f"<BookIssuance {self.id}>"


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    rating=db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('feedbacks_given', lazy=True))
    book = db.relationship('Book', backref=db.backref('feedbacks', lazy=True))

    def __repr__(self):
        return f"<Feedback {self.id}>"
    
with app.app_context():
    db.create_all()