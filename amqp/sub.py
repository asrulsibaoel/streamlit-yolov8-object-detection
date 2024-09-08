import asyncio
import aiormq
import aiormq.abc


host = "103.47.210.242"
port = 25672
username = "guest"
password = "guest"
exchange = "logs"
routing_key = "hello"


async def on_message(message: aiormq.abc.DeliveredMessage):
    print(f"[x] {message.body!r}")

    await message.channel.basic_ack(
        message.delivery.delivery_tag
    )


class LevinSub:

    def __init__(
            self,
            host: str = "localhost",
            port: int = 25672,
            username: str = "guest",
            password: str = "guest",
            exchange: str = "logs") -> None:
        self.uri = f"amqp://{username}:{password}@{host}:{port}/"
        self.exchange = exchange

    async def init(self):
        # Perform connection
        connection = await aiormq.connect(self.uri)

        # Creating a channel
        self.channel = await connection.channel()
        await self.channel.basic_qos(prefetch_count=1)

        await self.channel.exchange_declare(
            exchange=self.exchange, exchange_type='fanout'
        )

        # Declaring queue
        await self.channel.queue_declare(exclusive=True)

    async def consume(self, callback, routing: str = "hello"):

        # Binding the queue to the exchange
        await self.channel.queue_bind(routing, self.exchange)

        # Start listening the queue with name 'task_queue'
        await self.channel.basic_consume(routing, callback)


async def main():
    sub = LevinSub(host, port, username, password, exchange)
    await sub.init()
    await sub.consume(on_message, routing_key)


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.create_task(main())

    # we enter a never-ending loop that waits for data
    # and runs callbacks whenever necessary.
    print(' [*] Waiting for logs. To exit press CTRL+C')
    loop.run_forever()
