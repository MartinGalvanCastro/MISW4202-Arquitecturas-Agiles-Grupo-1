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

 3. Iniciar sesion, (El JWT va como encabezado de la respuesta)
```bash
curl -X POST http://127.0.0.1:5000/login \
-H "Content-Type: application/json" \
-d '{"username":usuario, "password":password}'
``` 

``` 
 4. En caso de que se requiera simular un ataque de tampering
```bash
curl -X POST http://127.0.0.1:5000/tampering 
``` 

### Detalles Aplicacion:
- API Gateway:
  - Desplegado en: http://127.0.0.1:5000
  - Endpoints disponibles:
    - `GET /incidentes`
    - `POST /incidentes`
    - `PUT /incidentes/{id}`
    - `DELETE /incidentes/{id}`
    - `GET /incidentes/{id}`
    - `GET /incidentes/{id}/histoiral`
    - `POST /login`
