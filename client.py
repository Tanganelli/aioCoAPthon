import asyncio
import logging.config

from aiocoapthon.client.coap_client import CoAPClient

__author__ = 'Giacomo Tanganelli'


if __name__ == "__main__":  # pragma: no cover

    def mine_callback(response):
        print(response)
        return True

    async def consumer(queue, stop):
        while True:
            response = await queue.get()
            queue.task_done()
            print(response)

    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
    logger = logging.getLogger(__name__)

    loop = asyncio.get_event_loop()
    client = CoAPClient("127.0.0.1", 5683)
    future = loop.run_until_complete(client.get("/basic"))
    print("Result: " + str(future))

    # future = loop.run_until_complete(client.observe("/basic", callback=mine_callback, timeout=60))
    # print("Result: " + str(future.result()))
    queue = asyncio.Queue()
    event = asyncio.Event()
    loop.create_task(consumer(queue, event))
    try:
        future = loop.run_until_complete(client.observe("/basic", queue=queue, stop=event, timeout=60))
        print("Result: " + str(future.result()))
    except KeyboardInterrupt:
        pass
