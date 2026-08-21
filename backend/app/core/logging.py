import logging


def configure_logging(level: str) -> None:
    """Configure concise process logging once the API lifespan starts."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
