import logging


def configure_logging():
    """Configure logging for the entire application"""
    # Define a console handler that logs messages to the terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Define a file handler that logs messages to a file
    file_handler = logging.FileHandler("hwstats.log", mode="w")
    file_handler.setLevel(logging.INFO)

    # Configure the root logger
    logging.basicConfig(
        level=logging.DEBUG,
        # format = '%(asctime)s [%(name)s:%(lineno)d] %(levelname)s: %(message)s',
        style="{",
        format="{asctime} [{name}:{lineno}] {levelname}: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[console_handler, file_handler],
    )
