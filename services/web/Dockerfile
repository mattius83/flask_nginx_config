# pull official base image
FROM python:3.8.1-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update \
  && apt-get install poppler-utils -y \
  && apt-get install tesseract-ocr -y

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app

# These are the new lines for gunicorn
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "manage"]
