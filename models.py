from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import pytz
# import random # Não é usado diretamente neste arquivo de modelos

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# DEFINIÇÃO CORRETA E ÚNICA DE group_members NO TOPO
group_members = db.Table('group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True), # group.id será definido abaixo
    db.Column('joined_at', db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String(20), nullable=False, default='default.png')
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')), onupdate=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
    
    # Relacionamentos existentes
    notes = db.relationship('Note', backref='user', lazy=True)
    tasks = db.relationship('Task', backref='user', lazy=True)
    
    # owned_groups e member_of_groups serão adicionados via backref da classe Group

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User id={self.id} name={self.first_name} email={self.email}>'
    
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')), onupdate=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))

    owner = db.relationship('User', backref=db.backref('owned_groups', lazy='dynamic'), foreign_keys=[owner_id])

    # Agora 'group_members' está definido e pode ser referenciado corretamente
    members = db.relationship('User', secondary=group_members, lazy='dynamic',
                              backref=db.backref('member_of_groups', lazy='dynamic'))

    def __repr__(self):
        return f'<Group id={self.id} name={self.name} owner_id={self.owner_id}>'

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')), onupdate=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
    # O backref 'user' em User.notes já cria a referência user.notes e note.user

    def __repr__(self):
        return f'<Note id={self.id} user_id={self.user_id} date={self.date}>' # Alterado para user_id para consistência

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')), onupdate=lambda: datetime.datetime.now(pytz.timezone('America/Sao_Paulo')))
    color = db.Column(db.String(20), nullable=True)
    # O backref 'user' em User.tasks já cria a referência user.tasks e task.user

    def __repr__(self):
        return f'<Task id={self.id} name={self.name} done={self.done} date={self.date} user_id={self.user_id}>' # Alterado para user_id

# A DEFINIÇÃO DUPLICADA DE group_members QUE ESTAVA AQUI FOI REMOVIDA.
