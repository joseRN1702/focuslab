import os
from flask import Flask, render_template, redirect, request, url_for, flash, session
from models import User, Note, Task, Group, db
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
def dashboard_dia_url(data): # 'data' aqui é a string "dd-mm-yyyy" da URL
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    now = datetime.datetime.now() # Defina 'now'

    try:
        dia, mes, ano = map(int, data.split('-'))
        data_obj = datetime.date(ano, mes, dia)
        data_exibicao = f"{data_obj.day:02d}/{data_obj.month:02d}/{data_obj.year}"
    except ValueError:
        flash('Formato de data inválido na URL do dashboard.', 'error')
        # Considere para onde redirecionar, talvez para a agenda com o ano atual
        return redirect(url_for('agenda', ano=now.year))

    nota_do_dia = Note.query.filter_by(user_id=user_id, date=data_obj).first()
    tarefas_do_dia = Task.query.filter_by(user_id=user_id, date=data_obj).all()

    return render_template('dashboard.html',
                           user=user,
                           data_exibicao=data_exibicao,       # Para mostrar no título (dd/mm/yyyy)
                           data_param_original=data,       # Para os formulários (dd-mm-yyyy)
                           now=now,                        # Para fallback nos formulários
                           nota=nota_do_dia,
                           tarefas=tarefas_do_dia)

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
            return render_template('perfil.html', user=user, now=now)
        else:
            user.first_name = new_name
            db.session.commit()
            flash('Nome atualizado com sucesso!', 'success')
            return render_template('perfil.html', user=user, now=now)
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
    now = datetime.datetime.now()
    for mes in range(1, 13):
        dias_do_mes = cal.monthdays2calendar(ano_selecionado, mes)
        calendario_ano[mes] = dias_do_mes

    return render_template('agenda.html', calendario=calendario_ano, meses=meses_portugues, dias_semana=dias_semana_portugues, ano=ano_selecionado, now=now)

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

@app.route('/grupo/<int:group_id>', methods=['GET', 'POST']) # Nova rota para visualizar e gerenciar um grupo
@login_required
def visualizar_grupo(group_id):
    user_id = session.get('user_id')
    current_user = User.query.get_or_404(user_id)
    group = Group.query.get_or_404(group_id)
    now = datetime.datetime.now() # Para o botão voltar no header

    # Verifica se o usuário atual é o proprietário ou um membro para visualização
    # (Você pode refinar as permissões para adicionar/remover membros depois)
    if group.owner_id != user_id and current_user not in group.members:
        flash('Você não tem permissão para visualizar este grupo.', 'error')
        return redirect(url_for('grupos'))

    if request.method == 'POST':
        # Lógica para adicionar/remover membros
        email_membro_para_adicionar = request.form.get('email_membro')
        if email_membro_para_adicionar:
            # Apenas o proprietário pode adicionar membros (exemplo de permissão)
            if group.owner_id == user_id:
                membro_a_adicionar = User.query.filter_by(email=email_membro_para_adicionar).first()
                if membro_a_adicionar:
                    if membro_a_adicionar in group.members:
                        flash(f'{membro_a_adicionar.first_name} já é membro deste grupo.', 'info')
                    else:
                        group.members.append(membro_a_adicionar)
                        db.session.commit()
                        flash(f'{membro_a_adicionar.first_name} adicionado ao grupo!', 'success')
                else:
                    flash(f'Usuário com email "{email_membro_para_adicionar}" não encontrado.', 'error')
            else:
                flash('Apenas o proprietário do grupo pode adicionar membros.', 'warning')
            return redirect(url_for('visualizar_grupo', group_id=group.id))

    # Para o botão Voltar no header, precisamos de uma 'data_filtrada' padrão
    data_para_voltar = f"{now.day:02d}-{now.month:02d}-{now.year}"

    # Busca todos os usuários para um possível dropdown de adicionar membros (simplificado)
    # Em uma aplicação real, você poderia querer uma busca de usuários ou uma lista de amigos.
    todos_usuarios = User.query.filter(User.id != current_user.id).all() # Exclui o próprio usuário

    return render_template('visualizar_grupo.html',
                           group=group,
                           current_user=current_user,
                           todos_usuarios=todos_usuarios,
                           now=now,
                           data_filtrada=data_para_voltar)


