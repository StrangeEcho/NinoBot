import asyncio
import os

from core.nino import NinoBot
from rich.traceback import install


async def main():
    bot = NinoBot()
    try:
        await bot.startup()
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    install()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
