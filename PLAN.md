# Historia 2: Inicio de sesión de usuario

## Story
Como usuario registrado, quiero iniciar sesión con mi correo y contraseña, para autenticarme y utilizar la plataforma. Requires: #1

## Acceptance criteria
- [x] Given que soy un usuario registrado, when ingreso mi correo y contraseña correctos y envío el formulario de inicio de sesión, then accedo a la plataforma y veo mi correo o sesión activa reflejada en la interfaz.
- [x] Given que ingreso credenciales incorrectas (correo no registrado o contraseña errónea), when intento iniciar sesión, then el sistema rechaza el acceso y muestra un mensaje de credenciales inválidas sin revelar cuál de los dos campos falló.
- [x] Given que ingreso campos con formato inválido o vacíos, when intento iniciar sesión, then el sistema no procesa el inicio de sesión y muestra los errores de validación.

## Plan
- Implementar la verificación de credenciales con hashing seguro contra la base de datos Neon y emitir un token de sesión/acceso.
- Exponer el endpoint de autenticación con validación de esquema y respuestas semánticas (200 OK con token, 401 Unauthorized para credenciales inválidas).
- Diseñar la vista/formulario de inicio de sesión en el frontend con estados de carga y retroalimentación de error.
- Almacenar el token de sesión en el cliente y actualizar el estado de autenticación en la interfaz.
- Conectar el formulario con el endpoint para completar el flujo de extremo a extremo.

## Out of scope
- Cierre de sesión (Historia #3).
- Persistencia compleja de refresh tokens o rotación multi-dispositivo.
- Recuperación o reseteo de contraseña.
- Bloqueo de cuenta tras N intentos fallidos (rate limiting avanzado).

## Suggestions (your call)
- Utilizar tokens JWT firmados (con `PyJWT`) para transportar la identidad del usuario de forma ligera entre Cloudflare Pages y Cloud Run.
- Alternar limpiamente entre los modales de "Registrarse" e "Iniciar sesión" en el frontend para una experiencia de usuario fluida.
