FROM python:3.11

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m camoufox fetch
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn octofiestaspotifyapi.api:app --host 0.0.0.0 --port ${API_CONTAINER_PORT:-8000}"]