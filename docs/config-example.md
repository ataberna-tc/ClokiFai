# Ejemplo Completo de Configuración 📝

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

time:
  year: 2025
  month: 2
  start_day: 4
  end_day: 28
  lunch_start: 12.5    # 12:30
  lunch_end: 13.5     # 13:30

execution:
  dry_run: true
  logging:
    console_level: "INFO"    # ERROR, WARNING, INFO, DEBUG
    file_level: "DEBUG"      # ERROR, WARNING, INFO, DEBUG
    file_name: "clockify_automation.log"
  sources:
    - type: "asana"
      enabled: true
    - type: "csv"
      enabled: false
      file_path: "tareas_manuales.csv"
      mapping:
        client:
          type: "fixed"
          value: "cliente-ejemplo"
        task:
          type: "column"
          value: "Descripcion"
        day:
          type: "column"
          value: "Fecha"

clockify:
  api_key: "tu-api-key-de-clockify-aqui"

asana:
  access_token: "tu-token-de-asana-aqui"
  workspace_id: "123456789"
  date_range:
    start: "2025-02-04"
    end: "2025-02-28"
```

## Notas Importantes 📌

- Reemplaza los valores de ejemplo con tus propios datos
- Mantén las API keys y tokens seguros
- Usa `dry_run: true` para probar la configuración
- Revisa los logs para detectar problemas 