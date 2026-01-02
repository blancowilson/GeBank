# 🏦 GeBankSaint: Middle-ERP Reconciliation Suite

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![HTMX](https://img.shields.io/badge/HTMX-3366CC?style=for-the-badge&logo=htmx&logoColor=white)](https://htmx.org/)
[![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/)

GeBankSaint es un middleware financiero de **Arquitectura Hexagonal** diseñado para automatizar la conciliación de pagos entre portales externos (Insytech) y sistemas ERP (Saint). Soporta operaciones multimoneda, gestión de efectivo y procesamiento asíncrono.

## ✨ Características Principales

*   **🔍 Motor de Conciliación Inteligente:** Match automático por referencia, monto y banco con tolerancia configurable.
*   **💱 Soporte Multimoneda:** Conversión dinámica entre USD y VES basada en tasas oficiales o paralelas.
*   **⚡ Interactividad con HTMX:** Interfaz moderna y fluida sin la complejidad de un SPA pesado.
*   **⚙️ Ejecución Flexible:** Soporta procesamiento en segundo plano (Celery + Redis) o ejecución síncrona según la carga.
*   **📂 Gestión de Efectivo:** Flujo diferenciado para "Caja Virtual" y depósitos bancarios.
*   **🛠️ Agnóstico por Diseño:** Estructura preparada para conectar diferentes ERPs o fuentes de pago mediante adaptadores.

## 🚀 Inicio Rápido

### Requisitos Previos
*   Python 3.12+
*   SQL Server (Instancia de Saint)
*   Redis (Para Celery)
*   [uv](https://github.com/astral-sh/uv) (Recomendado para gestión de paquetes)

### Instalación
1.  **Clonar y configurar entorno:**
    ```bash
    git clone https://github.com/your-repo/GeBankSaint.git
    cd GeBankSaint
    uv venv
    .venv\Scripts\activate
    uv pip install -r requirements/dev.txt
    ```

2.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` basado en `.env.example`:
    ```env
    SQL_SERVER_URL=mssql+aioodbc://user:pass@host/dbname?driver=ODBC+Driver+17+for+SQL+Server
    CELERY_BROKER_URL=redis://localhost:6379/0
    USE_CELERY=True
    ```

3.  **Ejecutar la Aplicación:**
    ```bash
    # Servidor Web
    uv run uvicorn app.main:app --reload

    # Celery Worker (En otra terminal)
    uv run celery -A app.infrastructure.tasks.celery_app worker --loglevel=info -P solo
    ```

## 🏗️ Estructura del Proyecto

```text
├── app/
│   ├── application/     # Casos de Uso y DTOs
│   ├── domain/          # Entidades, Lógica y Puertos (Interfaces)
│   ├── infrastructure/  # Adaptadores (Saint, Database, Tasks, Parsers)
│   ├── presentation/    # Rutas API (FastAPI) y Web (Templates Jinja2/HTMX)
│   └── shared/          # Utilidades y Excepciones
├── static/              # CSS (Tailwind) y JS
└── tests/               # Pruebas Unitarias e Integración
```

## 📖 Documentación

*   [Guía de Arquitectura](./ARCHITECTURE.md) - Detalles técnicos del diseño hexagonal.
*   [Roadmap de Implementación](./plan.md) - Estado de las fases del proyecto.
*   [Seguimiento de Tareas (Tracks)](./conductor/tracks.md) - Detalle granular de sprints y tareas.

---
Desarrollado con ❤️ para la eficiencia financiera.