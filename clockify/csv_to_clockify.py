import csv
import datetime
from clockify.clockify_api import (
    get_workspace_by_name, get_project_by_name, 
    get_project_task_by_name, create_time_entry,
    dummy_entry
)
from configuration.config import load_config
from configuration.logger import setup_logger
import logging
from typing import List, Tuple, Dict

logger = None

def create_task_entry(task, start_time, end_time, last_task, last_task_start, year, month, day):
    task_start = datetime.datetime(year, month, day, 
                                int(start_time), 
                                int((start_time % 1) * 60))
    
    task_end = datetime.datetime(year, month, day,
                                int(end_time),
                                int((end_time % 1) * 60))
    
    time_entry = task.copy()
    time_entry['start'] = task_start.isoformat() + 'Z'
    time_entry['end'] = task_end.isoformat() + 'Z'
    
    return task['description'], task_start, time_entry

def create_daily_time_entries(project_id: str, project_task_id: str, description: str, 
                            start_date: datetime.datetime, end_date: datetime.datetime) -> List[Dict]:
    """
    Crea entradas de tiempo diarias para un período específico.
    """
    logger = logging.getLogger('clockify_automation')
    time_entry = {
        'description': description,
        'projectId': project_id,
        'taskId': project_task_id,
        'billable': True
    }
    entries = []
    current_date = start_date

    while current_date <= end_date:
        logger.debug(f"Creando time entry para {current_date}")
        if current_date.weekday() < 5:  # Solo días laborables (Lun-Vie)
            entry_start = datetime.datetime.combine(current_date.date(), start_date.time())
            entry_end = datetime.datetime.combine(current_date.date(), end_date.time())
            
            entry = time_entry.copy()
            entry['start'] = entry_start.isoformat() + 'Z'
            entry['end'] = entry_end.isoformat() + 'Z'
            entries.append(entry)
            
        current_date += datetime.timedelta(days=1)
    
    return entries

def csv_to_dummy_entries(csv_file, project_id, project_task_id, client_name):
    entries = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Cliente'] == client_name:
                entry = dummy_entry(project_id, project_task_id, row['Tarea'])
                # Asegurarnos de que todos los campos necesarios estén presentes
                entry.update({
                    'day': int(row['Dia']),
                    'description': row['Tarea'],
                    'projectId': project_id,
                    'taskId': project_task_id
                })
                entries.append(entry)
    
    if not entries:
        print(f"No se encontraron entradas para el cliente {client_name}")
        
    return entries

def format_time(hours: float) -> str:
    """Convierte horas decimales a formato HH:MM."""
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h:02d}:{m:02d}"

def is_time_range_blocked(day: int, start_time: float, end_time: float, lunch_start: float, lunch_end: float, 
                         client: Dict, year: int, month: int) -> bool:
    """Verifica si un rango de tiempo está bloqueado por almuerzo o daily meetings."""
    logger = logging.getLogger('clockify_automation')
    logger.debug(f"Verificando bloqueo para: {format_time(start_time)} - {format_time(end_time)}")
    
    # Verificar almuerzo
    if start_time < lunch_end and end_time > lunch_start:
        logger.debug(f"Bloqueo por almuerzo: {format_time(start_time)} - {format_time(end_time)}")
        logger.debug(f"Horario almuerzo: {format_time(lunch_start)} - {format_time(lunch_end)}")
        return True
        
    # Verificar daily meetings
    daily_meetings = get_daily_meetings_for_day(day, client, year, month)
    logger.debug(f"Daily meetings para el día {day}: {len(daily_meetings)}")
    
    for meeting in daily_meetings:
        meeting_start = float(meeting['start_time'])
        meeting_end = float(meeting['end_time'])
        
        logger.debug(f"Comparando con daily meeting: {format_time(meeting_start)} - {format_time(meeting_end)}")
        
        if (
            (start_time >= meeting_start and start_time < meeting_end) or
            (end_time > meeting_start and end_time <= meeting_end) or
            (start_time <= meeting_start and end_time >= meeting_end)
        ):
            logger.debug("¡BLOQUEO! Solapamiento detectado con daily meeting")
            logger.debug(f"Tarea: {format_time(start_time)} - {format_time(end_time)}")
            logger.debug(f"Meeting: {format_time(meeting_start)} - {format_time(meeting_end)}")
            return True
            
    logger.debug("No se detectó bloqueo")
    return False

