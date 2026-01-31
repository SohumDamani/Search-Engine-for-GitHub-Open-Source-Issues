FROM python:3.11-slim

WORKDIR /app

COPY data-collection/requirements.txt /app/data-collection/requirements.txt

RUN pip install --no-cache-dir -r /app/data-collection/requirements.txt

CMD ["tail", "-f", "/dev/null"]
