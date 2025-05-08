import os
from flask import Flask, render_template, redirect, request, url_for, flash, session
from models import User, db
from functools import wraps
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///dados.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
app.config['SECRET_KEY'] = 'GUILHERMECASTRO'
UPLOAD_FOLDER = 'static/img/users_profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

default_profile_pics = ['profile1.png', 'profile2.png', 'profile3.png', 'profile4.png', 'profile5.png',
                'profile6.png', 'profile7.png', 'profile8.png', 'profile9.png', 'profile10.png']

@app.route('/')
def home():
    return render_template('home.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method=='POST':     
        primeiro_nome=request.form.get('primeiro_nome')
        email=request.form.get('email')
        senha=request.form.get('senha')
        confirmar_senha=request.form.get('confirmar_senha')
        email_duplicado=User.query.filter_by(email=email).first()
        
        if email_duplicado:
            flash('Este e-mail já está cadastrado no sistema, faça login', 'error')
            return render_template('registro.html', primeiro_nome=primeiro_nome, email=email)
        
        if senha != confirmar_senha:
            flash('As senhas nao coincidem, Tente novamente', 'error')
            return render_template('registro.html', primeiro_nome=primeiro_nome, email=email)
        
        if  len(primeiro_nome.split()) > 1:
            flash('Por favor, digite apenas o seu primeiro nome.', 'error')
            return render_template('registro.html', primeiro_nome=primeiro_nome, email=email)
        
        else:
            random_profile_pic = random.choice(default_profile_pics)
            user = User(first_name=primeiro_nome, email=email, profile_pic=random_profile_pic)
            user.set_password(senha)
            db.session.add(user)
            db.session.commit()
            flash('Conta criada com sucesso', 'success')
            return redirect(url_for('login'))          
    
    return render_template('registro.html') 


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        senha=request.form.get('senha')
        email_existente=User.query.filter_by(email=email).first()
        if email_existente and email_existente.check_password(senha):
            session['user_id'] = email_existente.id 
            return redirect(url_for('dashboard'))
        elif email_existente:
            flash('Senha incorreta.', 'error')
        else:
            flash('Usuário não encontrado.', 'error')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    if request.method=='POST':
        new_name=request.form.get('nome')
        if  len(new_name.split()) > 1:
            flash('Por favor, digite apenas o seu primeiro nome.', 'error')
            return render_template('perfil.html', user=user)
        else:
            user.first_name = new_name
            db.session.commit()
            flash('Nome atualizado com sucesso!', 'success')
            return render_template('perfil.html', user=user)
    return render_template('perfil.html', user=user)

@app.route('/atualizar_foto', methods=['POST'])
@login_required
def atualizar_foto():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    nova_foto = request.files.get('nova_foto')

    if nova_foto:
        if allowed_file(nova_foto.filename):
            filename = secure_filename(nova_foto.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            nova_foto.save(filepath)

            # Remover a foto de perfil antiga (se não for uma padrão)
            if user.profile_pic not in ['default1.png', 'default2.png', ..., 'default10.png']:
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_pic)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            elif user.profile_pic != 'default.png': # Se você tiver um 'default.png' genérico
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_pic)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)

            user.profile_pic = filename
            db.session.commit()
            flash('Foto de perfil atualizada com sucesso!', 'success')
        else:
            flash('Formato de arquivo não permitido.', 'error')
    return redirect(url_for('perfil'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

