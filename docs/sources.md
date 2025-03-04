# Configuración de Fuentes 📊

## Asana
```yaml
asana:
  access_token: "tu-token-de-asana"
  workspace_id: "123456789"
```

### Campos
- `access_token`: Tu token personal de Asana 🔑
- `workspace_id`: ID del workspace de Asana 🏢

## CSV
```yaml
sources:
  - type: "csv"
    enabled: true
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
```

### Campos
- `file_path`: Ruta al archivo CSV 📄
- `mapping`: Mapeo de columnas:
  - `type`: "fixed" (valor fijo) o "column" (nombre de columna)
  - `value`: Valor fijo o nombre de la columna

## Tips 💡
- El CSV debe tener encabezados
- Las fechas deben coincidir con la configuración de time
- Puedes usar valores fijos o columnas del CSV 