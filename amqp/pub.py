import base64
from io import BytesIO

import asyncio
import aiormq
from PIL import Image


host = "103.47.210.242"
port = 25672
username = "guest"
password = "guest"
exchange = "logs"
routing_key = "hello"


class LevinPub():

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
        self.connection = await aiormq.connect(self.uri)

        # Creating a channel
        self.channel = await self.connection.channel()

        await self.channel.exchange_declare(
            exchange=self.exchange, exchange_type='fanout'
        )

    async def send_message(self, message: str, routing: str = "hello"):

        body = str.encode(message)

        # Sending the message
        await self.channel.basic_publish(
            body, routing_key=routing, exchange=self.exchange
        )

        print(f" [x] Sent {body!r}")


async def main():
    pub = LevinPub(host, port, username, password, exchange)
    await pub.init()

    image = Image.open("resources/asrul.png").convert("RGB")

    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    img_str = img_str.decode()

    # count = 0
    # while True:
    #     if count == 10:
    #         break
    #     await pub.send_message(f"JANCOK yang ke: {count}", routing_key)

    #     count += 1

    await pub.send_message(img_str, routing_key)

    await pub.connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
