from flask import Flask
from models import db, User, UserRoleEnum
from api import initialize_routes
from flask_jwt_extended import JWTManager
import os
from prometheus_flask_exporter import PrometheusMetrics
from faker import Faker

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'





metrics = PrometheusMetrics(app)
metrics.info('app_info', 'AuthN/AuthZ Service', version='1.0.0')

fake = Faker()

def poblar_base_de_datos():
    if User.query.count() == 0:
        # Crear un usuario 'Gestor'
        gestor = User(
            username="gestor",
            role=UserRoleEnum.GESTOR
        )
        gestor.set_password('password123')
        db.session.add(gestor)

        # Crear un usuario 'Supervisor'
        supervisor = User(
            username="supervisor",
            role=UserRoleEnum.SUPERVISOR
        )
        supervisor.set_password('password123')
        db.session.add(supervisor)

        # Crear un usuario 'Admin'
        admin = User(
            username="admin",
            role=UserRoleEnum.ADMIN
        )
        admin.set_password('password123')
        db.session.add(admin)

        db.session.commit()


db.init_app(app)
jwt = JWTManager(app)
initialize_routes(app)
with app.app_context():
    db.create_all()
    poblar_base_de_datos()

@app.after_request
def after_hook(response):
    return response

if __name__ == '__main__':
    # Crear un usuario por cada rol
    app.run(host='0.0.0.0', port=5000)
