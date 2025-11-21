# Salud Rural - Frontend

Frontend de la aplicación de gestión de salud rural construido con React, Vite y Tailwind CSS.

## Características

- 🔐 **Autenticación JWT**: Sistema de login y gestión de sesiones
- 📊 **Dashboard**: Vista general con estadísticas y próximas citas
- 📅 **Gestión de Citas**: Crear, editar, cancelar y completar citas médicas
- 👥 **Gestión de Pacientes**: CRUD completo de pacientes
- 👨‍⚕️ **Médicos**: Visualización y filtrado de médicos
- 👤 **Perfil**: Gestión de información personal y cambio de contraseña
- 🎨 **UI Moderna**: Diseño limpio y responsivo con Tailwind CSS

## Requisitos Previos

- Node.js 16+ y npm
- Backend Django funcionando en `http://127.0.0.1:8000`

## Instalación

1. Instala las dependencias:

```bash
npm install
```

## Uso

### Modo Desarrollo

Ejecuta el servidor de desarrollo:

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

### Compilar para Producción

```bash
npm run build
```

Los archivos compilados estarán en la carpeta `dist/`.

### Vista Previa de Producción

```bash
npm run preview
```

## Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto frontend:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/      # Componentes reutilizables
│   │   ├── Layout.jsx
│   │   ├── Navbar.jsx
│   │   └── Sidebar.jsx
│   ├── contexts/        # Contextos de React
│   │   └── AuthContext.jsx
│   ├── pages/          # Páginas principales
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Citas.jsx
│   │   ├── Pacientes.jsx
│   │   ├── Medicos.jsx
│   │   └── Perfil.jsx
│   ├── services/       # Servicios API
│   │   └── api.js
│   ├── App.jsx         # Componente principal
│   ├── main.jsx        # Punto de entrada
│   └── index.css       # Estilos globales
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Funcionalidades Principales

### Autenticación
- Login con correo y contraseña
- Logout seguro
- Renovación automática de tokens JWT
- Protección de rutas

### Dashboard
- Estadísticas generales (citas del día, pendientes, pacientes, médicos)
- Lista de próximas citas

### Gestión de Citas
- Crear nuevas citas
- Ver lista de todas las citas
- Cancelar citas
- Completar citas
- Filtrar por estado

### Gestión de Pacientes
- Listar todos los pacientes
- Crear nuevo paciente
- Editar información de paciente
- Eliminar paciente
- Vista de tarjetas con información detallada

### Médicos
- Listar todos los médicos
- Filtrar por estado (Activo/Inactivo)
- Ver información detallada de cada médico

### Perfil
- Ver información personal
- Cambiar contraseña
- Actualizar datos de usuario

## Tecnologías Utilizadas

- **React 18**: Biblioteca de UI
- **Vite**: Build tool y dev server
- **React Router**: Enrutamiento
- **Axios**: Cliente HTTP
- **Tailwind CSS**: Framework de estilos
- **Lucide React**: Iconos
- **date-fns**: Manejo de fechas

## Conexión con el Backend

El frontend se conecta al backend Django mediante:

- **Base URL**: `http://127.0.0.1:8000/api`
- **Autenticación**: JWT Bearer tokens
- **CORS**: Configurado en el backend para permitir requests desde el frontend

## Notas

- Los tokens JWT se almacenan en `localStorage`
- El interceptor de Axios maneja automáticamente la renovación de tokens
- Las rutas protegidas redirigen al login si el usuario no está autenticado
- El diseño es responsivo y funciona en dispositivos móviles

## Problemas Comunes

### Error de CORS
Asegúrate de que el backend tenga configurado CORS correctamente en `settings.py`:
```python
CORS_ALLOW_ALL_ORIGINS = True
```

### Error de conexión con la API
Verifica que:
1. El backend esté corriendo en `http://127.0.0.1:8000`
2. La URL en `api.js` sea correcta
3. No haya problemas de red o firewall

### Tokens expirados
Los tokens se renuevan automáticamente. Si hay problemas, limpia el `localStorage` y vuelve a iniciar sesión.

## Desarrollo

Para contribuir al proyecto:

1. Crea una rama nueva
2. Realiza tus cambios
3. Prueba exhaustivamente
4. Crea un pull request

## Licencia

Este proyecto es parte del sistema Salud Rural.