def get_daily_meetings_for_day(day: int, client: Dict, year: int, month: int) -> List[Dict]:
    """Obtiene las daily meetings para un día específico del cliente."""
    if not client or 'daily_meetings' not in client:
        return []
        
    # Solo devolver meetings para días laborables
    if datetime.datetime(year, month, day).weekday() >= 5:
        return []
        
    return client['daily_meetings']

def get_available_blocks(day: int, start_time: float, end_time: float, lunch_start: float, lunch_end: float, 
                        client: Dict, year: int, month: int) -> List[Tuple[float, float]]:
    """Obtiene todos los bloques de tiempo disponibles en el día."""
    logger = logging.getLogger('clockify_automation')
    logger.info(f"Analizando bloques disponibles para el día {day}")
    blocks = []
    
    # Crear lista ordenada de todos los eventos bloqueados
    blocked_periods = []
    
    # Agregar almuerzo
    blocked_periods.append({
        'type': 'lunch',
        'start': lunch_start,
        'end': lunch_end
    })
    
    # Agregar daily meetings del día
    daily_meetings = get_daily_meetings_for_day(day, client, year, month)
    for meeting in daily_meetings:
        blocked_periods.append({
            'type': 'meeting',
            'description': meeting['description'],
            'start': float(meeting['start_time']),
            'end': float(meeting['end_time'])
        })
    
    blocked_periods.sort(key=lambda x: x['start'])
    
    logger.debug("Períodos bloqueados:")
    for period in blocked_periods:
        period_type = period['type']
        if period_type == 'meeting':
            logger.debug(f"Daily Meeting '{period['description']}': {format_time(period['start'])} - {format_time(period['end'])}")
        else:
            logger.debug(f"Almuerzo: {format_time(period['start'])} - {format_time(period['end'])}")
    
    # Encontrar bloques disponibles entre eventos bloqueados
    current_time = start_time
    
    for period in blocked_periods:
        period_start = period['start']
        period_end = period['end']
        
        # Si hay tiempo disponible antes del período bloqueado
        if current_time < period_start:
            blocks.append((current_time, period_start))
            logger.debug(f"Agregando bloque disponible: {format_time(current_time)} - {format_time(period_start)}")
        
        # Actualizar el tiempo actual al final del período bloqueado
        current_time = max(current_time, period_end)
    
    # Agregar bloque final si queda tiempo disponible
    if current_time < end_time:
        blocks.append((current_time, end_time))
        logger.debug(f"Agregando bloque final disponible: {format_time(current_time)} - {format_time(end_time)}")
    
    # Verificar y ajustar bloques
    final_blocks = []
    for start, end in blocks:
        # Solo agregar bloques que tengan al menos 15 minutos
        if end - start >= 0.25:
            final_blocks.append((start, end))
            
    logger.debug("\nBloques disponibles finales:")
    for start, end in final_blocks:
        logger.debug(f"{format_time(start)} - {format_time(end)}")
    
    return final_blocks

