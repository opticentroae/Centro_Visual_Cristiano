# 👓 Centro Visual Cristiano- Catálogo Digital v1.0

Sistema de catálogo interactivo de alto rendimiento diseñado para **Opticentro A&E**. Esta web prioriza la velocidad de carga y una experiencia de usuario fluida mediante una arquitectura moderna sin dependencias pesadas.

## 🚀 Arquitectura Técnica

- **Frontend Core:** HTML5, CSS3 (Custom Variables) y JavaScript Vanilla.
- **Data Engine:** Gestión dinámica de inventario mediante `inventario.json` para facilitar actualizaciones masivas.
- **UI/UX Style:** Diseño _Glassmorphism_ con soporte nativo para Dark Mode.
- **Optimización:** Aceleración por hardware para animaciones y carga de imágenes mediante estados `loaded`.

## 🛠 Guía para Desarrolladores

Este proyecto está optimizado para ser escalable y ligero:

1. **Variables de Marca:** Configuración de colores centralizada en `:root` dentro de `style.css`.
2. **Efecto Vivo:** Las descripciones utilizan gradientes animados por GPU (`@keyframes brilloTexto`).
3. **Filtrado:** El motor de búsqueda en `script.js` filtra por categorías sin recargar la página, manteniendo el estado de la UI.
4. **Despliegue:** Configurado para **GitHub Pages** con integración continua desde la rama `main`.

## 📦 Estructura de Archivos

- `/img`: Assets visuales y fotografías de aros.
- `/tool`: Scripts auxiliares de automatización.
- `inventario.json`: Base de datos plana del catálogo.
- `script.js`: Lógica de renderizado y filtros dinámicos.

---

Desarrollado con ❤️ por **Articdash** para Centro Visual Cristianoclear.
