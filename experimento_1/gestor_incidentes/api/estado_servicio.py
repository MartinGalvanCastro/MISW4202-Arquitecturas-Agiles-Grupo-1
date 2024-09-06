from flask import request
from flask_restful import Resource
from config import set_fallar

class ActivarFallosResource(Resource):
    def post(self):
        data = request.get_json()
        activar = data.get('activar', False)
        set_fallar(activar)
        if activar:
            return {"message": "El servicio comenzará a fallar aleatoriamente."}, 200
        else:
            return {"message": "El servicio volverá a responder normalmente."}, 200
