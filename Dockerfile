FROM python:3.11-slim

WORKDIR /app

# Install dependencies defined in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Run the cron job directly according to the render dockerCommand
CMD ["python", "main.py"]
