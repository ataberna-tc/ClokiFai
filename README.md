# ClokiFai 🕒✨

¡Bienvenido al proyecto más emocionante de automatización de registros de tiempo! (O al menos eso nos gusta pensar 😉)

## ¿Qué es esto?

ClokiFai es tu nuevo mejor amigo cuando se trata de registrar tiempo en Clockify. ¿Cansado de pasar horas registrando tus tareas manualmente? ¡Nosotros también! Por eso creamos esta herramienta que hace todo el trabajo pesado por ti.

## Características ✨

- Importa tareas desde Asana (porque copiar y pegar es muy 2010)
- Lee archivos CSV (para los que aún viven en la era de Excel)
- Registra todo automáticamente en Clockify (¡magia! 🎩)
- Maneja múltiples clientes (porque eres todo un profesional)
- Evita solapamientos con almuerzos y reuniones (porque nadie trabaja mientras come 🍕)

## Requisitos 📋

```
requests>=2.31.0  # Para hablar con las APIs
pandas>=2.1.0     # Porque los datos necesitan amor
pyyaml>=6.0.1     # Para configuraciones fancy
asana>=3.2.1      # Para robarle datos a Asana
python-dateutil>=2.8.2  # Porque las fechas son complicadas
```

## Estructura del Proyecto 🏗️

```
ClokiFai/
├── app.py                 # El cerebro de la operación
├── configuration/         # Donde vive la magia de la configuración
│   ├── config.py         # Para que no te pierdas en el camino
│   └── logger.py         # Para saber qué pasó cuando todo explota
├── sources/              # Las fuentes de la verdad
│   ├── asana_to_csv.py   # El espía en Asana
│   └── csv_to_csv.py     # El traductor de CSVs
└── clockify/             # El destino final
    ├── clockify_api.py   # El mensajero de Clockify
    └── csv_to_clockify.py # El alquimista que convierte CSVs en oro
```

## Configuración 🛠️

1. Crea un archivo `files/config.yaml` (sí, en la carpeta `files`, no seas rebelde)
2. Llénalo con tus secretos:
   ```yaml
   clockify:
     api_key: "tu-super-secreta-api-key"
   workspace:
     name: "Tu Workspace Favorito"
   ```README.md
   (Hay más configuraciones, pero dejemos algo para la sorpresa 😉)

## Uso 🚀

```
python app.py
```

Y ¡voilà! 🎉 Siéntate y mira cómo tu tiempo se registra mágicamente.

## ¿Qué hace cada módulo? 🤔

- **app.py**: El director de orquesta. Mantiene a todos en línea.
- **asana_to_csv.py**: El espía profesional que extrae tus tareas de Asana.
- **csv_to_csv.py**: El traductor universal de CSVs (porque un CSV nunca es suficiente).
- **csv_to_clockify.py**: El mago que hace que todo aparezca en Clockify.

## Advertencias ⚠️

- No usar mientras duermes (aunque técnicamente podrías)
- No responsable por exceso de tiempo libre generado
- Puede causar adicción a la automatización
- Tu jefe podría preguntarte qué haces con todo tu tiempo libre

## Contribuciones 🤝

¿Encontraste un bug? ¿Tienes una idea brillante? ¡Abre un issue! (Pero primero asegúrate de que no sea viernes por la tarde 😅)

## Licencia 📄

Este proyecto está bajo la licencia "Haz lo que quieras pero no me culpes si algo sale mal" 😉

## Agradecimientos 🙏

- A café ☕, por hacer posible este proyecto
- A los bugs 🐛, por mantenernos humildes
- A Stack Overflow 🚀, por existir

---

Hecho con ❤️ y mucho ☕ por alguien que odiaba registrar tiempo manualmente

*P.D.: Si este README te hizo reír, considera darle una ⭐*