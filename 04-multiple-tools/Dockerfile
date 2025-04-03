FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Install dos2unix to handle line endings
RUN apt-get update && apt-get install -y dos2unix

# Convert shell scripts from CRLF to LF (if needed)
RUN find . -type f -name "*.sh" -exec dos2unix {} \;

# Make run scripts executable
RUN chmod +x run.sh

# Default command
CMD ["bash", "./run.sh"]
