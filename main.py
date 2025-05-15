import os
from flask import Flask, render_template, redirect, request, url_for, flash, session
from models import User, Note, Task, db
from functools import wraps
import random
import datetime
from werkzeug.utils import secure_filename
import calendar
import pytz

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

meses_portugues = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
dias_semana_portugues = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

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
            hoje = datetime.date.today()
            hoje = datetime.date.today()
            data_formatada = f"{hoje.day:02d}-{hoje.month:02d}-{hoje.year}"
            return redirect(url_for('dashboard_dia_url', data=data_formatada))
        elif email_existente:
            flash('Senha incorreta.', 'error')
        else:
            flash('Usuário não encontrado.', 'error')
    return render_template('login.html')

@app.route('/dashboard/<data>')
@login_required
def dashboard_dia_url(data):
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)

    try:
        dia, mes, ano = map(int, data.split('-'))
        data_filtrada = datetime.date(ano, mes, dia)
        data_exibicao = f"{data_filtrada.day:02d}/{data_filtrada.month:02d}/{data_filtrada.year}"
    except ValueError:
        flash('Formato de data inválido na URL do dashboard.', 'error')
        return redirect(url_for('agenda'))

    nota_do_dia = Note.query.filter_by(user_id=user_id, date=data_filtrada).first()
    tarefas_do_dia = Task.query.filter_by(user_id=user_id, date=data_filtrada).all()

    return render_template('dashboard.html', user=user, data_filtrada=data_exibicao, nota=nota_do_dia, tarefas=tarefas_do_dia)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    now = datetime.datetime.now()
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
    return render_template('perfil.html', user=user, now=now)

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
            if user.profile_pic not in ['default1.png', 'default2.png', ..., 'default10.png']:
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_pic)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            elif user.profile_pic != 'default.png':
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_pic)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)

            user.profile_pic = filename
            db.session.commit()
            flash('Foto de perfil atualizada com sucesso!', 'success')
        else:
            flash('Formato de arquivo não permitido.', 'error')
    return redirect(url_for('perfil'))

@app.route('/agenda')
@login_required
def agenda():
    hoje = datetime.date.today()
    ano_selecionado = hoje.year
    cal = calendar.Calendar(firstweekday=0)
    calendario_ano = {}
    for mes in range(1, 13):
        dias_do_mes = cal.monthdays2calendar(ano_selecionado, mes)
        calendario_ano[mes] = dias_do_mes

    return render_template('agenda.html', calendario=calendario_ano, meses=meses_portugues, dias_semana=dias_semana_portugues, ano=ano_selecionado)

@app.route('/salvar_nota', methods=['POST'])
@login_required
def salvar_nota():
    user_id = session.get('user_id')
    content = request.form.get('content')
    data_str = request.form.get('data')

    if not data_str:
        flash('Erro ao salvar a nota: data não especificada.', 'error')
        return redirect(request.referrer)

    try:
        ano, mes, dia = map(int, data_str.split('-'))
        data_nota = datetime.date(ano, mes, dia)
    except ValueError:
        flash('Erro ao salvar a nota: formato de data inválido.', 'error')
        return redirect(request.referrer)

    nota = Note.query.filter_by(user_id=user_id, date=data_nota).first()

    if nota:
        nota.content = content
        nota.updated_at = datetime.datetime.now(pytz.timezone('America/Sao_Paulo'))
        db.session.commit()
        flash('Nota atualizada com sucesso!', 'success')
    else:
        nova_nota = Note(content=content, date=data_nota, user_id=user_id)
        db.session.add(nova_nota)
        db.session.commit()
        flash('Nota salva com sucesso!', 'success')

    return redirect(request.referrer)

@app.route('/adicionar_tarefa', methods=['POST'])
@login_required
def adicionar_tarefa():
    user_id = session.get('user_id')
    nome_tarefa = request.form.get('nome_tarefa')
    data_str = request.form.get('data')
    cor_tarefa = request.form.get('cor_tarefa')

    if not nome_tarefa:
        flash('O nome da tarefa não pode estar vazio.', 'error')
        return redirect(request.referrer)

    if not data_str:
        flash('Erro ao adicionar tarefa: data não especificada.', 'error')
        return redirect(request.referrer)

    try:
        ano, mes, dia = map(int, data_str.split('-'))
        data_tarefa = datetime.date(ano, mes, dia)
    except ValueError:
        flash('Erro ao adicionar tarefa: formato de data inválido.', 'error')
        return redirect(request.referrer)

    nova_tarefa = Task(name=nome_tarefa, date=data_tarefa, user_id=user_id, color=cor_tarefa)
    db.session.add(nova_tarefa)
    db.session.commit()
    flash('Tarefa adicionada com sucesso!', 'success')

    return redirect(request.referrer)

@app.route('/toggle_tarefa/<int:tarefa_id>', methods=['POST'], endpoint='toggle_tarefa')
@login_required
def toggle_tarefa(tarefa_id):
    tarefa = Task.query.get_or_404(tarefa_id)
    if tarefa.user_id != session.get('user_id'):
        flash('Você não tem permissão para alterar esta tarefa.', 'error')
        return redirect(request.referrer)
    tarefa.done = not tarefa.done
    db.session.commit()
    return redirect(request.referrer)

@app.route('/grupos')
@login_required
def grupos():
    return render_template('grupos.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

