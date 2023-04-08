from datetime import date, datetime
from flask import Flask, jsonify, request, render_template
from flask_swagger import swagger
from flask_sqlalchemy import SQLAlchemy
import os


# Créer l'application Flask
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiser la base de données
db = SQLAlchemy(app)



class Personne(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)

    def __init__(self, nom, prenom, date_naissance):
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance

    def age(self):
        aujourdhui = date.today()
        return aujourdhui.year - self.date_naissance.year - ((aujourdhui.month, aujourdhui.day) < (self.date_naissance.month, self.date_naissance.day))

@app.before_first_request
def create_tables():
    db.create_all()
    personne1 = Personne(nom='Dupont', prenom='Pierre', date_naissance=datetime(1980, 1, 1))
    personne2 = Personne(nom='Martin', prenom='Marie', date_naissance=datetime(1990, 3, 15))

    db.session.add(personne1)
    db.session.add(personne2)
    db.session.commit()

@app.route('/')
def hello():
    return 'Hello, world!'


# Endpoint pour ajouter une nouvelle personne
@app.route('/personnes', methods=['POST'])
def ajouter_personne():
    """
    Sauvegarde une nouvelle Personne.
    ---
    parameters:
      - name: personne
        in: body
        description: Personne à enregistrer.
        required: true
        schema:
          $ref: '#/definitions/Personne'
    responses:
      201:
        description: Personne créée avec succès.
        schema:
          $ref: '#/definitions/Personne'
      400:
        description: Données de la personne invalides.
    """
    donnees = request.get_json()
    nom = donnees['nom']
    prenom = donnees['prenom']
    date_naissance = donnees['date_naissance']

    # Vérifier que la personne a moins de 150 ans
    if Personne(nom=nom, prenom=prenom, date_naissance=date_naissance).age() >= 150:
        return jsonify({'message': 'Une personne ne peut pas avoir plus de 150 ans.'}), 400

    personne = Personne(nom=nom, prenom=prenom, date_naissance=date_naissance)
    db.session.add(personne)
    db.session.commit()
    return jsonify({'message': 'Personne ajoutée avec succès.'}), 201


# Endpoint pour récupérer toutes les personnes enregistrées
@app.route('/personnes', methods=['GET'])
def recuperer_personnes():
    """
    Renvoie toutes les Personnes enregistrées par ordre alphabétique, avec leur âge actuel.
    ---
    responses:
      200:
        description: Liste de toutes les Personnes enregistrées.
        schema:
          type: array
          items:
            $ref: '#/definitions/Personne'
      404:
        description: Aucune personne enregistrée.
    """
    personnes = Personne.query.order_by(Personne.nom).all()
    resultat = []
    for personne in personnes:
        resultat.append({
            'nom': personne.nom,
            'prenom': personne.prenom,
            'date_naissance': str(personne.date_naissance),
            'age': personne.age()
        })
    return jsonify(resultat), 200


@app.route('/doc')
def api_doc():
    """
    Endpoint pour accéder à la documentation Swagger de l'API.
    """
    return render_template('swagger_ui.html') # Renvoyer le template HTML avec les données YAML

if __name__ == '__main__':
    app.run(debug=True)