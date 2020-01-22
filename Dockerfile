FROM python:3.6.2-slim

ENV RABBITMQ_HOST rabbitmq
ENV RABBITMQ_PORT 5672
ENV RABBITMQ_QUEUE items

ADD requirements.txt /worker/requirements.txt
RUN pip install -r /worker/requirements.txt
ADD src /worker

RUN python -m nltk.downloader punkt
