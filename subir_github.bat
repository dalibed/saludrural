@echo off
echo ========================================
echo Subiendo cambios a GitHub
echo ========================================
echo.

REM Cambiar al directorio del proyecto
cd /d "C:\Users\ACER NITR 5\clondali\saludrural"

REM Verificar si git está instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git no está instalado o no está en el PATH
    echo.
    echo Por favor:
    echo 1. Instala Git desde https://git-scm.com/download/win
    echo 2. O abre Git Bash y ejecuta estos comandos manualmente:
    echo    cd "C:\Users\ACER NITR 5\clondali\saludrural"
    echo    git add .
    echo    git commit -m "feat: Agregar frontend completo y correcciones de errores"
    echo    git push
    pause
    exit /b 1
)

echo Verificando estado del repositorio...
git status

echo.
echo ¿Deseas continuar con el commit y push? (S/N)
set /p continuar=

if /i not "%continuar%"=="S" (
    echo Operación cancelada.
    pause
    exit /b 0
)

echo.
echo Agregando archivos...
git add .

echo.
echo Creando commit...
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

echo.
echo ¿Deseas hacer push al repositorio remoto? (S/N)
set /p hacer_push=

if /i "%hacer_push%"=="S" (
    echo.
    echo Subiendo cambios a GitHub...
    git push
    
    if errorlevel 1 (
        echo.
        echo ERROR: No se pudo hacer push. Verifica:
        echo 1. Que tengas un repositorio remoto configurado
        echo 2. Que tengas permisos de escritura
        echo 3. Que la rama remota exista
        echo.
        echo Para configurar el remoto (si no está configurado):
        echo git remote add origin URL_DEL_REPOSITORIO
        echo git push -u origin main
    ) else (
        echo.
        echo ¡Cambios subidos exitosamente!
    )
) else (
    echo.
    echo Commit creado localmente. Puedes hacer push más tarde con:
    echo git push
)

echo.
pause
