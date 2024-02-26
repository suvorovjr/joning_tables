FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/

RUN pip3 install -r requirements.txt

COPY . /code/

EXPOSE 5000