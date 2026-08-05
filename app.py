from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///estoque.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Dicionário para converter nomes em português para código de cor CSS
MAPA_CORES = {
    'preto': '#000000',
    'preta': '#000000',
    'branco': '#FFFFFF',
    'branca': '#FFFFFF',
    'vermelho': '#FF0000',
    'vermelha': '#FF0000',
    'azul': '#0000FF',
    'azul marinho': '#000080',
    'verde': '#008000',
    'militar': '#4B5320',
    'amarelo': '#FFFF00',
    'amarela': '#FFFF00',
    'cinza': '#808080',
    'chumbo': '#333333',
    'rosa': '#FFC0CB',
    'pink': '#FF1493',
    'roxo': '#800080',
    'roxa': '#800080',
    'vinho': '#722F37',
    'bordo': '#800020',
    'bordô': '#800020',
    'marrom': '#964B00',
    'laranja': '#FFA500',
    'bege': '#F5F5DC'
}

def obter_hex_cor(nome_cor):
    cor_limpa = nome_cor.lower().strip()
    return MAPA_CORES.get(cor_limpa, '#CCCCCC') # Cinza padrão se não encontrar no dicionário

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100), nullable=False)
    cor = db.Column(db.String(50), nullable=False)
    tamanho = db.Column(db.String(10), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    codigo = db.Column(db.String(50), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    ordem_tamanhos = {'PP': 1, 'P': 2, 'M': 3, 'G': 4, 'GG': 5, 'G1': 6, 'G2': 7, 'G3': 8}
    produtos = Produto.query.all()
    
    # Associa a cor hexadecimal a cada produto antes de enviar para a tela
    for p in produtos:
        p.cor_hex = obter_hex_cor(p.cor)

    produtos_ordenados = sorted(
        produtos, 
        key=lambda x: (
            x.modelo.lower(), 
            x.cor.lower(), 
            ordem_tamanhos.get(x.tamanho.upper(), 99)
        )
    )
    
    return render_template('index.html', produtos=produtos_ordenados)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    modelo = request.form.get('modelo').strip()
    cor = request.form.get('cor').strip()
    tamanho = request.form.get('tamanho')
    quantidade = int(request.form.get('quantidade'))

    produto_existente = Produto.query.filter(
        Produto.modelo.ilike(modelo),
        Produto.cor.ilike(cor),
        Produto.tamanho == tamanho
    ).first()

    if produto_existente:
        produto_existente.quantidade += quantidade
    else:
        novo_produto = Produto(modelo=modelo, cor=cor, tamanho=tamanho, quantidade=quantidade)
        db.session.add(novo_produto)
    
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/baixa/<int:id>', methods=['POST'])
def baixa(id):
    produto = Produto.query.get_or_404(id)
    qtd_baixa = int(request.form.get('qtd_baixa', 1))
    
    if produto.quantidade > qtd_baixa:
        produto.quantidade -= qtd_baixa
    else:
        db.session.delete(produto)
        
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)