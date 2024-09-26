from flask_restful import Resource, reqparse
from models import db, Incidente, HistorialModificaciones, EstadoEnum, IncidenteSchema, HistorialModificacionesSchema
from lib.decorators import roles_required, confidential_fields
from flask_jwt_extended import get_jwt_identity
import hashlib
from flask import request

# Definir los argumentos requeridos y opcionales
parser = reqparse.RequestParser()
parser.add_argument('canal', type=str, required=True, help="El canal es requerido")
parser.add_argument('descripcion', type=str, required=True, help="La descripción es requerida")
parser.add_argument('estado', type=str, required=True, help="El estado es requerido")
parser.add_argument('prioridad', type=int, required=True, help="La prioridad es requerida")
parser.add_argument('idGestor', type=int, required=True, help="El id del gestor es requerido")
parser.add_argument('idClienteIncidente', type=int, required=True, help="El id del cliente es requerido")
parser.add_argument('solucion', type=str, required=False)
parser.add_argument('detallesSolucion', type=str, required=False)  # Confidencial
parser.add_argument('logsTecnicos', type=str, required=False)  # Confidencial

incidente_schema = IncidenteSchema(many=True)
historial_schema = HistorialModificacionesSchema(many=True)

# Función para calcular el hash
def calculate_hash(data):
    return hashlib.sha256(data).hexdigest()

# Verificar el hash recibido con el hash calculado del cuerpo de la solicitud
def verify_hash(request):
    data = request.get_data()
    received_hash = request.headers.get('X-Body-Hash')
    calculated_hash = calculate_hash(data)

    if received_hash != calculated_hash:
        return False
    return True

# Registrar la modificación en el historial
def registrar_modificacion(incidente_id, cambio, idUsuario):
    nueva_modificacion = HistorialModificaciones(
        idIncidente=incidente_id,
        cambio=cambio,
        idUsuario=idUsuario
    )
    db.session.add(nueva_modificacion)
    db.session.commit()

class IncidentesResource(Resource):
    @roles_required(['Gestor', 'Supervisor', 'Admin'])
    @confidential_fields(data="list")
    def get(self):
        incidentes = Incidente.query.all()
        return incidente_schema.dump(incidentes), 200

    @roles_required(['Gestor', 'Supervisor', 'Admin'])
    def post(self):
        if not verify_hash(request):
            return {'message': 'Hash mismatch. Possible tampering detected.'}, 400

        data = parser.parse_args()

        # Verificación del estado permitido
        if data['estado'] not in EstadoEnum.__members__:
            return {'message': 'Estado no permitido. Valores válidos: Abierto, Cerrado, En Progreso, Escalado'}, 400

        nuevo_incidente = Incidente(
            canal=data['canal'],
            descripcion=data['descripcion'],
            estado=data['estado'],
            prioridad=data['prioridad'],
            idGestor=data['idGestor'],
            idClienteIncidente=data['idClienteIncidente'],
            solucion=data.get('solucion'),
            detallesSolucion=data.get('detallesSolucion', ''),  # Puede ser confidencial
            logsTecnicos=data.get('logsTecnicos', '')  # Puede ser confidencial
        )
        db.session.add(nuevo_incidente)
        db.session.commit()

        return incidente_schema.dump(nuevo_incidente), 201

class IncidenteResource(Resource):
    @roles_required(['Gestor', 'Supervisor', 'Admin'])
    @confidential_fields(data="single")
    def get(self, incidente_id):
        incidente = Incidente.query.get_or_404(incidente_id)
        return incidente_schema.dump(incidente), 200

    @roles_required(['Gestor', 'Supervisor', 'Admin'])
    def put(self, incidente_id):
        if not verify_hash(request):
            return {'message': 'Hash mismatch. Possible tampering detected.'}, 400

        data = parser.parse_args()
        incidente = Incidente.query.get_or_404(incidente_id)
        current_user = get_jwt_identity()
        rol = current_user.get('rol')

        cambios = []
        # Modificaciones permitidas según el rol
        if rol == 'Gestor':
            if 'canal' in data:
                cambios.append(f"canal modificado de {incidente.canal} a {data['canal']}")
                incidente.canal = data['canal']
            if 'descripcion' in data:
                cambios.append(f"descripcion modificada de {incidente.descripcion} a {data['descripcion']}")
                incidente.descripcion = data['descripcion']
            if 'estado' in data:
                cambios.append(f"estado modificado de {incidente.estado} a {data['estado']}")
                incidente.estado = data['estado']
            if 'prioridad' in data:
                cambios.append(f"prioridad modificada de {incidente.prioridad} a {data['prioridad']}")
                incidente.prioridad = data['prioridad']
        elif rol in ['Supervisor', 'Admin']:  # Roles superiores pueden modificar campos confidenciales
            if 'detallesSolucion' in data:
                cambios.append(f"detallesSolucion modificado")
                incidente.detallesSolucion = data['detallesSolucion']
            if 'logsTecnicos' in data:
                cambios.append(f"logsTecnicos modificado")
                incidente.logsTecnicos = data['logsTecnicos']

        db.session.commit()

        for cambio in cambios:
            registrar_modificacion(incidente_id, cambio, current_user['id'])

        return incidente_schema.dump(incidente), 200

    @roles_required(['Admin'])
    def delete(self, incidente_id):
        incidente = Incidente.query.get_or_404(incidente_id)
        db.session.delete(incidente)
        db.session.commit()
        return '', 204

class HistorialModificacionesResource(Resource):
    @roles_required(['Supervisor', 'Admin'])
    def get(self, incidente_id):
        historial = HistorialModificaciones.query.filter_by(idIncidente=incidente_id).all()
        if not historial:
            return {'message': 'No se encontraron modificaciones para este incidente'}, 404

        return historial_schema.dump(historial), 200
