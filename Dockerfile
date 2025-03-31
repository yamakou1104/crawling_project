# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app /app

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    curl wget \
    cmake \
    && apt-get clean

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pyngrok>=7.0.0

EXPOSE 80 5000

# デフォルトのコマンド
CMD ["python", "app.py"]
