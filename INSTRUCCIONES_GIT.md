# Instrucciones para subir cambios al repositorio

## Si Git está instalado pero no está en el PATH:

1. Abre PowerShell o CMD como administrador
2. Navega a la carpeta del proyecto:
```cmd
cd "C:\Users\ACER NITR 5\clondali\saludrural"
```

3. Ejecuta los siguientes comandos:

### Si es un repositorio nuevo:
```cmd
git init
git add .
git commit -m "feat: Agregar frontend completo con React + Vite + Tailwind CSS

- Sistema de autenticación JWT completo
- Dashboard con estadísticas
- Gestión de citas, pacientes y médicos
- Perfil de usuario con cambio de contraseña
- UI moderna y responsiva con Tailwind CSS
- Integración completa con API backend Django"
```

### Si ya es un repositorio existente:
```cmd
git add .
git commit -m "feat: Agregar frontend completo con React + Vite + Tailwind CSS

- Sistema de autenticación JWT completo
- Dashboard con estadísticas
- Gestión de citas, pacientes y médicos
- Perfil de usuario con cambio de contraseña
- UI moderna y responsiva con Tailwind CSS
- Integración completa con API backend Django"

git push origin main
```

## Si necesitas configurar Git por primera vez:

```cmd
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

## Si el repositorio remoto aún no está configurado:

1. Crea un repositorio en GitHub/GitLab/Bitbucket
2. Conecta el repositorio local con el remoto:
```cmd
git remote add origin URL_DEL_REPOSITORIO
git branch -M main
git push -u origin main
```

## Resumen de cambios incluidos:

✅ Frontend completo con React + Vite
✅ Configuración de Tailwind CSS
✅ Sistema de autenticación JWT
✅ Dashboard, Citas, Pacientes, Médicos, Perfil
✅ Servicios API para conexión con backend
✅ Componentes reutilizables
✅ Enrutamiento y navegación
✅ Documentación (README.md)

## Nota importante:

Asegúrate de que el archivo `.gitignore` esté configurado correctamente para excluir:
- `node_modules/`
- `dist/`
- Archivos `.env`
- Archivos compilados de Python (`__pycache__/`)
- Archivos de base de datos

Los cambios ya están guardados en tu sistema de archivos local y listos para ser subidos al repositorio.
