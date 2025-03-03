import yaml
from typing import Dict
import os

def load_config(config_file: str = 'files/config.yaml') -> Dict:
    """Carga la configuración desde el archivo YAML."""
    # Obtener el directorio raíz del proyecto
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(root_dir, config_file)
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)