FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Swiss Ephemeris data files: mount at runtime or bake in under /app/ephe
ENV SE_EPHE_PATH=/app/ephe
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
