# Instrucciones para subir cambios a GitHub

## Opción 1: Usar el script automático (Recomendado)

1. **Ejecuta el archivo `subir_github.bat`** haciendo doble clic sobre él
2. El script te guiará paso a paso

## Opción 2: Comandos manuales en Git Bash

Si tienes Git Bash instalado:

1. **Abre Git Bash**
2. **Navega al proyecto:**
   ```bash
   cd "C:\Users\ACER NITR 5\clondali\saludrural"
   ```

3. **Verifica el estado:**
   ```bash
   git status
   ```

4. **Agrega todos los cambios:**
   ```bash
   git add .
   ```

5. **Crea un commit:**
   ```bash
   git commit -m "feat: Agregar frontend completo con React + Vite + Tailwind CSS

   - Sistema de autenticación JWT completo
   - Dashboard con estadísticas según rol de usuario
   - Gestión de citas, pacientes y médicos
   - Perfil de usuario con cambio de contraseña
   - UI moderna y responsiva con Tailwind CSS
   - Integración completa con API backend Django
   - Correcciones de errores 405 y 403
   - Manejo correcto de permisos según rol
   - Eliminación de endpoints inexistentes"
   ```

6. **Sube los cambios:**
   ```bash
   git push
   ```

## Opción 3: Usar GitHub Desktop

Si tienes GitHub Desktop instalado:

1. Abre GitHub Desktop
2. Selecciona el repositorio `saludrural`
3. Verás todos los archivos modificados en la pestaña "Changes"
4. Escribe un mensaje de commit
5. Haz clic en "Commit to main"
6. Haz clic en "Push origin" para subir los cambios

## Opción 4: Usar Visual Studio Code

Si usas VS Code:

1. Abre la carpeta del proyecto en VS Code
2. Ve a la pestaña "Source Control" (icono de ramificación en la barra lateral)
3. Verás todos los archivos modificados
4. Escribe un mensaje de commit en el campo superior
5. Haz clic en el icono de ✓ para hacer commit
6. Haz clic en "..." (tres puntos) y selecciona "Push"

## Si el repositorio remoto no está configurado

Si es la primera vez que subes este proyecto:

1. **Crea un repositorio en GitHub:**
   - Ve a https://github.com
   - Haz clic en "New repository"
   - Dale un nombre (ej: "saludrural")
   - **NO** inicialices con README, .gitignore o licencia (ya existen)

2. **Conecta el repositorio local con el remoto:**
   ```bash
   git remote add origin https://github.com/TU_USUARIO/saludrural.git
   git branch -M main
   git push -u origin main
   ```

   Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub.

## Verificar que todo está bien

Después de hacer push, verifica:

1. Ve a tu repositorio en GitHub
2. Deberías ver todos los archivos del frontend
3. Verifica que el commit aparezca en el historial

## Archivos que se subirán

- Todo el directorio `frontend/` con:
  - Configuración de Vite
  - Componentes React
  - Páginas (Dashboard, Citas, Pacientes, etc.)
  - Servicios API
  - Estilos con Tailwind CSS
  - Documentación (README.md)

- Archivos de configuración:
  - `.gitignore` (actualizado)
  - Archivos de configuración del proyecto

## Nota importante

Los siguientes archivos NO se subirán (están en .gitignore):
- `node_modules/`
- Archivos compilados (`dist/`)
- Variables de entorno (`.env`)
- Archivos temporales

¡Listo! Sigue cualquiera de estas opciones para subir tus cambios a GitHub.
