# Context & Stack

## Context
Sistema de autenticación y gestión de usuarios individuales para Yael Bot, permitiendo registro, inicio y cierre de sesión seguro.

Stack:
- **Backend:** FastAPI (Python >= 3.13)
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
- **Base de datos:** PostgreSQL en Neon
- **Base de datos vectorial:** Qdrant Cloud
- **LLM:** Google Gemini Flash
- **Autenticación:** Correo electrónico y contraseña

Expensive decisions: none (cuentas individuales, rol estándar único, 100% online, un solo idioma)
