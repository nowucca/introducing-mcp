# Use a standard Python image
FROM python:3.12

# Create app directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Make the run script executable
RUN chmod +x run.sh

# Run the server and client using our script
CMD ["./run.sh"]
