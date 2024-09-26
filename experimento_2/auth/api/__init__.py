from flask_restful import Api
from .login import LoginResource

api = Api()


def initialize_routes(app):
    api.add_resource(LoginResource, '/login')
    api.init_app(app)