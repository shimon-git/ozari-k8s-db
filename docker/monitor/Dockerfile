# Use Python 3.9 as base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy only the Python script (config will be mounted at runtime)
COPY main.py /app/

# Install required Python packages
RUN pip install flask pyyaml

# Start the listener
CMD ["python", "main.py"]

