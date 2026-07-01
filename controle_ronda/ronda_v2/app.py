from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/fotos'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    senha = db.Column(db.String(100))

class Ronda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    tipo = db.Column(db.String(50))

class SessaoRonda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    data = db.Column(db.Date)
    hora_inicio = db.Column(db.Time)
    hora_fim = db.Column(db.Time)
    concluida = db.Column(db.Boolean, default=False)

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sessao_id = db.Column(db.Integer, db.ForeignKey('sessao_ronda.id'))
    ronda_id = db.Column(db.Integer, db.ForeignKey('ronda.id'))
    hora = db.Column(db.Time)
    foto = db.Column(db.String(200))
    obs = db.Column(db.String(500))
    nome_militar = db.Column(db.String(100))
    numero_lacre = db.Column(db.String(100))

@app.route("/", methods=["GET", "POST"])
def inicio():
    if request.method == "POST":
        nome = request.form["usuario"]
        senha = request.form["senha"]
        usuario = Usuario.query.filter_by(nome=nome, senha=senha).first()
        if usuario:
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            return redirect('/painel')
        return render_template("login.html", erro="Usuário ou senha incorretos")
    return render_template('login.html')

@app.route('/painel')
def painel():
    if 'usuario_id' not in session:
        return redirect('/')
    return render_template("index_adm.html", nome=session['usuario_nome'])

@app.route('/sair')
def sair():
    session.clear()
    return redirect('/')

@app.route('/adicionar_usuario', methods=['GET', 'POST'])
def adicionar_usuario():
    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]
        db.session.add(Usuario(nome=nome, senha=senha))
        db.session.commit()
        return redirect('/painel')
    return render_template('adicionar_usuario.html')

@app.route('/ver_usuarios')
def ver_usuarios():
    usuarios = Usuario.query.all()
    return render_template('ver_usuarios.html', usuarios=usuarios)

@app.route('/apagar_usuario/<int:id>')
def apagar_usuario(id):
    usuario = db.session.get(Usuario, id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect('/ver_usuarios')

@app.route('/adicionar_ronda', methods=['GET', 'POST'])
def adicionar_ronda():
    if request.method == "POST":
        db.session.add(Ronda(nome=request.form["nome_da_ronda"], tipo=request.form["tipo"]))
        db.session.commit()
        return redirect('/ver_rondas')
    return render_template('adicionar_ronda.html')

@app.route('/ver_rondas')
def ver_rondas():
    return render_template('ver_rondas.html', rondas=Ronda.query.all())

@app.route('/editar_ronda/<int:id>', methods=['GET', 'POST'])
def editar_ronda(id):
    ronda = db.session.get(Ronda, id)
    if request.method == "POST":
        ronda.nome = request.form["nome"]
        ronda.tipo = request.form["tipo"]
        db.session.commit()
        return redirect('/ver_rondas')
    return render_template('editar_ronda.html', ronda=ronda)

@app.route('/editar_conta/<int:id>', methods=['GET', 'POST'])
def editar_conta(id):
    usuario = db.session.get(Usuario, id)
    if request.method == "POST":
        usuario.nome = request.form["nome"]
        usuario.senha = request.form["senha"]
        db.session.commit()
        return redirect('/ver_usuarios')
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/apagar_ronda/<int:id>')
def apagar_ronda(id):
    ronda = db.session.get(Ronda, id)
    db.session.delete(ronda)
    db.session.commit()
    return redirect('/ver_rondas')

@app.route('/iniciar_sessao')
def iniciar_sessao():
    if 'usuario_id' not in session:
        return redirect('/')
    nova_sessao = SessaoRonda(
        usuario_id=session['usuario_id'],
        data=date.today(),
        hora_inicio=datetime.now().time(),
        concluida=False
    )
    db.session.add(nova_sessao)
    db.session.commit()
    return redirect(f'/sessao/{nova_sessao.id}')

@app.route('/sessao/<int:id>')
def sessao(id):
    sessao_ativa = db.session.get(SessaoRonda, id)
    rondas = Ronda.query.all()
    registros = Registro.query.filter_by(sessao_id=id).all()
    rondas_registradas = {r.ronda_id: r.id for r in registros}
    return render_template('sessao.html', sessao=sessao_ativa, rondas=rondas, rondas_registradas=rondas_registradas)

@app.route('/registro/<int:sessao_id>/<int:ronda_id>', methods=['GET', 'POST'])
def registro(sessao_id, ronda_id):
    sessao_ativa = db.session.get(SessaoRonda, sessao_id)
    if sessao_ativa.concluida:
        return redirect(f'/sessao/{sessao_id}')
    ronda = db.session.get(Ronda, ronda_id)
    registro_existente = Registro.query.filter_by(sessao_id=sessao_id, ronda_id=ronda_id).first()
    if request.method == "POST":
        foto_path = None
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto and foto.filename:
                os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)
                nome_foto = f"{sessao_id}_{ronda_id}_{datetime.now().strftime('%H%M%S')}.jpg"
                foto.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], nome_foto))
                foto_path = nome_foto
        if registro_existente:
            registro_existente.obs = request.form.get("observacao")
            registro_existente.nome_militar = request.form.get("nome_militar")
            registro_existente.numero_lacre = request.form.get("numero_lacre")
            if foto_path:
                registro_existente.foto = foto_path
        else:
            novo = Registro(
                sessao_id=sessao_id, ronda_id=ronda_id,
                hora=datetime.now().time(),
                obs=request.form.get("observacao"),
                nome_militar=request.form.get("nome_militar"),
                numero_lacre=request.form.get("numero_lacre"),
                foto=foto_path
            )
            db.session.add(novo)
        db.session.commit()
        return redirect(f'/sessao/{sessao_id}')
    return render_template('registro.html', ronda=ronda, sessao_id=sessao_id, registro=registro_existente)

@app.route('/concluir_sessao/<int:id>')
def concluir_sessao(id):
    sessao_ativa = db.session.get(SessaoRonda, id)
    sessao_ativa.hora_fim = datetime.now().time()
    sessao_ativa.concluida = True
    db.session.commit()
    return redirect('/painel')

@app.route('/historico')
def historico():
    if 'usuario_id' not in session:
        return redirect('/')
    sessoes = SessaoRonda.query.order_by(SessaoRonda.data.desc(), SessaoRonda.hora_inicio.desc()).all()
    usuarios = {u.id: u.nome for u in Usuario.query.all()}
    return render_template('historico.html', sessoes=sessoes, usuarios=usuarios)

@app.route('/historico/<int:sessao_id>')
def detalhe_sessao(sessao_id):
    sessao_ativa = db.session.get(SessaoRonda, sessao_id)
    registros = Registro.query.filter_by(sessao_id=sessao_id).all()
    rondas = {r.id: r for r in Ronda.query.all()}
    usuario = db.session.get(Usuario, sessao_ativa.usuario_id)
    return render_template('detalhe_sessao.html', sessao=sessao_ativa, registros=registros, rondas=rondas, usuario=usuario)

@app.route('/apagar_sessoes_incompletas')
def apagar_sessoes_incompletas():
    sessoes = SessaoRonda.query.filter_by(concluida=False).all()
    for s in sessoes:
        db.session.delete(s)
    db.session.commit()
    return redirect('/historico')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not Usuario.query.first():
            db.session.add(Usuario(nome='admin', senha='123'))
            db.session.commit()
    app.run(debug=True, host='0.0.0.0')
