FROM python:3.6.2-slim

ENV RABBITMQ_HOST localhost
ENV RABBITMQ_PORT 5672

ADD requirements.txt /worker/requirements.txt
RUN pip install -r /worker/requirements.txt
ADD src /worker

RUN python -m nltk.downloader punkt
CMD cd /worker && python worker.py elfarodeceuta
