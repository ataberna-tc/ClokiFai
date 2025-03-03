import requests
import datetime
from configuration.config import load_config

def get_api_key(config_file='files/config.yaml'):
    """Obtiene la API key de Clockify desde el archivo de configuración."""
    config = load_config(config_file)
    return config['clockify']['api_key']

def get_user():
    api_key = get_api_key()
    data = {'x-api-key': api_key}
    r = requests.get('https://api.clockify.me/api/v1/user', headers=data)
    return r.json()

def get_workspaces():
    api_key = get_api_key()
    data = {'x-api-key': api_key}
    r = requests.get('https://api.clockify.me/api/v1/workspaces', headers=data)
    return r.json()

def get_workspace_by_name(workspace_name):
    workspaces = get_workspaces()
    for workspace in workspaces:
        if workspace['name'].lower().strip() == workspace_name.lower().strip():
            return workspace
    return None

def get_clients(workspace_id):
    api_key = get_api_key()
    data = {'x-api-key': api_key}
    r = requests.get(f'https://global.api.clockify.me/workspaces/{workspace_id}/project-picker/clients?page=1&excludedProjects=&excludedTasks=&search=&userId=&archived=false', headers=data)
    return r.json()

def get_client_by_name(workspace_id, client_name):
    clients = get_clients(workspace_id)
    for client in clients:
        if client['client']['name'].lower().strip() == client_name.lower().strip():
            return client
    return None

def get_project_by_name(workspace_id, client_name, project_name):
    client = get_client_by_name(workspace_id, client_name)
    for project in client['projects']:
        if project['name'].lower().strip() == project_name.lower().strip():
            return project
    return None

def get_project_tasks(workspace_id, project_id):
    api_key = get_api_key()
    data = {'x-api-key': api_key}
    r = requests.get(f'https://api.clockify.me/api/v1/workspaces/{workspace_id}/projects/{project_id}/tasks', headers=data)
    return r.json()

def get_project_task_by_name(workspace_id, project_id, task_name):
    tasks = get_project_tasks(workspace_id, project_id)
    for task in tasks:
        if task['name'].lower().strip() == task_name.lower().strip():
            return task
    return None

def create_time_entry(workspace_id, time_entry):
    api_key = get_api_key()
    data = {'x-api-key': api_key}
    time_entry['start'] = utc_3(time_entry['start']).isoformat() + 'Z'
    time_entry['end'] = utc_3(time_entry['end']).isoformat() + 'Z'
    r = requests.post(f'https://api.clockify.me/api/v1/workspaces/{workspace_id}/time-entries', headers=data, json=time_entry)
    return r.json()

def utc_3(some_date):
    return some_date + datetime.timedelta(hours=3)

def dummy_entry(project_id, project_task_id, description):
    return {
        "billable": True,
        "projectId": project_id,
        "taskId": project_task_id,
        "description": description
    }