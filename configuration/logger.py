import logging
from typing import Dict

def setup_logger(config: Dict) -> logging.Logger:
    """Configura el logger según las especificaciones del config.yaml"""
    # Mapeo de niveles de log
    log_levels = {
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG
    }

    logger = logging.getLogger('clockify_automation')
    logger.setLevel(logging.DEBUG)  # El nivel más bajo posible para capturar todo

    # Limpiar handlers existentes para evitar duplicados
    logger.handlers = []

    # Obtener configuración de logging
    logging_config = config['execution'].get('logging', {})

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_level = logging_config.get('console_level', 'INFO').upper()
    console_handler.setLevel(log_levels.get(console_level, logging.INFO))
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # Handler para archivo
    file_name = logging_config.get('file_name', 'clockify_automation.log')
    file_handler = logging.FileHandler(file_name)
    file_level = logging_config.get('file_level', 'DEBUG').upper()
    file_handler.setLevel(log_levels.get(file_level, logging.DEBUG))
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    logger.info(f"Logger configurado - Consola: {console_level}, Archivo: {file_level}")
    return logger