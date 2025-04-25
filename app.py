
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'segredo123'

# Configuração do PostgreSQL (Railway)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lueCWdejYTzxAdazTWdxILNSZwMMlHhV@postgres.railway.internal:5432/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Ordem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loja = db.Column(db.String(50))
    ro = db.Column(db.String(50))
    stock = db.Column(db.String(50))
    vin = db.Column(db.String(50))
    servico = db.Column(db.String(100))
    data = db.Column(db.String(50))

servicos_por_loja = {
    "bmw": ["RECON", "DELIVERY", "PDI", "RECON INTERIOR", "RECON EXTERIOR", "WASH"],
    "acura": ["NCD", "UCD", "PDI", "RECON", "WASH", "SHOWROOM"],
    "nissan": ["DELIVERY+SOLO", "RECON", "DELIVERY+FULL", "MINI DETAIL", "PDI"],
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        loja = request.form['loja'].lower()
        if loja in servicos_por_loja:
            session['loja'] = loja
            return redirect('/painel')
        else:
            return render_template('login.html', erro='Loja inválida.')
    return render_template('login.html')

@app.route('/painel')
def painel():
    if 'loja' not in session:
        return redirect('/')
    loja = session['loja']
    ordens = Ordem.query.filter_by(loja=loja).all()
    return render_template('index.html', loja=loja.upper(), servicos=servicos_por_loja[loja], ordens=[(o.ro, o.stock, o.vin, o.servico, o.data) for o in ordens])

@app.route('/lancar', methods=['POST'])
def lancar():
    if 'loja' not in session:
        return redirect('/')
    nova_ordem = Ordem(
        loja=session['loja'],
        ro=request.form['ro'],
        stock=request.form['stock'],
        vin=request.form['vin'],
        servico=request.form['servico'],
        data=datetime.now().strftime('%d/%m/%Y %H:%M')
    )
    db.session.add(nova_ordem)
    db.session.commit()
    return redirect('/painel')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

with app.app_context():
    db.create_all()
