from flask_security import SQLAlchemyUserDatastore 
from applications.models import db , User, Role, Book 


datastore=SQLAlchemyUserDatastore(db,User,Role)

