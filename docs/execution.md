# Configuración de Ejecución 🎮

## Estructura
```yaml
execution:
  dry_run: true
  logging:
    console_level: "INFO"
    file_level: "DEBUG"
    file_name: "clockify_automation.log"
  sources:
    - type: "asana"
      enabled: true
    - type: "csv"
      enabled: false
```

## Campos

### Modo de Ejecución
- `dry_run`: Si es true, no crea entradas en Clockify (útil para pruebas) 🧪

### Logging
- `console_level`: Nivel de detalle en consola (ERROR, WARNING, INFO, DEBUG) 📟
- `file_level`: Nivel de detalle en archivo de log 📝
- `file_name`: Nombre del archivo de log 📄

### Sources
Lista de fuentes de datos habilitadas:
- `type`: Tipo de fuente ("asana" o "csv") 📊
- `enabled`: Si está activa o no ✅

## Tips 💡
- Usa dry_run: true para probar la configuración
- Los logs te ayudarán a detectar problemas
- Puedes tener múltiples fuentes activas 