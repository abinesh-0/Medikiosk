import logging
from pathlib import Path
def configure_logging(base_dir):
    Path(base_dir, "logs").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.FileHandler(Path(base_dir,"logs","medikiosk.log"), encoding="utf-8"),
                  logging.StreamHandler()]
    )
