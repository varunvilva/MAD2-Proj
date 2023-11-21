# auth.py
from flask_security import SQLAlchemyUserDatastore
from api_application.models import db, User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
