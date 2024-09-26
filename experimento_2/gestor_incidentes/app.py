from flask import Flask, request
from models import db
from api import initialize_routes
from faker import Faker
from models import Incidente
import os
from config import INSTANCE_TYPE
from prometheus_client import Counter
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///incidentes.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_incidentes.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
fake = Faker()



metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')

request_counter = Counter(
    'experimento_1_data', 'Total HTTP Requests',
    ['instance', 'path', 'method', 'status_code']
)


def poblar_base_de_datos(cantidad=10):
    if Incidente.query.count() == 0:
        for _ in range(cantidad):
            incidente = Incidente(
                canal=fake.random_element(elements=('Email', 'Chat', 'Teléfono')),
                descripcion=fake.sentence(),
                estado=fake.random_element(elements=('Pendiente', 'En Progreso', 'Resuelto')),
                prioridad=fake.random_int(min=1, max=3),
                idGestor=fake.random_int(min=1, max=100),
                idClienteIncidente=fake.random_int(min=1, max=1000),
                solucion=fake.sentence() if fake.boolean(chance_of_getting_true=50) else None
            )
            db.session.add(incidente)
        db.session.commit()

with app.app_context():
    db.create_all()
    poblar_base_de_datos(10)

initialize_routes(app)


@app.after_request
def after_hook(response):
    
    if not (request.path in['/metrics','/activar_fallos','/healthcheck']) :
        request_counter.labels(
            instance=f"GESTOR_INCIDENTES_{INSTANCE_TYPE}",
            path=request.path,
            method=request.method,
            status_code=response.status_code
        ).inc()
    
    response.headers['X-Host'] = INSTANCE_TYPE
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
