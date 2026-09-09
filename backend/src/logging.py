import structlog
from contextvars import ContextVar
from uuid import uuid4

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

def configure_structlog():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger("INFO"),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

def get_logger():
    return structlog.get_logger()

def set_request_id(request_id: str | None = None) -> str:
    if request_id is None:
        request_id = str(uuid4())
    request_id_var.set(request_id)
    return request_id

def get_request_id() -> str:
    return request_id_var.get()