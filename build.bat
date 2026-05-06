@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ======================================
echo   Guns and Boots - Build Release
echo ======================================
echo.

rem NOTE: `build.bat apk` prepares a mobile package only — it does NOT build
rem a real APK. Building for Android requires external toolchains (Buildozer
rem or Briefcase) and typically a Linux/WSL environment. See mobile_package\README-mobile.txt
rem after running `build.bat apk` for next steps.

cd /d "%~dp0"

set "PYTHON_EXE=.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

set "ROOT_DIR=%~dp0"
set "DIST_DIR=release"
set "WORK_DIR=build"
set "APP_NAME=Guns and Boots"
set "ASSETS_SRC=%ROOT_DIR%assets"
set "SAVE_SRC=%ROOT_DIR%save.json"
set "APP_DIR=%DIST_DIR%\%APP_NAME%"
set "SAVE_DST=%APP_DIR%\save.json"

if "%~1"=="apk" goto BUILD_APK

echo [*] Verificando PyInstaller...
%PYTHON_EXE% -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Instalando PyInstaller...
    %PYTHON_EXE% -m pip install pyinstaller -q
)

echo [*] Limpando build anterior...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%" >nul 2>&1
if exist "%WORK_DIR%" rmdir /s /q "%WORK_DIR%" >nul 2>&1
if exist "%WORK_DIR%\%APP_NAME%.spec" del /q "%WORK_DIR%\%APP_NAME%.spec" >nul 2>&1

echo [*] Criando diretorios...
mkdir "%DIST_DIR%" 2>nul

echo [*] Compilando com PyInstaller...
echo     (pode levar alguns minutos, nao feche a janela)
echo.

%PYTHON_EXE% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onedir ^
    --windowed ^
    --optimize 2 ^
    --name "%APP_NAME%" ^
    --distpath "%DIST_DIR%" ^
    --workpath "%WORK_DIR%" ^
    --specpath "%WORK_DIR%" ^
    --add-data "%ASSETS_SRC%;assets" ^
    main.py

if %errorlevel% equ 0 (
    echo.
    if not exist "%APP_DIR%" mkdir "%APP_DIR%" >nul 2>&1
    if exist "%SAVE_SRC%" (
        copy /y "%SAVE_SRC%" "%SAVE_DST%" >nul
    ) else (
        > "%SAVE_DST%" (
            echo {
            echo   "unlocked_players": ["Pablo"],
            echo   "defeated_bosses": [],
            echo   "defeated_final_bosses": [],
            echo   "defeated_enemies": [],
            echo   "enemy_round": 0,
            echo   "player_name": "",
            echo   "completed": false
            echo }
        )
    )
    echo.
    echo ======================================
    echo   BUILD CONCLUIDO COM SUCESSO!
    echo ======================================
    echo.
    echo Pasta final: %DIST_DIR%\%APP_NAME%
    echo Executavel: %DIST_DIR%\%APP_NAME%\%APP_NAME%.exe
    echo Save: %SAVE_DST%
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

:BUILD_APK
echo.
echo ======================================
echo   PREPARANDO PACOTE ANDROID (APK)
echo ======================================

set "ANDROID_DIR=%DIST_DIR%\android"
if exist "%ANDROID_DIR%" rmdir /s /q "%ANDROID_DIR%" >nul 2>&1
mkdir "%ANDROID_DIR%" >nul 2>&1

echo [*] Detectando WSL para build nativo Android (recomendado)...
where wsl.exe >nul 2>&1
if %errorlevel%==0 goto WSL_BUILD
goto APK_FALLBACK

:WSL_BUILD
echo [*] WSL encontrado — executando Buildozer dentro do WSL (pode demorar).
echo [*] Entre no processo se solicitado (sudo apt installs).
wsl bash -lc "cd \"$(wslpath '%CD%')\" && sudo apt-get update -y && sudo apt-get install -y --no-install-recommends python3-pip python3-venv openjdk-11-jdk git zip unzip zlib1g-dev libncurses5 libncurses5-dev libffi-dev libssl-dev libsqlite3-dev libjpeg-dev build-essential && python3 -m pip install --user --upgrade pip && python3 -m pip install --user cython buildozer && export PATH=\$HOME/.local/bin:\$PATH && ~/.local/bin/buildozer android debug"

echo [*] Copiando APK(s) gerados para %ANDROID_DIR% ...
if not exist "%ANDROID_DIR%" mkdir "%ANDROID_DIR%" >nul 2>&1
for %%f in ("%CD%\bin\*.apk") do copy /y "%%~f" "%ANDROID_DIR%\" >nul 2>&1
echo [*] Se houver APKs, elas foram copiadas para %ANDROID_DIR%.
goto APK_DONE

:APK_FALLBACK
echo [*] WSL nao encontrado — criando archive do projeto (project.zip) em %ANDROID_DIR% (exclui %DIST_DIR% e .venv)...
powershell -noprofile -command "Get-ChildItem -Path '%ROOT_DIR%' -Force | Where-Object { $_.Name -ne '%DIST_DIR%' -and $_.Name -ne '.venv' } | Compress-Archive -DestinationPath '%ANDROID_DIR%\\project.zip' -Force" >nul 2>&1 || (
    echo [!] Falha ao criar project.zip via PowerShell. Tentando fallback simples...
)
echo [*] Gerando README com instrucoes de build para Android em %ANDROID_DIR% ...

:APK_DONE
(
    echo Build instructions for Android (Kivy/Buildozer or Briefcase):
    echo.
    echo 1) Choose a packaging tool. Recommended: Buildozer (Kivy) on Linux/WSL or Briefcase on Windows.
    echo.
    echo 2) Build with Buildozer (Linux/WSL):
    echo    - Install buildozer, Android SDK/NDK prerequisites
    echo    - Create or adapt buildozer.spec
    echo    - From inside the project folder run: buildozer android debug
    echo.
    echo 3) Build with Briefcase (Windows supported):
    echo    - Install Briefcase and configure Android tooling following its docs
    echo    - Use: briefcase create android && briefcase build android
    echo.
    echo 4) Alternative: transfer the zip (project.zip) to a Linux build host and run Buildozer there.
    echo.
    echo Note: This script only prepares the project. Building an APK requires external toolchains (NDK/SDK) and is not performed here.
) > "%ANDROID_DIR%\README-mobile.txt"

echo [*] Creating compressed project archive for easy transfer...
powershell -noprofile -command "Compress-Archive -Path '%ANDROID_DIR%\project\*' -DestinationPath '%ANDROID_DIR%\project.zip' -Force" >nul 2>&1 || (
    echo [!] Could not create zip via PowerShell; skipping archive.
)

echo.
echo Mobile package prepared: %ANDROID_DIR%
echo Files:
echo   - %ANDROID_DIR%\project    (full project copy)
echo   - %ANDROID_DIR%\project.zip (zipped project, if created)
echo   - %ANDROID_DIR%\README-mobile.txt
echo.
pause
