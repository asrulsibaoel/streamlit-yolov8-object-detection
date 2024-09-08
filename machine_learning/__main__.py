import asyncio


async def run():
    print("cok")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run())

    # we enter a never-ending loop that waits for data
    # and runs callbacks whenever necessary.
    # print(' [*] Waiting for logs. To exit press CTRL+C')
    loop.run_forever()
