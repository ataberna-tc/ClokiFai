from configuration.config import load_config
from configuration.logger import setup_logger
from sources.asana_to_csv import main as asana_main
from sources.csv_to_csv import main as csv_main
from clockify.csv_to_clockify import main as clockify_main

import logging
import os
from typing import Dict
import csv

def process_source(source: Dict, config: Dict, output_file: str) -> bool:
    """Procesa una fuente específica y agrega las tareas al archivo de salida."""
    logger = logging.getLogger('clockify_automation')
    source_type = source.get('type', '').lower()
    
    if not source.get('enabled', False):
        logger.info(f"Fuente {source_type} deshabilitada, saltando...")
        return True

    logger.info(f"Procesando fuente: {source_type}")

    try:
        if source_type == 'asana':
            result = asana_main(output_file)
            return result
            
        elif source_type == 'csv':
            result = csv_main(output_file)
            return result
            
        else:
            logger.error(f"Tipo de fuente no soportado: {source_type}")
            return False
            
    except Exception as e:
        logger.error(f"Error procesando fuente {source_type}: {str(e)}", exc_info=True)
        return False

def create_output_file(output_file: str) -> bool:
    """Crea el archivo de salida con los encabezados."""
    logger = logging.getLogger('clockify_automation')
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Cliente', 'Tarea', 'Dia']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            logger.info(f"Archivo {output_file} creado exitosamente")
        return True
    except Exception as e:
        logger.error(f"Error creando archivo {output_file}: {str(e)}")
        return False

def main():
    try:
        # Cargar configuración
        config = load_config()
        logger = setup_logger(config)
        logger.info("Iniciando orquestador de tareas")

        # Crear archivo de salida
        output_file = 'horarios.csv'
        if os.path.exists(output_file):
            os.remove(output_file)
            logger.debug(f"Archivo anterior {output_file} eliminado")
        
        if not create_output_file(output_file):
            logger.error("No se pudo crear el archivo de salida")
            return

        # Procesar cada fuente
        sources = config['execution'].get('sources', [])
        if not sources:
            logger.warning("No se encontraron fuentes configuradas")
            return

        success = True
        for source in sources:
            if not process_source(source, config, output_file):
                success = False
                logger.error(f"Error procesando fuente: {source.get('type')}")

        if not success:
            logger.error("Hubo errores procesando algunas fuentes")
            return

        # Verificar si se generaron tareas
        if os.path.getsize(output_file) <= len('Cliente,Tarea,Dia\n'):
            logger.error("No se generaron tareas para procesar")
            return

        # Ejecutar csv_to_clockify
        logger.info("Iniciando procesamiento de tareas en Clockify")
        clockify_main()

        logger.info("Proceso completado exitosamente")

    except Exception as e:
        logger.error(f"Error en el orquestador: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 