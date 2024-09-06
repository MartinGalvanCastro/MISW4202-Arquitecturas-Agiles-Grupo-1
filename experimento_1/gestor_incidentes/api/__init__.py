from flask_restful import Api
from .incidente import IncidenteResource
from .estado_servicio import ActivarFallosResource
from .health import HealthCheck
from config import INSTANCE_TYPE

api = Api()

def initialize_routes(app):
    api.add_resource(IncidenteResource, '/incidentes')
    api.add_resource(HealthCheck,'/healthcheck')
    if INSTANCE_TYPE == 'principal':
        api.add_resource(ActivarFallosResource, '/activar_fallos')
    api.init_app(app)
