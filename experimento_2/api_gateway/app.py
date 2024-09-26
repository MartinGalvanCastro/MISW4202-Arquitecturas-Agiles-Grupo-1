from flask import Flask, request, Response
import requests
import hashlib
from prometheus_client import Counter
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

PRINCIPAL_URL = "http://tampering:5000"
AUTH_URL = "http://auth:5000"

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')

request_counter = Counter(
    'experimento_2_data', 'Total HTTP Requests',
    ['instance', 'path', 'method', 'status_code']
)

def calculate_hash(data):
    return hashlib.sha256(data).hexdigest()

@app.after_request
def registrar_errores(response):
    if not (request.path in ['/metrics', '/healthcheck']):
        request_counter.labels(
            instance=f"API GATEWAY",
            path=request.path,
            method=request.method,
            status_code=response.status_code
        ).inc()
    return response

def forward_request(url, endpoint, hash_value=None):
    headers = dict(request.headers)
    if hash_value:
        headers['X-Body-Hash'] = hash_value

    return requests.request(
        method=request.method,
        url=f"{url}{endpoint}",
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

@app.route('/login', methods=["POST"])
def login():
    response = forward_request(AUTH_URL, '/login')
    return Response(response.content, status=response.status_code, headers=dict(response.headers))


@app.route('/<path:endpoint>', methods=["GET", "POST", "PUT", "DELETE"])
def api_gateway(endpoint):
    data = request.get_data()
    hash_value = None

    if request.method in ['POST', 'PUT']:
        hash_value = calculate_hash(data)

    response = forward_request(PRINCIPAL_URL, f"/{endpoint}", hash_value=hash_value)
    return Response(response.content, status=response.status_code, headers=dict(response.headers))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
