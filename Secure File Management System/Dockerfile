# Use an official Python runtime as a parent image (slim version for efficiency)
FROM python:3.11-slim

# Prevent Python from writing .pyc files to container disk
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent Python from buffering stdout and stderr (helps with Docker logs)
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's build caching
COPY requirements.txt /app/

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . /app/

# Make sure the static/uploads folder exists for local fallback storage
RUN mkdir -p /app/static/uploads

# Expose port 5000 (standard Flask port)
EXPOSE 5000

# Run the application using gunicorn for a production-ready server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
