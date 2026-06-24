from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

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

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date)
    hora = db.Column(db.Time)
    foto = db.Column(db.String(200))
    obs = db.Column(db.String(500))
    nome_militar = db.Column(db.String(100))
    numero_lacre = db.Column(db.String(100))

@app.route("/", methods=["GET", "POST"])
def inicio():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        if usuario == 'admin' and senha == '123':
            return render_template("index_adm.html")
        elif usuario == 'usuario' and senha == '123':
            return render_template("index_user.html")
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)