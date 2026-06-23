FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY unifi_air_exporter ./unifi_air_exporter

RUN useradd --create-home --uid 1000 exporter
USER exporter

EXPOSE 9840

CMD ["python", "-m", "unifi_air_exporter.main"]
