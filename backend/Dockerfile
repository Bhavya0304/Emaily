# Base image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["flask", "run", "--host=0.0.0.0","--port=80"]
