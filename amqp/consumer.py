import asyncio
import aiormq
import time


host = "103.47.210.242"
port = 25672
username = "guest"
password = "guest"

routing_key = "hello"


def on_message(message):
    """
    on_message doesn't necessarily have to be defined as async.
    Here it is to show that it's possible.
    """
    print(f" [x] Received message {message!r}")
    print(f"Message body is: {message.body!r}")
    print("Before sleep!")
    time.sleep(1)
      # Represents async I/O operations
    print("After sleep!")


class LevinConsumer:

    def __init__(
            self,
            host: str = "localhost",
            port: int = 25672,
            username: str = "guest",
            password: str = "guest",
            routing: str = "hello") -> None:

        self.uri = f"amqp://{username}:{password}@{host}:{port}//"
        self.routing = routing

    async def init(self, callback):
        # Perform connection
        connection = await aiormq.connect(self.uri)

        # Creating a channel
        channel = await connection.channel()

        # Declaring queue
        declare_ok = await channel.queue_declare(self.routing)

        await channel.basic_consume(
            # declare_ok.queue, callback, no_ack=True
            self.routing, callback
        )


async def main():

    consumer = LevinConsumer(host, port, username, password)
    await consumer.init(on_message)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
