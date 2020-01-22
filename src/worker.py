#!/usr/bin/env python
import argparse
import logging
import pika

from cleaner import Tokenized
from settings import RABBITMQ_HOST, RABBITMQ_PORT

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Connector(object):
    def __init__(self, queue):
        self.logger = logger
        self.queue = queue
        credentials = pika.PlainCredentials('guest', 'guest')
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBITMQ_HOST,
                                      RABBITMQ_PORT,
                                      '/',
                                      credentials))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue, durable=True)
        self.logger.info(' Initializing Connector')

    def start_connector(self):
        def callback(ch, method, properties, body):
            Tokenized(body)
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
    logger.info(' Initializing worker')
    print("hey")
    init_worker(args.queue)
