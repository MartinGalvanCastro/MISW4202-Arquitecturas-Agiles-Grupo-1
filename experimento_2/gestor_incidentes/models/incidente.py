from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


class Incidente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    canal = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    prioridad = db.Column(db.Integer, nullable=False)
    idGestor = db.Column(db.Integer, nullable=False)
    idClienteIncidente = db.Column(db.Integer, nullable=False)
    solucion = db.Column(db.String(200), nullable=True)
    fechaIncidente = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Incidente {self.descripcion}>"


class IncidenteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Incidente
        include_relationships = False
        load_instance = True

    fechaIncidente = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
