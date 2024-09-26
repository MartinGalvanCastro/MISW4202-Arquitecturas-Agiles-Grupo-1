import random
from flask_restful import Resource, reqparse
from models import db, Incidente
from config import get_fallar
import os

parser = reqparse.RequestParser()
parser.add_argument('canal', type=str, required=True, help="El canal es requerido")
parser.add_argument('descripcion', type=str, required=True, help="La descripción es requerida")
parser.add_argument('estado', type=str, required=True, help="El estado es requerido")
parser.add_argument('prioridad', type=int, required=True, help="La prioridad es requerida")
parser.add_argument('idGestor', type=int, required=True, help="El id del gestor es requerido")
parser.add_argument('idClienteIncidente', type=int, required=True, help="El id del cliente es requerido")
parser.add_argument('solucion', type=str, required=False)



class IncidenteResource(Resource):
    def get(self):
        if get_fallar():
            numero_aleatorio = random.randint(1, 10)
            if numero_aleatorio % 2 == 0:
                return {'message': 'Error interno del servidor simulado'}, 500

        incidentes = Incidente.query.all()
        return [{
            'id': incidente.id,
            'canal': incidente.canal,
            'descripcion': incidente.descripcion,
            'estado': incidente.estado,
            'prioridad': incidente.prioridad,
            'idGestor': incidente.idGestor,
            'idClienteIncidente': incidente.idClienteIncidente,
            'solucion': incidente.solucion,
            'fechaIncidente': incidente.fechaIncidente.strftime("%Y-%m-%d %H:%M:%S")
        } for incidente in incidentes], 200

    def post(self):
        if get_fallar():
            numero_aleatorio = random.randint(1, 10)
            if numero_aleatorio % 2 == 0:
                return {'message': 'Error interno del servidor simulado'}, 500

        data = parser.parse_args()
        nuevo_incidente = Incidente(
            canal=data['canal'],
            descripcion=data['descripcion'],
            estado=data['estado'],
            prioridad=data['prioridad'],
            idGestor=data['idGestor'],
            idClienteIncidente=data['idClienteIncidente'],
            solucion=data.get('solucion')
        )
        db.session.add(nuevo_incidente)
        db.session.commit()
        return {
            'id': nuevo_incidente.id,
            'canal': nuevo_incidente.canal,
            'descripcion': nuevo_incidente.descripcion,
            'estado': nuevo_incidente.estado,
            'prioridad': nuevo_incidente.prioridad,
            'idGestor': nuevo_incidente.idGestor,
            'idClienteIncidente': nuevo_incidente.idClienteIncidente,
            'solucion': nuevo_incidente.solucion,
            'fechaIncidente': nuevo_incidente.fechaIncidente
        }, 201
