FROM python:3.11-alpine

WORKDIR /app

COPY . /app

VOLUME [ "/app/data" ]

RUN pip install -r requirements.txt

EXPOSE 5005

CMD ["python", "auth.py"]
