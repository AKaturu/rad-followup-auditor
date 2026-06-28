FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgtk-3-0 libgdk-pixbuf2.0-0 libpango-1.0-0 libpangocairo-1.0-0 \
    libcairo2 libgdk-pixbuf2.0-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir ".[app]"

EXPOSE 8501
ENTRYPOINT ["rad-followup-auditor"]
CMD ["serve"]
