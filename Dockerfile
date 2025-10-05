FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8080"]
