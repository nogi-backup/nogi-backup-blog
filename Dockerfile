FROM python:3.8-buster

WORKDIR /app
COPY nogi/ /app/nogi
COPY blog.py /app/blog.py
COPY blog.sh /app/blog.sh
COPY requirement.txt /app

RUN pip install -r requirement.txt