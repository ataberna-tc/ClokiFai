# Configuración del Tiempo ⏰

## Estructura
```yaml
time:
  year: 2025
  month: 2
  start_day: 4
  end_day: 28
  lunch_start: 12.5    # 12:30
  lunch_end: 13.5      # 13:30
```

## Campos

### Período
- `year`: Año a procesar 📅
- `month`: Mes a procesar (1-12) 📅
- `start_day`: Día inicial del mes 📅
- `end_day`: Día final del mes 📅

### Horarios
- `lunch_start`: Hora de inicio del almuerzo (formato decimal) 🍽️
- `lunch_end`: Hora de fin del almuerzo (formato decimal) 🍽️

## Formato de Horas
- Se usa formato decimal
- 12.5 = 12:30
- 13.75 = 13:45
- 9.25 = 9:15

## Tips 💡
- El almuerzo se bloquea automáticamente
- Solo se procesan días hábiles (Lun-Vie)
- Las horas se ajustan automáticamente para evitar solapamientos 