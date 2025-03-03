from configuration.config import load_config
from configuration.logger import setup_logger 

import asana
import csv
from datetime import datetime
from typing import List, Dict
import logging

def between_dates(task_date: datetime, start_date: datetime, end_date: datetime) -> bool:
    if start_date.year <= task_date.year <= end_date.year:
        if start_date.month <= task_date.month <= end_date.month:
            if start_date.day <= task_date.day <= end_date.day:
                return True
    return False

class AsanaTaskExtractor:
    def __init__(self, access_token: str):
        """Inicializa el cliente de Asana con un token de acceso."""
        self.logger = logging.getLogger('clockify_automation')
        self.logger.debug("Inicializando cliente de Asana")
        config = asana.Configuration()
        config.access_token = access_token
        self.client = asana.ApiClient(config)
        self.client.headers={'asana-enable': 'new_user_task_lists'}
        
    def get_my_tasks(self, workspace_id: str, start_date: datetime, end_date: datetime, client_name: str) -> List[Dict]:
        """Obtiene todas las tareas del usuario en el rango de fechas especificado."""
        users_api_instance = asana.UsersApi(self.client)
        tasks_api_instance = asana.TasksApi(self.client)

        me = users_api_instance.get_user("me", {})
        user_id = me['gid']
        self.logger.debug(f"ID de usuario obtenido: {user_id}")

        opts = {
            'limit': 100,
            'assignee': user_id,
            'workspace': workspace_id,
            'completed_since': start_date.isoformat(),
            'modified_since': start_date.isoformat(),
            'opt_fields': "name,assignee,assignee.name,assignee_status,custom_fields,custom_fields.name,custom_fields.display_value,custom_fields.enum_value,custom_fields.enum_value.name,completed,completed_at,completed_by,completed_by.name,created_at,created_by,due_at,due_on,start_at,start_on,modified_at,workspace,workspace.name",
        }
        
        self.logger.debug("Consultando tareas en Asana")
        tasks_search = tasks_api_instance.get_tasks(opts)
        tasks = []
        for task in tasks_search:
            for field in task['custom_fields']:
                if field['name'].lower()=="status":
                    task.update({'status':field['display_value']})

            task.pop('custom_fields',None)
            tasks.append(task)

        self.logger.debug(f"Se encontraron {len(tasks)} tareas en total")

        formatted_tasks = []
        for task in tasks:
            try:
                is_completed = task.get('completed', False)

                task_status = task.get('status')
                if task_status:
                    task_status = task_status.replace('Completed','Completada').replace('In Progress','En Progreso')
                else:
                    task_status = 'Completada' if is_completed else 'No iniciada'

                task_modified_date = task.get('modified_at',None)
                task_modified_date = datetime.fromisoformat(task_modified_date.replace('Z', '+00:00')) if task_modified_date else None
                
                if is_completed and task.get('completed_at'):
                    task_end_date = datetime.fromisoformat(task['completed_at'].replace('Z', '+00:00'))
                elif task.get('due_on'):
                    task_end_date = datetime.fromisoformat(task['due_on'].replace('Z', '+00:00'))
                else:
                    task_end_date = task_modified_date


                task_start_date = task.get('start_on',None)
                if task_start_date:
                    task_start_date = datetime.fromisoformat(task_start_date.replace('Z', '+00:00'))
                    task_start_date = task_modified_date if task_modified_date.isoformat() < task_start_date.isoformat() else task_start_date
                else:
                    task_start_date = task_modified_date

                if task.get('due_on'):
                    if datetime.fromisoformat(task['due_on'].replace('Z', '+00:00')).isoformat() < task_start_date.isoformat():
                        task_start_date = datetime.fromisoformat(task['due_on'].replace('Z', '+00:00'))

                include_task = between_dates(task_modified_date,start_date,end_date) and (task_status in ['En Progreso','Completada'])

                # Incluir la tarea si está dentro del rango de fechas
                if include_task:
                    self.logger.debug(f"Procesando tarea: {task['name']}")
                    current_day = task_start_date.day

                    last_worked_day = task_end_date.day
                    if task_end_date.month > end_date.month:
                        last_worked_day = end_date.day

                    while current_day <= last_worked_day:
                        # Formatear la tarea
                        formatted_task = {
                            'Dia': current_day,
                            'Cliente': client_name,
                            'Tarea': task['name'],
                            'Estado': task_status
                        }
                        formatted_tasks.append(formatted_task.copy())
                        current_day += 1
                
            except Exception as e:
                self.logger.error(f"Error procesando tarea: {task.get('name', 'Sin nombre')} - {str(e)}")
                continue
        
        self.logger.info(f"Se procesaron {len(formatted_tasks)} entradas de tareas exitosamente")
        return formatted_tasks
    
    def _extract_client_from_task(self, task: Dict) -> str:
        """Extrae el nombre del cliente de los campos personalizados o del proyecto."""
        # Buscar en campos personalizados
        if task.get('custom_fields'):
            for field in task['custom_fields']:
                if field['name'].lower() in ['cliente', 'client', 'company']:
                    return field.get('display_value', 'Sin Cliente')
        
        # Si no hay campo personalizado, intentar extraer del nombre del proyecto
        if task.get('projects'):
            project_name = task['projects'][0]['name']
            if ' - ' in project_name:
                return project_name.split(' - ')[0]
        
        return 'Sin Cliente'

