FROM python:3.8.6-alpine
WORKDIR /code
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers
COPY dependencias.txt dependencias.txt
RUN pip install -r dependencias.txt
COPY . /code
CMD ["flask", "run"]
