#!/usr/bin/env python
import argparse
import logging
import json
import subprocess
from time import sleep

from async_consumer import Consumer
from cleaner import Tokenized
from mongo import Mongo
from settings import (
        RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD,
        MONGO_HOST, MONGO_PORT, MONGO_DATABASE)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Connector(object):
    __callback_dicts__ = {
        'text': '_callback_text',
        'pdf': '_callback_pdf'
    }

    def __init__(self, queue, text_type, pdf_separator):
        self.logger = logger
        self.pdf_separator = pdf_separator
        self.logger.info("Connecting to rabbitmq: {}:{}".format(RABBITMQ_HOST,
                                                                RABBITMQ_PORT))
        self._reconnect_delay = 0
        self._amqp_url = 'amqp://{}:{}@localhost:5672/'.format(
            RABBITMQ_USER,
            RABBITMQ_PASSWORD,
            RABBITMQ_HOST,
            RABBITMQ_PORT
        )
        self._consumer = Consumer(self._amqp_url,
                                  queue,
                                  getattr(self,
                                          self.__callback_dicts__[text_type]))
        self.logger.info("Connected to rabbitmq: {}:{}".format(RABBITMQ_HOST,
                                                               RABBITMQ_PORT))
        db = Mongo(
                    MONGO_DATABASE,
                    MONGO_HOST,
                    MONGO_PORT
                )
        self.db = db
        self.logger.info("Connected to mongo: {}:{}".format(MONGO_HOST,
                                                            MONGO_PORT))

    def run(self):
        while True:
            try:
                self._consumer.run()
            except KeyboardInterrupt:
                self._consumer.stop()
                break
            self._maybe_reconnect()

    def _maybe_reconnect(self):
        if self._consumer.should_reconnect:
            self._consumer.stop()
            reconnect_delay = self._get_reconnect_delay()
            self.logger.info('Reconnecting after %d seconds', reconnect_delay)
            sleep(reconnect_delay)
            self._consumer = Consumer(self._amqp_url)

    def _get_reconnect_delay(self):
        if self._consumer.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay

    def _callback_text(self, body):
        self.logger.info("Tokenizing")
        body_json = json.loads(body.decode('utf8'))
        self.logger.info(body_json.keys())
        if 'content' in body_json.keys():
            tokenized = Tokenized(body_json['content'])
            body_json['tokenized'] = []
            body_json['tokenized'].append(tokenized.clean_text())
            self.logger.info("inserting in mongo")
            self.db.insert_collection("default", body_json)
            self.logger.info(body)

    def _callback_pdf(self, body):
        self.logger.info("Tokenizing")
        body_json = json.loads(body.decode('utf8'))
        self.logger.info(body_json.keys())
        if 'file_path' in body_json.keys():
            content = subprocess.run(['pdftotext', body_json['file_path'], '-'],
                                     stdout=subprocess.PIPE)
            body_json['content'] = str(content.stdout, 'utf-8')\
                .replace('\n ', '').replace('\n', ' ')

            text = body_json['content'].split(self.pdf_separator)
            body_json['tokenized'] = []
            for paragraph in text:
                tokenized = Tokenized(paragraph)
                body_json['tokenized'].append(tokenized.clean_text())
            self.logger.info("inserting in mongo")
            self.db.insert_collection("pdfs", body_json)
            self.logger.info(body)


def init_worker(queue, text_type, pdf_separator):
    consumer = Connector(queue, text_type, pdf_separator)
    consumer.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Init worker')
    parser.add_argument('queue', help='Queue to read messages')
    parser.add_argument('--text-type', help='Type of text to tokenize',
                        default='text')
    parser.add_argument('--pdf_separator', help='PDF paragraph text separator',
                        default='  \x0c')
    args = parser.parse_args()
    init_worker(args.queue, args.text_type, args.pdf_separator)
