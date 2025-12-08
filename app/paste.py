# Use a lightweight Python base image
FROM python:3.10-slim

# Prevent Python from writing .pyc files & using output buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Install system dependencies (if you need pandas, pillow, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code (including .env)
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Default environment (can be overridden at runtime)
ENV HOST=0.0.0.0
ENV PORT=8000


from fastapi import Request

LB_PREFIX = "/asr-benchmarking"

@app.middleware("http")
async def strip_lb_prefix(request: Request, call_next):
    path = request.scope.get("path", "")
    if path.startswith(LB_PREFIX):
        request.scope["path"] = path[len(LB_PREFIX):] or "/"
    return await call_next(request)
# Start the app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
