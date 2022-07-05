import os
import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger
# Override the built-in werkzeug logging function in order to change the log line format.
from werkzeug.serving import WSGIRequestHandler
from werkzeug.urls import uri_to_iri
werkzeug_logger = logging.getLogger('werkzeug')

# Load all configuration from environment. You need to run 'source setup.sh' unix command to load environ variables.
CONFIG = {
    "console_log": os.getenv("CONSOLE_LOG", "enable"),
    "log_json": os.getenv("LOG_JSON", "enable"),
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "log_file": os.getenv("LOG_FILE", "output.json"),
    "log_appname": os.getenv("LOG_APPNAME", "test-app")
}
logger = logging.getLogger('root')


def log_request(self, code="-", size="-"):
    try:
        path = uri_to_iri(self.path)
        msg = f"{self.command} {path} {self.request_version}"
    except AttributeError:
        msg = self.requestline
    code = str(code)
    if path and 'ready' in path:
        return
    else:
        self.log("info", '"%s" %s %s', msg, code, size)


WSGIRequestHandler.log_request = log_request
WSGIRequestHandler.log = lambda self, type, message, *args: \
    getattr(werkzeug_logger, type)("{} - - [] {}".format(self.address_string(), message.replace('"', '\'')), *args,)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['appname'] = CONFIG['log_appname']
        if not log_record.get('@timestamp'):
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['@timestamp'] = now


# Create logs file with names track the package/module hierarchy.
def configure_logging():
    # Setup format for FILE logs handler and Console logs handler.
    if CONFIG['log_json'] == 'enable':
        formatter = CustomJsonFormatter('%(@timestamp)%(levelname)%(threadName)%(message)')
    else:
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    # Console output if it's enable on CONFIG
    if CONFIG['console_log'] == 'enable':
        console_handler = logging.StreamHandler()
        if CONFIG['log_level'] == 'WARN':
            console_handler.setLevel(logging.WARNING)
            logger.setLevel(logging.WARNING)
        elif CONFIG['log_level'] == 'DEBUG':
            console_handler.setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.INFO)
            logger.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        werkzeug_logger.addHandler(console_handler)
        return console_handler
    else:
        file_handler = logging.FileHandler(CONFIG['log_file'], encoding="utf-8")
        if CONFIG['log_level'] == 'WARN':
            file_handler.setLevel(logging.WARNING)
            logger.setLevel(logging.WARNING)
        if CONFIG['log_level'] == 'DEBUG':
            file_handler.setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        else:
            file_handler.setLevel(logging.INFO)
            logger.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        werkzeug_logger.addHandler(file_handler)
        return file_handler


# Trigger self config
logger.addHandler(configure_logging())
