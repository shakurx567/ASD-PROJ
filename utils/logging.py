# Student ID: 24000310
# Student Name: Mzamil Ahmed
# Component: Component 1 - Database Design & Project Infrastructure

import logging as log

log.basicConfig(
    filename="system.log",
    level=log.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message):
    log.info(message)

def log_error(message):
    log.error(message)