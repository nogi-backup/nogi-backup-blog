FROM python:3.8-buster

WORKDIR /app
COPY nogi/ /app/nogi
COPY blog.* .
COPY requirement.txt .

RUN pip install -r requirement.txt