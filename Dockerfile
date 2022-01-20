FROM python:3.10.2

RUN pip install flask-restx

WORKDIR /app

COPY . /app/

ENTRYPOINT ["python", "app.py"]
