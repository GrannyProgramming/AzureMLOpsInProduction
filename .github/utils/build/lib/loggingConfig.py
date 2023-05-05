import logging

import logging

def setup_logging(log_file_path: str, level: str = "INFO") -> None:
    # Configure logging
    logging.basicConfig(
        filename=log_file_path,
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create a stream handler to output logs to the console
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console)

