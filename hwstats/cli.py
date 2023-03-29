import asyncio
import logging

from hwstats.frontend import start_app
from hwstats.log_config import configure_logging
from hwstats.monitor import start_metrics_collection


async def main():
    """Start the app and start collecting metrics"""
    await start_metrics_collection()
    await start_app()
    # await asyncio.gather(start_app(), start_metrics_collection())


if __name__ == "__main__":
    configure_logging()
    logger = logging.getLogger("hwstats")
    logger.info("Starting the Hardware Stats monitoring application")

    asyncio.run(main())
