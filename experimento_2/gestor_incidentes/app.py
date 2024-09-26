from flask import Flask, request
from models import db, Incidente, HistorialModificaciones
from api import initialize_routes
from faker import Faker
from flask_jwt_extended import JWTManager

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///incidentes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db.init_app(app)
fake = Faker()



def registrar_modificacion(incidente_id, cambio, idUsuario):
    nueva_modificacion = HistorialModificaciones(
        idIncidente=incidente_id,
        cambio=cambio,
        idUsuario=idUsuario
    )
    db.session.add(nueva_modificacion)
    db.session.commit()


def poblar_base_de_datos(cantidad=10):
    if Incidente.query.count() == 0:
        for _ in range(cantidad):
            incidente = Incidente(
                canal=fake.random_element(elements=('Email', 'Chat', 'Teléfono')),
                descripcion=fake.sentence(),
                estado=fake.random_element(elements=('ABIERTO', 'CERRADO', 'EN_PROGRESO', 'ESCALADO')),
                prioridad=fake.random_int(min=1, max=3),
                idGestor=fake.random_int(min=1, max=100),
                idClienteIncidente=fake.random_int(min=1, max=1000),
                solucion=fake.sentence() if fake.boolean(chance_of_getting_true=50) else None,
                detallesSolucion=fake.text(max_nb_chars=200),
                logsTecnicos=fake.text(max_nb_chars=500),
                fechaIncidente=fake.date_time_this_year()
            )
            db.session.add(incidente)
            db.session.commit()

            registrar_modificacion(incidente.id, "Incidente creado", incidente.idGestor)
            registrar_modificacion(incidente.id, "Estado cambiado a En Progreso", incidente.idGestor)
            registrar_modificacion(incidente.id, "Prioridad actualizada", incidente.idGestor)


with app.app_context():
    db.create_all()
    poblar_base_de_datos(10)

initialize_routes(app)
jwt = JWTManager(app)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
