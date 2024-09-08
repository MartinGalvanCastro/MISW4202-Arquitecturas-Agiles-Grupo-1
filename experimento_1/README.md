## Video Resultados:

https://youtu.be/wP9S90autjY

## Como correr:

### Requerimientos:
  - Docker & Docker-Compose

### Instrucciones:
 1. Activar Docker si es requerido (En windows, es necesario abrir Docker Desktop)
 2. Ejecutar el comando:
```bash
docker-compose up -d
``` 
 3. En caso de que se requiera simular una falla, se debe hacer el siguiente request
```bash
curl -X POST http://127.0.0.1:5001/activar_fallos \
-H "Content-Type: application/json" \
-d '{"activar":true}'
``` 

### Detalles Aplicacion:
- API Gateway:
  - Desplegado en: http://127.0.0.1:5000
  - Endpoints disponibles:
    - `GET /incidentes`
- Gestor Incidentes Principal:
  - Desplegado en: http://127.0.0.1:5001
  - Endpoints disponibles:
    - `GET /incidentes`
    - `POST /activar_fallos`
- Gestor Incidentes Redundante
  - Desplegado en: http://127.0.0.1:5002
  - Endpoints disponibles:
    - `GET /incidentes`
- Prometheus
  - Desplegado en: http://127.0.0.1:9090
- Grafana
  - Desplegado en: http://127.0.0.1:3000
