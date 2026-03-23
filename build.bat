@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ======================================
echo   Guns and Boots - Build Exe
echo ======================================
echo.

cd /d "%~dp0"

echo [*] Verificando PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Instalando PyInstaller...
    python -m pip install pyinstaller -q
)

echo [*] Limpando build anterior...
if exist "build_output" rmdir /s /q "build_output" >nul 2>&1

echo [*] Criando diretorios...
mkdir "build_output\dist" 2>nul

echo [*] Compilando com PyInstaller...
echo     (pode levar alguns minutos, nao feche a janela)
echo.

python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "Guns and Boots" ^
    --distpath "build_output\dist" ^
    --workpath "build_output\work" ^
    --specpath "build_output" ^
    --add-data "assets\;assets\" ^
    main.py

if %errorlevel% equ 0 (
    echo.
    echo [*] Copiando arquivos...
    if exist "save.json" copy "save.json" "build_output\dist\save.json" >nul
    
    echo [*] Criando launcher...
    (
        echo @echo off
        echo cd /d "%%%%~dp0dist"
        echo "Guns and Boots.exe"
    ) > "build_output\Jogar.bat"
    
    echo.
    echo ======================================
    echo   BUILD CONCLUIDO COM SUCESSO!
    echo ======================================
    echo.
    echo Executavel: build_output\dist\Guns and Boots.exe
    echo Launcher: build_output\Jogar.bat
    echo.
    pause
) else (
    echo.
    echo ======================================
    echo   ERRO NA COMPILACAO!
    echo ======================================
    echo.
    pause
)
