from flask_restful import Api
from .incidente import IncidentesResource, IncidenteResource, HistorialModificacionesResource

api = Api()

def initialize_routes(app):
    api.add_resource(IncidentesResource, '/incidentes')
    api.add_resource(IncidenteResource, '/incidentes/<int:incidente_id>')
    api.add_resource(HistorialModificacionesResource, '/incidentes/<int:incidente_id>/historial')
    api.init_app(app)
