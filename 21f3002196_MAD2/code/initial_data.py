from main import app 
from applications.sec import datastore
from applications.models import db,Role,User
from flask_security import hash_password
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    datastore.find_or_create_role(name="admin" , description="User is an Admin")
    datastore.find_or_create_role(name="librarian" , description="User is a Librarian")
    datastore.find_or_create_role(name="user" , description="User is a User")
    db.session.commit()
    if not datastore.find_user(email="admin@email.com"):
        datastore.create_user(email="admin@email.com" , password=generate_password_hash("admin") , roles=["admin"])
    if not datastore.find_user(email="librarian@email.com"):
        datastore.create_user(email="librarian@email.com" , password=generate_password_hash("librarian") , roles=["librarian"] , active=False)
    if not datastore.find_user(email="user@email.com"):
        datastore.create_user(email="user@email.com" , password=generate_password_hash("user") , roles=["user"])

    db.session.commit()    
     
