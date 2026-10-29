# Historia 1: Registro de usuario y persistencia en Neon

## Story
Como usuario nuevo, quiero registrarme con correo y contraseña, para tener una cuenta personal y acceder a la plataforma sobre una base de datos PostgreSQL en Neon, en una arquitectura desacoplada (Frontend en Cloudflare Pages y Backend en Google Cloud Run).

## Acceptance criteria
- [x] Given que soy un usuario sin cuenta, when ingreso un correo y contraseña válidos y envío el formulario de registro, then se crea mi cuenta en la base de datos Neon y recibo confirmación de registro exitoso.
- [x] Given que un correo ya está registrado en el sistema, when intento registrarme nuevamente con ese mismo correo, then el sistema rechaza el registro y muestra un mensaje indicando que el correo ya está en uso.
- [x] Given que ingreso datos inválidos (correo mal formado o contraseña vacía), when envío el formulario de registro, then el sistema no crea la cuenta y muestra los errores de validación correspondientes.

## Estado de infraestructura previa completada
- [x] **Aprovisionamiento Neon completado:**
  - Neon CLI v8.13.2 instalado y autenticado.
  - Proyecto vinculado a `lucky-shape-90239548` (rama `production`, org `org-winter-haze-15926637`).
  - Variables `DATABASE_URL`, `DATABASE_URL_UNPOOLED` y `NEON_BRANCH` sincronizadas en `.env`.
  - Servidor MCP de Neon y 10 skills oficiales instalados en el entorno.
- [x] **Desacoplamiento Frontend / Backend completado:**
  - Frontend preparado para Cloudflare Pages con normalización de `VITE_API_URL` en `frontend/src/services/api.ts` y plantilla `frontend/.env.example`.
  - Backend preparado para Cloud Run con soporte configurable de `CORS_ORIGINS` en `src/infrastructure/config.py` y `src/presentation/main.py`.
  - Dockerfile simplificado como contenedor exclusivo de Python/FastAPI (sin etapa Node.js).
  - Verificación `npm run build` ejecutada con éxito.

## Plan de Implementación (Historia 1)
- Instalar dependencias de base de datos y seguridad en el backend (`asyncpg`, `sqlalchemy[asyncio]`, `pwdlib`/`bcrypt`) y configurar la conexión a Neon vía `DATABASE_URL` (pooled) y creación/migración de la tabla `users` (id, email, password_hash, created_at).
- Implementar el repositorio y caso de uso de registro de usuario con validación de correo único y hashing seguro de contraseñas.
- Exponer el endpoint `POST /api/v1/auth/register` con esquemas Pydantic para validación y respuestas HTTP semánticas (201 Created, 400 Bad Request, 409 Conflict).
- Integrar la llamada de registro en `frontend/src/services/api.ts` y construir el componente/formulario de registro en React con estados de carga, éxito y visualización de errores de validación.
- Conectar el formulario con la API y validar el flujo de extremo a extremo contra Neon.

## Verificación y Pruebas
- Ejecutar `npm run build` en el frontend para asegurar que compila sin errores de tipos o bundling.
- Ejecutar pruebas automatizadas de integración contra los endpoints de registro y la base de datos Neon.
- Probar el flujo extremo a extremo en la aplicación.
- Reportar los cambios efectuados y los resultados de las pruebas.

## Out of scope
- Inicio de sesión y generación de tokens de sesión JWT / cookies (Historia #2).
- Cierre de sesión (Historia #3).
- Verificación por correo electrónico o envío de correos transaccionales.
- Recuperación o reseteo de contraseña.
