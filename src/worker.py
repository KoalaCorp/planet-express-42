#!/usr/bin/env python
import argparse
import pika


class Connector(object):
    def __init__(self, queue):
        self.queue = queue
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue, durable=True)

    def start_connector(self):
        def callback(ch, method, properties, body):
            print(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
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
