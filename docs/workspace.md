# Configuración del Workspace 🏢

## Estructura
```yaml
workspace:
  name: 'Mi Workspace'
  clients:
    - name: 'cliente-ejemplo'
      project: 'Proyecto Demo'
      task: 'Desarrollo'
      start_time: 9
      end_time: 18
      daily_meetings:
        - description: 'Daily Scrum'
          start_time: 12
          end_time: 12.5    # 12:30
```

## Campos

### Workspace
- `name`: Nombre de tu workspace en Clockify 🏢

### Clients
Lista de clientes con sus configuraciones específicas:

- `name`: Nombre del cliente 👥
- `project`: Nombre del proyecto en Clockify 📊
- `task`: Nombre de la tarea general 📝
- `start_time`: Hora de inicio de la jornada (formato 24h) 🌅
- `end_time`: Hora de fin de la jornada (formato 24h) 🌇

### Daily Meetings
Reuniones diarias que se registrarán automáticamente:

- `description`: Nombre de la reunión 💬
- `start_time`: Hora de inicio (12.5 = 12:30) ⏰
- `end_time`: Hora de fin (13.5 = 13:30) ⏰

## Ejemplo Completo
```yaml
workspace:
  name: 'Mi Super Workspace'
  clients:
    - name: 'Cliente A'
      project: 'Proyecto Increíble'
      task: 'Desarrollo Frontend'
      start_time: 9
      end_time: 18
      daily_meetings:
        - description: 'Daily Scrum'
          start_time: 9.5    # 9:30
          end_time: 10       # 10:00
        - description: 'Planning'
          start_time: 15     # 15:00
          end_time: 16       # 16:00
```

## Tips 💡
- Los horarios usan formato decimal (9.5 = 9:30)
- Puedes tener múltiples daily meetings
- El nombre del workspace debe coincidir exactamente con el de Clockify 