from utils.logging import get_logger

logger = get_logger(__name__)


def process_results(data: dict) -> None:
    """
    Process incoming webhook data.

    For now this just logs the payload. In a generated project you can replace
    this with your own business logic.
    """

    logger.info("Processing webhook data: %s", data)

