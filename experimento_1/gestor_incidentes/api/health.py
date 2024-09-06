from flask import request
from flask_restful import Resource
from models import db, Incidente

class HealthCheck(Resource):
    def get(self):
        try:
            db.session.query(Incidente).count()
            return {"status":"HEALTHY"}, 200
        except Exception as e:
            return {"status":"UNHEALTHY"}, 200
