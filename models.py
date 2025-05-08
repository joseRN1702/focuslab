from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import pytz

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__='Users'

    id=db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String(80), nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(255), nullable=False)
    profile_pic=db.Column(db.String(50), nullable=False)
    created_at=db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