def dummy_to_time_entries(entries_wo_time: List[Dict], workspace_id: str, year: int, month: int, 
                         start_day: int, end_day: int, start_time: float, end_time: float, 
                         lunch_start: float, lunch_end: float, client: Dict) -> List[Dict]:
    """
    Genera entradas de tiempo evitando solapamientos y maximizando el uso del tiempo disponible.
    """
    logger = logging.getLogger('clockify_automation')
    tasks_by_day = {}
    time_entries = []

    # Obtener IDs de Clockify
    try:
        project = get_project_by_name(workspace_id, client['name'], client['project'])
        if not project:
            logger.error(f"No se encontró el proyecto: {client['project']}")
            return []
        project_id = project['id']

        task = get_project_task_by_name(workspace_id, project_id, client['task'])
        if not task:
            logger.error(f"No se encontró la tarea: {client['task']}")
            return []
        task_id = task['id']

    except Exception as e:
        logger.error(f"Error obteniendo IDs de Clockify: {str(e)}")
        return []

    # Procesar daily meetings primero si están configuradas
    if client.get('daily_meetings'):
        start_date = datetime.datetime(year, month, start_day)
        end_date = datetime.datetime(year, month, end_day)
        
        for meeting in client['daily_meetings']:
            daily_entries = create_daily_time_entries(
                project_id,
                task_id,
                meeting['description'],
                start_date,
                end_date
            )
            time_entries.extend(daily_entries)
            logger.info(f"Agregadas {len(daily_entries)} entradas para daily meeting: {meeting['description']}")

    # Agrupar tareas por día
    for day in range(start_day, end_day + 1):
        tasks_by_day[day] = []
        for entry in entries_wo_time:
            try:
                entry_day = int(entry['Dia'])
                if entry_day == day:
                    task_entry = {
                        'description': entry['Tarea'],
                        'projectId': project_id,
                        'taskId': task_id,
                        'billable': True
                    }
                    tasks_by_day[day].append(task_entry)
            except (ValueError, KeyError) as e:
                logger.warning(f"Error procesando entrada: {entry}. Error: {str(e)}")
                continue

    # Procesar cada día
    for day in range(start_day, end_day + 1):
        if day not in tasks_by_day or not tasks_by_day[day]:
            continue
            
        logger.info(f"Procesando día {day}")
        daily_tasks = tasks_by_day[day]
        available_blocks = get_available_blocks(
            day, start_time, end_time, lunch_start, lunch_end, 
            client, year, month
        )
        
        if not available_blocks:
            logger.warning(f"No hay bloques disponibles para el día {day}")
            continue

        total_available_time = sum(end - start for start, end in available_blocks)
        avg_duration = total_available_time / len(daily_tasks)
        logger.info(f"Tiempo total disponible: {format_time(total_available_time)}")
        logger.debug(f"Duración promedio por tarea: {format_time(avg_duration)}")
        
        if len(daily_tasks) == 1:
            task = daily_tasks[0]
            
            # Distribuir la tarea entre los bloques disponibles
            for block_start, block_end in available_blocks:
                if is_time_range_blocked(day, block_start, block_end, lunch_start, lunch_end, client, year, month):
                    continue
                
                if block_end - block_start >= 0.25:  # Mínimo 15 minutos
                    time_entry = task.copy()
                    time_entry['start'] = datetime.datetime(
                        year, month, day,
                        int(block_start),
                        int((block_start % 1) * 60)
                    ).isoformat() + 'Z'
                    
                    time_entry['end'] = datetime.datetime(
                        year, month, day,
                        int(block_end),
                        int((block_end % 1) * 60)
                    ).isoformat() + 'Z'
                    
                    if datetime.datetime(year, month, day).weekday() < 5:
                        time_entries.append(time_entry)
        else:
            current_task_index = 0
            for block_start, block_end in available_blocks:
                block_duration = block_end - block_start
                tasks_in_block = max(1, int(block_duration / avg_duration))
                
                if current_task_index >= len(daily_tasks):
                    break
                    
                time_per_task = block_duration / tasks_in_block
                
                for _ in range(tasks_in_block):
                    if current_task_index >= len(daily_tasks):
                        break
                        
                    task = daily_tasks[current_task_index]
                    task_start = block_start
                    task_end = min(block_end, task_start + time_per_task)
                    
                    if is_time_range_blocked(day, task_start, task_end, lunch_start, lunch_end, client, year, month):
                        continue
                    
                    if task_end - task_start >= 0.25:  # Mínimo 15 minutos
                        time_entry = task.copy()
                        time_entry['start'] = datetime.datetime(
                            year, month, day,
                            int(task_start),
                            int((task_start % 1) * 60)
                        ).isoformat() + 'Z'
                        
                        time_entry['end'] = datetime.datetime(
                            year, month, day,
                            int(task_end),
                            int((task_end % 1) * 60)
                        ).isoformat() + 'Z'
                        
                        if datetime.datetime(year, month, day).weekday() < 5:
                            time_entries.append(time_entry)
                    
                    block_start = task_end
                    current_task_index += 1

    return time_entries

