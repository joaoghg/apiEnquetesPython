from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Enquete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(30), unique=True, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    data = db.Column(db.DateTime, nullable=False, default=datetime.now)
    opcoes = db.relationship('EnqueteOpcoes', backref='author', lazy=True, cascade='all,delete')


class EnqueteOpcoes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opcao = db.Column(db.String(100), unique=True, nullable=False)
    enquete_id = db.Column(db.Integer, db.ForeignKey('enquete.id'), nullable=False)
    votos = db.relationship('Votos', backref='author', lazy=True, cascade='all,delete')


class Votos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False, default=datetime.now)
    enquete_opcoes_id = db.Column(db.Integer, db.ForeignKey('enquete_opcoes.id'), nullable=False)


@app.route('/api/enquetes', methods=['POST'])
def criar_enquete():
    dados = request.json

    if 'titulo' not in dados or 'descricao' not in dados:
        return jsonify({'msg': 'Campos "titulo" e "descricao" são obrigatórios.'}), 400

    nova_enquete = Enquete(titulo=dados['titulo'], descricao=dados['descricao'])

    db.session.add(nova_enquete)
    db.session.commit()

    return jsonify({'msg': 'Enquete criada com sucesso.', 'id': nova_enquete.id}), 201


@app.route('/api/enquetes', methods=['GET'])
def listar_enquetes():
    enquetes = Enquete.query.all()

    enquetes_json = []
    for enquete in enquetes:
        enquete_json = {
            'id': enquete.id,
            'titulo': enquete.titulo,
            'descricao': enquete.descricao,
            'data': enquete.data.strftime('%Y-%m-%d %H:%M:%S')
        }
        enquetes_json.append(enquete_json)

    return jsonify(enquetes_json), 200


@app.route('/api/enquetes/<int:enquete_id>', methods=['GET'])
def obter_detalhes_enquete(enquete_id):
    enquete = Enquete.query.get(enquete_id)

    if enquete is None:
        return jsonify({'msg': 'Enquete não encontrada.'}), 404

    enquete_json = {
        'id': enquete.id,
        'titulo': enquete.titulo,
        'descricao': enquete.descricao,
        'data': enquete.data.strftime('%Y-%m-%d %H:%M:%S')
    }

    return jsonify(enquete_json), 200


@app.route('/api/enquetes/<int:enquete_id>/votar', methods=['POST'])
def votar_enquete(enquete_id):
    dados = request.json

    if 'enquete_opcoes_id' not in dados:
        return jsonify({'msg': 'Campo "enquete_opcoes_id" é obrigatório.'}), 400

    enquete = Enquete.query.get(enquete_id)
    if enquete is None:
        return jsonify({'msg': 'Enquete não encontrada.'}), 404

    opcao_id = dados['enquete_opcoes_id']
    opcao_enquete = EnqueteOpcoes.query.filter_by(id=opcao_id).first()
    if opcao_enquete is None:
        return jsonify({'msg': 'Opção de enquete não encontrada.'}), 404

    novo_voto = Votos(enquete_opcoes_id=opcao_id)
    db.session.add(novo_voto)
    db.session.commit()

    return jsonify({'msg': 'Voto registrado com sucesso.'}), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
