from flask import Flask, request, Response
import requests
from faker import Faker
import json

app = Flask(__name__)

PRINCIPAL_URL = "http://gestor_incidentes_principal:5000"
tampering_activated = False
fake = Faker()

@app.route('/tampering', methods=["POST"])
def toggle_tampering():
    global tampering_activated
    tampering_activated = not tampering_activated
    status = "activated" if tampering_activated else "deactivated"
    return Response(f"Tampering {status}", status=200)

@app.route('/<path:endpoint>', methods=["GET", "POST", "PUT", "DELETE"])
def tampering_forwarding(endpoint):
    global tampering_activated

    data = request.get_data()
    if tampering_activated and data:
        data = tamper_data(data)

    response = requests.request(
        method=request.method,
        url=f"{PRINCIPAL_URL}/{endpoint}",
        headers=request.headers,
        data=data,
        cookies=request.cookies,
        allow_redirects=False
    )

    return Response(response.content, status=response.status_code, headers=dict(response.headers))

def tamper_data(data):
    try:
        json_data = json.loads(data)
        json_data["descripcion"] = fake.sentence()  # Modificamos el campo "descripcion" con un valor aleatorio
        tampered_data = json.dumps(json_data)
        return tampered_data.encode('utf-8')
    except (ValueError, KeyError):
        return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
