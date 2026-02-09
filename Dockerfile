FROM python:3.11-slim

WORKDIR /app

COPY dataCollection/requirements.txt /app/dataCollection/requirements.txt
COPY indexing/requirements.txt /app/indexing/requirements.txt

RUN pip install --no-cache-dir -r /app/dataCollection/requirements.txt
RUN pip install --no-cache-dir -r /app/indexing/requirements.txt

CMD ["tail", "-f", "/dev/null"]
