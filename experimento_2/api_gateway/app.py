from flask import Flask, request, Response
import requests
import time
import random
from prometheus_client import Counter
from prometheus_flask_exporter import PrometheusMetrics
from collections import deque
import sys
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

PRINCIPAL_URL = "http://gestor_incidentes_principal:5000"
RESPALDO_URL = "http://gestor_incidentes_respaldo:5000"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1281068075193602168/FTs79VIrR7CYzHBbyjWezhNWJVS6DvxWrG3W0gXMay3aou0lNOUrHR64iMKSku0g0rEL"
sys.stdout.reconfigure(line_buffering=True)


error_timestamps = {
    "principal": deque(),
    "respaldo": deque()
}

THRESHOLD = 40
WINDOW_SIZE = 60


def generar_mensaje(instancia: str):
    embed = {
        "description": "Alerta de errores",
        "title": f"Error en la instancia ${instancia}"
    }

    data = {
        "content": f"Se detectaron mas de 40 errores por min en ${instancia}",
        "embeds": [
            embed
        ],
    }

    headers = {
        "Content-Type": "application/json"
    }

    return data, headers


metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')

request_counter = Counter(
    'experimento_1_data', 'Total HTTP Requests',
    ['instance', 'path', 'method', 'status_code']
)


@app.route('/healthcheck', methods=['GET'])
def gateway_healthcheck():
    results = {}
    try:
        response = requests.get(f"{PRINCIPAL_URL}/healthcheck")
        if response.status_code == 200:
            results['gestor_incidentes_principal'] = response.json().get('status', 'UNKNOWN')
        else:
            results['gestor_incidentes_principal'] = 'UNREACHABLE'
    except requests.exceptions.RequestException:
        results['gestor_incidentes_principal'] = 'UNREACHABLE'

    try:
        response = requests.get(f"{RESPALDO_URL}/healthcheck")
        if response.status_code == 200:
            results['gestor_incidentes_respaldo'] = response.json().get('status', 'UNKNOWN')
        else:
            results['gestor_incidentes_respaldo'] = 'UNREACHABLE'
    except requests.exceptions.RequestException:
        results['gestor_incidentes_respaldo'] = 'UNREACHABLE'

    return results, 200


@app.after_request
def registrar_errores(response):

    if not (request.path in ['/metrics', '/healthcheck']):
        request_counter.labels(
            instance=f"API GATEWAY",
            path=request.path,
            method=request.method,
            status_code=response.status_code
        ).inc()

    if response.status_code >= 500:
        host = response.headers.get('X-Host')
        app.logger.info(f'Se registro una falla en la instancia para la instancia {host}')
        registrar_error(host)

    return response


def registrar_error(instancia):
    now = time.time()
    error_timestamps[instancia].append(now)

    while error_timestamps[instancia] and now - error_timestamps[instancia][0] > WINDOW_SIZE:
        error_timestamps[instancia].popleft()

    app.logger.info(f'Se tienen estos errores por minuto: {len(error_timestamps[instancia])}')

    if len(error_timestamps[instancia]) >= THRESHOLD:
        app.logger.info(f'Se va a enviar la alerta a Discord para la instancia {instancia}')
        enviar_alerta(instancia)


ultimo_envio=None
def enviar_alerta(instancia):
    global ultimo_envio
    if not ultimo_envio:
        ultimo_envio = time.time()
    elif time.time() - ultimo_envio < 60*2:
        return
    try:

        data, headers = generar_mensaje(instancia)
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, headers=headers)
        app.logger.info(f"Alerta enviada para {instancia}. Respuesta: {response.status_code}")

        if response.status_code != 200:
            app.logger.error(f"Error en la respuesta del webhook: {response.status_code}, {response.text}")
    except Exception as e:
        app.logger.error(f"Error enviando alerta: {e}")


def forward_request(url, endpoint):
    return requests.request(
        method=request.method,
        url=f"{url}{endpoint}",
        headers=request.headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )


@app.route('/<path:endpoint>', methods=["GET", "POST", "PUT", "DELETE"])
def api_gateway(endpoint):
    response = None
    if random.choice([True, False]):
        response = forward_request(PRINCIPAL_URL, f"/{endpoint}")
    else:
        response = forward_request(RESPALDO_URL, f"/{endpoint}")
    return Response(response.content, status=response.status_code, headers=dict(response.headers))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
