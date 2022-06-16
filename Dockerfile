# Use an official Python runtime as a parent image
FROM python:3.8

# Set environment varibles
ENV PYTHONUNBUFFERED 1

WORKDIR /code/

# Copy the current directory contents into the container at /code/
COPY Pipfile /code/
COPY Pipfile.lock /code/
# Set the working directory to /code/
RUN pip install --upgrade pip && pip install pipenv && pipenv install --skip-lock && pipenv install uvicorn[standart]
# Copy the current directory contents into the container at /code/
COPY . /code/
RUN echo -n > ..env
