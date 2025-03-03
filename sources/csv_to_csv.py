from configuration.config import load_config
from configuration.logger import setup_logger 

import csv
import logging
from typing import  Dict
import os

def validate_csv_format(file_path: str, mapping: Dict) -> bool:
    """Valida que el CSV tenga el formato correcto según el mapeo configurado."""
    logger = logging.getLogger('clockify_automation')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = set(reader.fieldnames)
            
            # Verificar columnas requeridas según el mapeo
            required_columns = set()
            for field, map_config in mapping.items():
                if map_config['type'] == 'column':
                    required_columns.add(map_config['value'])
            
            if not required_columns.issubset(headers):
                missing_fields = required_columns - headers
                logger.error(f"Columnas requeridas faltantes en el CSV: {missing_fields}")
                return False
                
            # Validar que haya al menos una fila de datos
            if not any(row for row in reader):
                logger.error("El archivo CSV está vacío")
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"Error validando el archivo CSV: {str(e)}")
        return False

def map_row_to_task(row: Dict, mapping: Dict) -> Dict:
    """Mapea una fila del CSV a una tarea según la configuración."""
    task = {}
    
    # Mapear Cliente
    if mapping['client']['type'] == 'fixed':
        task['Cliente'] = mapping['client']['value']
    else:
        task['Cliente'] = row[mapping['client']['value']]
    
    # Mapear Tarea
    task['Tarea'] = row[mapping['task']['value']]
    
    # Mapear Día
    task['Dia'] = row[mapping['day']['value']]
    
    return task

def process_csv_tasks(input_file: str, output_file: str, mapping: Dict) -> bool:
    """Procesa las tareas del CSV de entrada y las agrega al archivo de salida."""
    logger = logging.getLogger('clockify_automation')
    
    try:
        if not validate_csv_format(input_file, mapping):
            return False
            
        logger.info(f"Procesando tareas desde {input_file}")
        
        # Leer tareas del archivo de entrada
        tasks = []
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    task = map_row_to_task(row, mapping)
                    tasks.append(task)
                except KeyError as e:
                    logger.warning(f"Error mapeando fila, columna no encontrada: {str(e)}")
                    continue
                except Exception as e:
                    logger.warning(f"Error procesando fila: {str(e)}")
                    continue
        
        logger.info(f"Se encontraron {len(tasks)} tareas válidas en el archivo")
        
        # Agregar al archivo de salida
        with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Cliente', 'Tarea', 'Dia']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerows(tasks)
            
        logger.info(f"Tareas agregadas exitosamente a {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error procesando el archivo CSV: {str(e)}", exc_info=True)
        return False

def main(output_file: str = 'horarios.csv') -> bool:
    """Función principal para procesar fuentes CSV."""
    try:
        config = load_config()
        logger = setup_logger(config)
        
        logger.info("Iniciando procesamiento de fuentes CSV")
        
        # Obtener fuentes CSV habilitadas
        csv_sources = [
            source for source in config['execution'].get('sources', [])
            if source.get('type') == 'csv' and source.get('enabled', False)
        ]
        
        if not csv_sources:
            logger.info("No hay fuentes CSV habilitadas")
            return True
        
        success = True
        for source in csv_sources:
            file_path = source.get('file_path')
            mapping = source.get('mapping')
            
            if not file_path:
                logger.error("Ruta de archivo CSV no especificada")
                success = False
                continue
                
            if not mapping:
                logger.error("Configuración de mapeo no especificada")
                success = False
                continue
                
            if not os.path.exists(file_path):
                logger.error(f"Archivo CSV no encontrado: {file_path}")
                success = False
                continue
                
            logger.info(f"Procesando archivo CSV: {file_path}")
            if not process_csv_tasks(file_path, output_file, mapping):
                success = False
        
        return success
        
    except Exception as e:
        logger.error(f"Error en el procesamiento de CSV: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    main() 