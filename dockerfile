# syntax=docker/dockerfile:1

FROM python:3.9.5-slim-buster
#FROM tiangolo/uwsgi-nginx-flask:python3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#ENV PATH="/scripts:${PATH}"
WORKDIR /sar2python

RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
# packages required for setting up WSGI
RUN apt-get update
RUN apt-get install -y gcc libc-dev python3-dev


COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /sar2python

#CMD [ "./startWeb" ]
ENTRYPOINT ["./startWeb"]
