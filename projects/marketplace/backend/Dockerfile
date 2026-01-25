FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Railway provides PORT env var
ENV PORT=8000
EXPOSE 8000

# Start command - uses shell form to expand $PORT
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
