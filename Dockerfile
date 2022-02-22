#FROM tiangolo/meinheld-gunicorn-flask:python3.9
FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk --update add bash nano
#RUN apt update
#RUN apt install -y bash nano vim git 
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
ENV PARSE_SERVER_URL http://example.com/parse
ENV PARSE_SERVER_APLICATION_ID e0ef0e30-b8e6-11eb-8529-0242ac130003
ENV PARSE_SERVER_MASTER_KEY 32xb
COPY ./requirements.txt /var/www/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /var/www/requirements.txt
COPY ./ /app