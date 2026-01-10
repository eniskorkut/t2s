FROM python:3.10-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY vanna_config.py .
COPY init_db.py .
COPY app.py .

# Expose port
EXPOSE 8084

# Run the application
CMD ["python", "app.py"]
