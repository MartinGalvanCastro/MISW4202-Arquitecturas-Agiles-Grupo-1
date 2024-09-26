import enum
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


# Definir EstadoEnum usando el módulo `enum` de Python
class EstadoEnum(str, enum.Enum):
    ABIERTO = "Abierto"
    CERRADO = "Cerrado"
    EN_PROGRESO = "En Progreso"
    ESCALADO = "Escalado"


# Definir CanalEnum usando el módulo `enum` de Python
class CanalEnum(str, enum.Enum):
    TELEFONO = "Teléfono"
    CHAT = "Chat"
    EMAIL = "Email"
    APP = "App"


class Incidente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    canal = db.Column(db.Enum(CanalEnum), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.Enum(EstadoEnum), nullable=False)
    prioridad = db.Column(db.Integer, nullable=False)
    idGestor = db.Column(db.Integer, nullable=False)
    idClienteIncidente = db.Column(db.Integer, nullable=False)
    solucion = db.Column(db.String(200), nullable=True)
    detallesSolucion = db.Column(db.String(500), nullable=False)
    logsTecnicos = db.Column(db.Text, nullable=False)
    fechaIncidente = db.Column(db.DateTime, default=datetime.utcnow)


    modificaciones = db.relationship('HistorialModificaciones', backref='incidente', lazy=True)

    def __repr__(self):
        return f"<Incidente {self.descripcion}>"


class HistorialModificaciones(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idIncidente = db.Column(db.Integer, db.ForeignKey('incidente.id'), nullable=False)
    cambio = db.Column(db.String(200), nullable=False)
    fechaCambio = db.Column(db.DateTime, default=datetime.utcnow)
    idUsuario = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<HistorialModificaciones {self.cambio} en incidente {self.idIncidente}>"


class IncidenteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Incidente
        include_relationships = True
        load_instance = True

class HistorialModificacionesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = HistorialModificaciones
        include_relationships = True
        load_instance = True