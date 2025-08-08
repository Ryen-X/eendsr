import logging
import logging.config
import yaml
from pathlib import Path

def setup_logging():
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "settings.yaml"
    
    if not config_path.exists():
        logging.basicConfig(level=logging.INFO)
        logging.warning(f"Warning: Logging configuration file not found at {config_path}. Using basic config.")
        return

    with open(config_path, 'rt') as f:
        try:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config['logging'])
            logging.getLogger(__name__).info("Logging configured successfully.")
        except Exception as e:
            logging.basicConfig(level=logging.INFO)
            logging.warning(f"Error loading logging configuration: {e}. Using basic config.")