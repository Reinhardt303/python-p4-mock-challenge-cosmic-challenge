#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

Api.error_router = lambda self, router, error: router(error)
api = Api(app)

class Scientists(Resource):
    def get(self):
        scientists = [s.to_dict(rules=("-missions",)) for s in Scientist.query.all()]
        return make_response(scientists, 200)
    
    def post(self):
        req_data = request.get_json()
        try:
            sci = Scientist(**req_data)
            db.session.add(sci)
            db.session.commit()
            return make_response(sci.to_dict(), 201)
        except ValueError as e:
            return make_response({"errors": ['validation errors']}, 400)

    
class ScientistsById(Resource):
    def get(self, id):
        try:
            sci = Scientist.query.filter(Scientist.id == id).first()
            if not sci:
                return make_response({"error": "Scientist not found"}, 404)
            return make_response(sci.to_dict(), 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)
    
    def delete(self, id):
        sci = Scientist.query.filter(Scientist.id == id).first()
        if not sci:
            return make_response({"error": "Scientist not found"}, 404)
        db.session.delete(sci)
        db.session.commit()
        return make_response({}, 204)
    
    def patch(self, id):
        sci = Scientist.query.filter(Scientist.id == id).first()
        if not sci:
            return make_response({"error": "Scientist not found"}, 404)
        fields = request.get_json()
        try:
            for field in fields:
                setattr(sci, field, fields[field])
            db.session.commit()
            return make_response(sci.to_dict(), 202)
        except ValueError:
            return make_response({"errors": ['validation errors']}, 400)

class Planets(Resource):
    def get(self):
        planets = [p.to_dict(rules=('-missions',)) for p in Planet.query.all()]
        return make_response(planets, 200)
    
class Missions(Resource):
    
    def post(self):
        req_data = request.get_json()
        try:
            mission = Mission(**req_data)
            db.session.add(mission)
            db.session.commit()
            return make_response(mission.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ['validation errors']}, 400)

api.add_resource(Missions, '/missions')     
api.add_resource(Planets, '/planets') 
api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistsById, '/scientists/<int:id>')

@app.route('/')
def home():
    return ''


if __name__ == '__main__':
    app.run(port=5555, debug=True)
