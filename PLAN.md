# Historia 3: Cierre de sesión (Logout)

## Story
Como usuario autenticado, quiero cerrar mi sesión, para proteger mi cuenta y privacidad al terminar de usar la plataforma. Requires: #2

## Acceptance criteria
- [x] Given que he iniciado sesión y tengo una sesión activa, when selecciono la opción de cerrar sesión, then mi sesión finaliza inmediatamente, el token y datos locales se eliminan y la interfaz vuelve al estado no autenticado.
- [x] Given que he cerrado sesión, when recargo la página o navego en la aplicación, then el sistema no restablece la sesión previa y muestra las opciones de "Iniciar sesión" y "Registrarse".

## Plan
- Exponer la acción de cierre de sesión en la interfaz (botón o menú en el Navbar junto al correo activo).
- Limpiar el almacenamiento local del cliente (`localStorage.removeItem`) para invalidar el token y perfil del usuario.
- Restablecer el estado reactivo de usuario en la aplicación y mostrar retroalimentación visual (toast) de cierre de sesión exitoso.
- Proveer un endpoint opcional de logout en la API para terminación formal de sesión.

## Out of scope
- Invalidación de tokens en lista negra distribuida con Redis (innecesario para el MVP de cuentas individuales).
- Cierre de sesión remoto en otros dispositivos.

## Suggestions (your call)
- Colocar un botón sutil de cierre de sesión (icono de salida `LogOut`) al lado del correo del usuario en el [Navbar](file:///home/soyisuss/Documents/rag-docs/frontend/src/components/Navbar.tsx).