def save_entries_to_csv(entries, output_file='time_entries.csv'):
    # Define las columnas que queremos guardar
    fieldnames = ['description', 'start', 'end', 'billable', 'projectId', 'taskId']
    
    # Abre el archivo en modo escritura
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        # Crea el escritor CSV
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escribe el encabezado
        writer.writeheader()
        
        # Escribe cada entrada
        for entry in entries:
            writer.writerow({
                'description': entry['description'],
                'start': entry['start'],
                'end': entry['end'],
                'billable': entry['billable'],
                'projectId': entry['projectId'],
                'taskId': entry['taskId']
            })
    
    print(f"Entries saved to {output_file}")

def main() -> bool:
    """Función principal para procesar el CSV y crear entradas en Clockify."""
    try:
        global logger

        config = load_config()

        if not logger:
            logger = setup_logger(config)

        logger.info("Iniciando procesamiento de tareas para Clockify")

        # Obtener configuración
        workspace_name = config['workspace']['name']
        clients = config['workspace']['clients']
        time_config = config.get('time', {})
        
        # Validar configuración de tiempo
        required_time_params = ['year', 'month', 'start_day', 'end_day', 'lunch_start', 'lunch_end']
        missing_params = [param for param in required_time_params if param not in time_config]
        if missing_params:
            logger.error(f"Faltan parámetros de tiempo en la configuración: {missing_params}")
            return False

        logger.info(f"Procesando para workspace: {workspace_name}")
        
        # Obtener workspace_id
        workspace = get_workspace_by_name(workspace_name)
        if not workspace:
            logger.error(f"No se encontró el workspace: {workspace_name}")
            return False
            
        workspace_id = workspace['id']
        logger.debug(f"Workspace ID: {workspace_id}")

        # Procesar cada cliente
        for client_config in clients:
            client_name = client_config['name']
            logger.info(f"Procesando cliente: {client_name}")
            
            # Leer tareas del CSV
            entries_wo_time = []
            with open('horarios.csv', 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                entries_wo_time = [row for row in reader if row['Cliente'].lower() == client_name.lower()]

            if not entries_wo_time:
                logger.warning(f"No se encontraron tareas para el cliente: {client_name}")
                continue

            logger.info(f"Se encontraron {len(entries_wo_time)} tareas para {client_name}")

            # Generar entradas de tiempo
            time_entries = dummy_to_time_entries(
                entries_wo_time=entries_wo_time,
                workspace_id=workspace_id,
                year=time_config['year'],
                month=time_config['month'],
                start_day=time_config['start_day'],
                end_day=time_config['end_day'],
                start_time=client_config.get('start_time', 9),
                end_time=client_config.get('end_time', 18),
                lunch_start=time_config['lunch_start'],
                lunch_end=time_config['lunch_end'],
                client=client_config
            )

            if not time_entries:
                logger.warning(f"No se generaron entradas de tiempo para: {client_name}")
                continue

            logger.info(f"Se generaron {len(time_entries)} entradas de tiempo para {client_name}")

            # Si no es dry run, crear entradas en Clockify
            if not config['execution'].get('dry_run', True):
                for entry in time_entries:
                    try:
                        create_time_entry(workspace_id, entry)
                        logger.debug(f"Entrada creada: {entry.get('description', 'Sin descripción')}")
                    except Exception as e:
                        logger.error(f"Error creando entrada: {str(e)}")
                        return False
                logger.info(f"Entradas creadas exitosamente para {client_name}")
            else:
                logger.info("Modo dry run - No se crearon entradas en Clockify")
                save_entries_to_csv(time_entries, f'time_entries_{client_name}.csv')

        logger.info("Proceso completado exitosamente")
        return True

    except Exception as e:
        logger.error(f"Error en el procesamiento: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    main()