#!/usr/bin/env python
import argparse
import logging
import json
import pika

from cleaner import Tokenized
from mongo import Mongo
from settings import (
        RABBITMQ_HOST, RABBITMQ_PORT, MONGO_HOST,
        MONGO_PORT, MONGO_DATABASE)


# create logger
logger = logging.getLogger('main_logger')
logger.setLevel(logging.DEBUG)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Connector(object):
    def __init__(self, queue):
        self.logger = logger
        self.logger.info("Connecting to rabbitmq: {}:{}".format(RABBITMQ_HOST,
                                                                RABBITMQ_PORT))
        self.queue = queue
        credentials = pika.PlainCredentials('guest', 'guest')
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBITMQ_HOST,
                                      RABBITMQ_PORT,
                                      '/',
                                      credentials))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue, durable=True)
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

    def start_connector(self):
        def callback(ch, method, properties, body):
            self.logger.info("Tokenizing")
            tokenized = Tokenized(body)
            self.logger.info("inserting in mongo")
            db = self.__mongo_connection__()
            db.insert_collection("default", json.loads(body.decode('utf8')))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            self.logger.info(body)
        self.logger.info('Starting Connector')
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(callback, queue=self.queue)
        self.channel.start_consuming()


def init_worker(queue):
    connector = Connector(queue)
    connector.start_connector()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Init worker')
    parser.add_argument('queue', help='Queue to read messages')
    args = parser.parse_args()
    init_worker(args.queue)
