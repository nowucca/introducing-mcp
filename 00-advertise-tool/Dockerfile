# Use a standard Python image
FROM python:3.12

# Create app directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install dos2unix to handle line endings
RUN apt-get update && apt-get install -y dos2unix

# Convert shell scripts from CRLF to LF (if needed)
RUN find . -type f -name "*.sh" -exec dos2unix {} \;

# Make the run script executable
RUN chmod +x run.sh

# Run the server and client using our script
CMD ["bash", "./run.sh"]
