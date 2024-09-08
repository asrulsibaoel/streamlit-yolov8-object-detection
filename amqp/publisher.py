import asyncio
from typing import Optional

import aiormq
from aiormq.abc import DeliveredMessage

host = "103.47.210.242"
port = 25672
username = "guest"
password = "guest"

routing_key = "hello"


class LevinPublisher():

    def __init__(
            self,
            host: str = "localhost",
            port: int = 25672,
            username: str = "guest",
            password: str = "guest",
            routing: str = "hello") -> None:

        self.uri = f"amqp://{username}:{password}@{host}:{port}//"
        self.routing = routing

    async def init(self):
        # Perform connection
        connection = await aiormq.connect(self.uri)

        # Creating a channel
        self.channel = await connection.channel()

        # self.declare_ok = await self.channel.queue_declare(self.routing, auto_delete=True)

    async def send_message(self, message: str) -> None:

        # Sending the message
        await self.channel.basic_publish(str.encode(message))
        print(f" [x] Sent {message}")

        # response = await self.channel.basic_get(self.declare_ok.queue)
        # print(f" [x] Received message from {self.declare_ok.queue!r}")
        # print(response)


async def main():
    publisher = LevinPublisher(host, port, username, password, routing_key)
    await publisher.init()

    message = " Haha Hihihi yang ke: "

    count = 0
    while count < 10:
        await publisher.send_message(message=message + str(count))
        count += 1


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
