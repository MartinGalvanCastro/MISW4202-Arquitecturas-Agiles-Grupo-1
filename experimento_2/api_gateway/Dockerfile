FROM python:3.10


RUN apt update && apt install -y curl

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


EXPOSE 5000


CMD ["flask", "run", "--host=0.0.0.0"]
