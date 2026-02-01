FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libatomic1 \
    openssl \
    ca-certificates \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g prisma \
    && rm -rf /var/lib/apt/lists/*
    
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Copy application code
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY core/ ./core/
COPY src/ ./src/
COPY main.py .
COPY services/ ./services/
COPY templates/ ./templates/
COPY api/ ./api/
COPY models/ ./models/
COPY prisma/ ./prisma/

# Generate Prisma Client
RUN prisma generate

# Expose port
EXPOSE 8084

# Run the application with uvicorn (unbuffered output)
CMD ["python", "-u", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8084"]
