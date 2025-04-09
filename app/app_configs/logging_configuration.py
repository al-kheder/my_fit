from logging.config import dictConfig

from app.app_configs.environment_config import DevConfig,config


def configure_logging()->None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            'filters': {
                      'correlation_id': {
                            '()': 'asgi_correlation_id.CorrelationIdFilter',
                            'uuid_length':8 if isinstance(config,DevConfig) else 32,
                             'default_value': '-',
                        },
            },
            "formatters":{
                "console":{
                    "class":"logging.Formatter",
                    "datefmt":"%Y-%m-%d %H:%M:%S",
                    "format":"(%(correlation_id)s)  %(asctime)s || %(name)s:%(lineno)d || %(levelname)s || %(message)s",
                },
                "file":{
                    "class":"pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt":"%Y-%m-%d %H:%M:%S",
                    "format":"%(asctime)s %(name)s:%(lineno)d [%(correlation_id)s]  %(levelname)s %(message)s",
                }
            },
            "handlers":{
                "default":{
                    "class":"rich.logging.RichHandler",
                    "level":"DEBUG",
                    "formatter":"console",
                    "filters":["correlation_id"],
                },
                "rotating_file":{
                    "class":"logging.handlers.RotatingFileHandler",
                    "level":"DEBUG",
                    "formatter":"file",
                    "filename":"storeapi.log",
                    "maxBytes":1024*1024*5,
                    "backupCount":2,
                    "encoding":"utf-8",
                    "filters":["correlation_id"],
                },
            },
            "loggers":{
                "uvicorn":{
                    "handlers":["default","rotating_file"],
                    "level":"INFO",
                    "propagate":False,
                },
                "app":{
                    "handlers":["default","rotating_file"],
                    "level":"DEBUG" if isinstance(config,DevConfig) else "INFO",
                    "propagate":False,
                },
                "databases":{
                    "handlers":["default","rotating_file"],
                    "level":"WARNING" if isinstance(config,DevConfig) else "INFO",
                    "propagate":False,
                },
                "aiosqlite":{
                    "handlers":["default","rotating_file"],
                    "level":"WARNING" if isinstance(config,DevConfig) else "INFO",
                    "propagate":False,
                },
            },


        }
    )
