import json
import logging
import sys
from datetime import datetime, timezone

# Standard LogRecord attributes — everything else is caller-supplied extra fields.
_STDLIB_FIELDS = frozenset({
    "args", "created", "exc_info", "exc_text", "filename", "funcName",
    "levelname", "levelno", "lineno", "message", "module", "msecs", "msg",
    "name", "pathname", "process", "processName", "relativeCreated",
    "stack_info", "taskName", "thread", "threadName",
})


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        doc: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            doc["exception"] = self.formatException(record.exc_info)
        # Extra fields passed via logger.info(..., extra={...}) land as top-level
        # attributes on the LogRecord — not under a nested "extra" key.
        for key, val in record.__dict__.items():
            if key not in _STDLIB_FIELDS and not key.startswith("_"):
                doc[key] = val
        return json.dumps(doc)


def get_logger(service_name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(service_name)
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger
