import random
random.seed(42)

from linkprediction.application_logger import set_up_logging
from linkprediction.webserver import run_webserver

if __name__ == "__main__":
    set_up_logging(
        debug_level='ERROR',
        log_to_console=True,
        log_header_config={
            'LOGINFO': 'This Log file serves as an error debug basis for this application'
        }
    )
    run_webserver()
