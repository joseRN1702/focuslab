from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import pytz
import random

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String(20), nullable=False, default='default.png')
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')), onupdate=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
    notes = db.relationship('Note', backref='user', lazy=True)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User id={self.id} name={self.first_name} email={self.email}>'

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')), onupdate=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))

    def __repr__(self):
        return f'<Note id={self.id} user={self.user_id} date={self.date}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')), onupdate=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
    color = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'<Task id={self.id} name={self.name} done={self.done} date={self.date} user={self.user_id}>'
