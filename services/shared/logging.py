import logging
import json
import time

class StructuredJSONLogger(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "level": record.levelname,
            "service_name": getattr(record, "service_name", "lumo-microservice"),
            "message": record.getMessage()
        }
        return json.dumps(log_obj)
