# pull official base image
FROM python:3.10-slim

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all project files into container
# Copies everything into /usr/src/app
COPY . .