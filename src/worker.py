#!/usr/bin/env python
import argparse
import logging
import json
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
    def __init__(self, queue):
        self.logger = logger
        self.logger.info("Connecting to rabbitmq: {}:{}".format(RABBITMQ_HOST,
                                                                RABBITMQ_PORT))
        self._reconnect_delay = 0
        self._amqp_url = 'amqp://{}:{}@localhost:5672/'.format(
            RABBITMQ_USER,
            RABBITMQ_PASSWORD,
            RABBITMQ_HOST,
            RABBITMQ_PORT
        )
        self._consumer = Consumer(self._amqp_url, queue, self._callback)
        self.logger.info("Connected to rabbitmq: {}:{}".format(RABBITMQ_HOST,
                                                               RABBITMQ_PORT))

    def __mongo_connection__(self):
        db = Mongo(
                    MONGO_DATABASE,
                    MONGO_HOST,
                    MONGO_PORT
                )
        self.logger.info("Connected to mongo: {}:{}".format(MONGO_HOST,
                                                            MONGO_PORT))
        return db

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

    def _callback(self, body):
        self.logger.info("Tokenizing")
        body_json = json.loads(body.decode('utf8'))
        self.logger.info(body_json.keys())
        if 'content' in body_json.keys():
            tokenized = Tokenized(body_json['content'])
            body_json['tokenized'] = tokenized.clean_text()
            self.logger.info("inserting in mongo")
            db = self.__mongo_connection__()
            db.insert_collection("default", body_json)
            self.logger.info(body)


def init_worker(queue):
    consumer = Connector(queue)
    consumer.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Init worker')
    parser.add_argument('queue', help='Queue to read messages')
    args = parser.parse_args()
    init_worker(args.queue)