@app.route('/remover_membro/<int:group_id>/<int:member_id>', methods=['POST'])
@login_required
def remover_membro(group_id, member_id):
    user_id = session.get('user_id')
    group = Group.query.get_or_404(group_id)
    membro_a_remover = User.query.get_or_404(member_id)

    # Apenas o proprietário pode remover membros
    if group.owner_id != user_id:
        flash('Apenas o proprietário do grupo pode remover membros.', 'error')
        return redirect(url_for('visualizar_grupo', group_id=group.id))

    # O proprietário não pode ser removido
    if membro_a_remover.id == group.owner_id:
        flash('O proprietário não pode ser removido do grupo.', 'warning')
        return redirect(url_for('visualizar_grupo', group_id=group.id))

    if membro_a_remover in group.members:
        group.members.remove(membro_a_remover)
        db.session.commit()
        flash(f'{membro_a_remover.first_name} foi removido do grupo.', 'success')
    else:
        flash(f'{membro_a_remover.first_name} não é membro deste grupo.', 'info')

    return redirect(url_for('visualizar_grupo', group_id=group.id))

@app.route('/grupos', methods=['GET', 'POST'])
@login_required
def grupos():
    user_id = session.get('user_id')
    current_user = User.query.get_or_404(user_id)
    now = datetime.datetime.now() # Para o botão voltar no header

    data_para_voltar = f"{now.day:02d}-{now.month:02d}-{now.year}"

    if request.method == 'POST':
        group_name = request.form.get('group_name')
        group_description = request.form.get('group_description')

        if not group_name:
            flash('O nome do grupo é obrigatório.', 'error')
        elif len(group_name) > 100:
            flash('O nome do grupo não pode exceder 100 caracteres.', 'error')
        else:
            existing_group = Group.query.filter_by(name=group_name).first() # Case-sensitive
            if existing_group:
                flash(f'Um grupo com o nome "{group_name}" já existe. Por favor, escolha outro nome.', 'error')
            else:
                new_group = Group(name=group_name, description=group_description, owner_id=user_id)
                db.session.add(new_group)
                
                new_group.members.append(current_user)
                
                try:
                    db.session.commit()
                    flash(f'Grupo "{group_name}" criado com sucesso!', 'success')
                    return redirect(url_for('grupos')) # Redireciona para a mesma página para ver o novo grupo
                except Exception as e:
                    db.session.rollback() # Desfaz em caso de erro no commit
                    flash(f'Erro ao criar o grupo: {str(e)}', 'error')


    owned_groups = current_user.owned_groups.order_by(Group.created_at.desc()).all()
    
    member_groups = current_user.member_of_groups.filter(Group.owner_id != user_id).order_by(Group.name).all()

    return render_template('grupos.html',
                           owned_groups=owned_groups,
                           member_groups=member_groups,
                           now=now, # Passando 'now' para o template
                           data_filtrada=data_para_voltar # Passando 'data_filtrada' para o header
                           )

@app.route('/deletar_tarefa/<int:tarefa_id>', methods=['POST'])
@login_required
def deletar_tarefa(tarefa_id):
    user_id = session.get('user_id')
    tarefa = Task.query.get_or_404(tarefa_id)

    # Verifica se a tarefa pertence ao usuário logado
    if tarefa.user_id != user_id:
        flash('Você não tem permissão para deletar esta tarefa.', 'error')
        # Redireciona para a página anterior ou para o dashboard do dia da tarefa
        data_redirect = f"{tarefa.date.day:02d}-{tarefa.date.month:02d}-{tarefa.date.year}"
        return redirect(request.referrer or url_for('dashboard_dia_url', data=data_redirect))

    try:
        db.session.delete(tarefa)
        db.session.commit()
        flash('Tarefa deletada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar a tarefa: {str(e)}', 'error')

    data_redirect = f"{tarefa.date.day:02d}-{tarefa.date.month:02d}-{tarefa.date.year}"
    return redirect(request.referrer or url_for('dashboard_dia_url', data=data_redirect))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