def save_tasks_to_csv(tasks: List[Dict], output_file: str):
    """Guarda las tareas en un archivo CSV."""
    logger = logging.getLogger('clockify_automation')
    
    if not tasks:
        logger.warning("No hay tareas para guardar en CSV")
        return
    
    # Eliminar el campo Estado que no necesitamos en el output
    for task in tasks:
        task.pop('Estado', None)
    
    fieldnames = ['Cliente', 'Tarea', 'Dia']
    
    try:
        # Agregar al archivo existente
        with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerows(tasks)
        
        logger.info(f"Se agregaron {len(tasks)} tareas al archivo {output_file}")
        logger.debug(f"Se guardaron {len(tasks)} entradas en el CSV")
    except Exception as e:
        logger.error(f"Error al guardar el archivo CSV: {str(e)}")
        raise

def main(output_file: str = 'horarios.csv') -> bool:
    """Función principal para extraer tareas de Asana."""
    try:
        config = load_config()
        logger = setup_logger(config)
        logger.info("Iniciando extracción de tareas de Asana")
        
        # Obtener configuración de Asana
        asana_config = config.get('asana', {})
        access_token = asana_config.get('access_token')
        workspace_id = asana_config.get('workspace_id')
        
        if not access_token or not workspace_id:
            logger.error("Falta configuración de Asana (access_token o workspace_id)")
            return False
        
        # Obtener fechas del rango
        date_range = asana_config.get('date_range', {})
        try:
            start_date = datetime.fromisoformat(date_range.get('start'))
            end_date = datetime.fromisoformat(date_range.get('end'))
        except (ValueError, TypeError) as e:
            logger.error(f"Error al procesar las fechas: {str(e)}")
            return False
        
        logger.info(f"Período de búsqueda: {start_date.date()} hasta {end_date.date()}")
        
        # Inicializar el extractor
        logger.debug("Inicializando extractor de Asana")
        extractor = AsanaTaskExtractor(access_token)
        
        try:
            # Obtener tareas
            logger.info("Obteniendo tareas de Asana...")
            tasks = extractor.get_my_tasks(workspace_id, start_date, end_date, 'trafilea')
            logger.info(f"Se obtuvieron {len(tasks)} entradas de tareas")

            unique_tasks = set([task['Tarea']+'---'+task['Estado'] for task in tasks])
            
            # Imprimir resumen
            total_tasks = len(unique_tasks)
            completed_tasks = sum(1 for task in unique_tasks if task.split('---')[1] == 'Completada')
            in_progress_tasks = total_tasks - completed_tasks
            
            logger.info("\nResumen de tareas:")
            logger.info(f"Total de tareas únicas: {total_tasks}")
            logger.info(f"Tareas completadas: {completed_tasks}")
            logger.info(f"Tareas en progreso: {in_progress_tasks}")
            
            # Guardar en CSV
            save_tasks_to_csv(tasks, output_file)
            logger.info("Proceso completado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al procesar las tareas: {str(e)}", exc_info=True)
            return False

    except Exception as e:
        logger.error(f"Error en la extracción de Asana: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    main() 