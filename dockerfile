# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Install dependencies needed for building Python packages
RUN apk add --no-cache build-base libffi-dev

# Create and set the working directory
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app-multi.py app.py

# Copy the quizzes
COPY quizzes quizzes

# Copy the templates
COPY templates templates

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run gunicorn when the container launches
CMD ["gunicorn", "-b", ":5000", "app:app"]