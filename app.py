from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = 'chave_secreta_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    senha = db.Column(db.String(100))

class Ronda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    qr_code = db.Column(db.String(200))

class SessaoRonda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    data = db.Column(db.Date)
    hora_inicio = db.Column(db.Time)
    hora_fim = db.Column(db.Time)

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sessao_id = db.Column(db.Integer, db.ForeignKey('sessao_ronda.id'))
    ronda_id = db.Column(db.Integer, db.ForeignKey('ronda.id'))
    hora = db.Column(db.Time)
    foto = db.Column(db.String(200))
    obs = db.Column(db.String(500))
    nome_militar = db.Column(db.String(100))
    numero_lacre = db.Column(db.String(100))

@app.route('/adicionar_usuario', methods=['GET', 'POST'])
def adicionar_usuario():
    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]
        novo_usuario = Usuario(nome=nome, senha=senha)
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect('/')
    return render_template('adicionar_usuario.html')

@app.route("/", methods=["GET", "POST"])
def inicio():
    if request.method == "POST":
        nome = request.form["usuario"]
        senha = request.form["senha"]
        usuario = Usuario.query.filter_by(nome=nome, senha=senha).first()
        if usuario:
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            return render_template("index_adm.html")
        else:
            return render_template("login.html")
    return render_template('login.html')

@app.route('/adicionar_ronda', methods=['GET', 'POST'])
def adicionar_ronda():
    if request.method == "POST":
        tipo_de_ronda = request.form["tipo"]
        nome_da_ronda = request.form["nome_da_ronda"]
        nova_ronda = Ronda(nome=nome_da_ronda, tipo=tipo_de_ronda)
        db.session.add(nova_ronda)
        db.session.commit()
    return render_template('adicionar_ronda.html')

@app.route('/ver_rondas')
def ver_rondas():
    rondas = Ronda.query.all()
    return render_template('ver_rondas.html', rondas=rondas)

@app.route('/editar_ronda/<int:id>', methods=['GET', 'POST'])
def editar_ronda(id):
    ronda = db.session.get(Ronda, id)
    if request.method == "POST":
        ronda.nome = request.form["nome"]
        ronda.tipo = request.form["tipo"]
        db.session.commit()
    return render_template('editar_ronda.html', ronda=ronda)

@app.route('/apagar_ronda/<int:id>')
def apagar_ronda(id):
    ronda = db.session.get(Ronda, id)
    db.session.delete(ronda)
    db.session.commit()
    return redirect('/ver_rondas')


@app.route("/registrar_ronda", methods=["GET", "POST"])
def registrar_ronda():
    if request.method == "POST":
        pass

    todas_rondas = Ronda.query.all()
    rondas_com_status = []

    for ronda in todas_rondas:
        # Verifica se já existe algum registro para esta ronda
        ja_foi_registrada = Registro.query.filter_by(ronda_id=ronda.id).first()

        # Se encontrou registro, está concluída. Se não, está pendente.
        if ja_foi_registrada:
            status = "Concluída"
        else:
            status = "Pendente"

        # Guarda os dados da ronda junto com o status dela
        rondas_com_status.append({
            'id': ronda.id,
            'nome': ronda.nome,
            'tipo': ronda.tipo,
            'status': status
        })
    return render_template('registrar_ronda.html', rondas=rondas_com_status)

@app.route('/registro/<int:id>', methods=['GET', 'POST'])
def registro(id):
    ronda = db.session.get(Ronda, id)
    return render_template('registro.html', ronda=ronda)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not Usuario.query.first():
            admin = Usuario(nome='admin', senha='123')
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin criado!")

    app.run(debug=True, host='0.0.0.0')