FROM python:3.10-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY vanna_config.py .
COPY init_db.py .
COPY main.py .
COPY custom_auth.py .
COPY services/ ./services/
COPY templates/ ./templates/
COPY api/ ./api/
COPY models/ ./models/

# Expose port
EXPOSE 8084

# Run the application with uvicorn (unbuffered output)
CMD ["python", "-u", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8084"]
