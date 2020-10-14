FROM python:3.6.2-slim

ENV RABBITMQ_HOST rabbitmq
ENV MONGO_HOST mongo

ADD requirements.txt /worker/requirements.txt
RUN pip install -r /worker/requirements.txt
ADD src /worker

RUN python -m spacy download es_core_news_md
