#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script simplificado para compilar o jogo em exe.
Uso: python build.py
"""

import io
import sys
import os
import shutil
import subprocess

# Forca saida em UTF-8
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except:
    pass

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(PROJECT_ROOT, "build_output")
DIST_DIR = os.path.join(BUILD_DIR, "dist")
MAIN_FILE = os.path.join(PROJECT_ROOT, "main.py")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
SAVE_FILE = os.path.join(PROJECT_ROOT, "save.json")

def log(msg):
    print(f"[*] {msg}")

def main():
    try:
        log("Iniciando build...")
        
        # 1. Verificar PyInstaller
        log("Verificando PyInstaller...")
        result = subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"],
                                capture_output=True)
        if result.returncode != 0:
            log("Instalando PyInstaller...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])
        
        # 2. Limpar build anterior
        log("Limpando build anterior...")
        if os.path.exists(BUILD_DIR):
            shutil.rmtree(BUILD_DIR)
        if os.path.exists(os.path.join(PROJECT_ROOT, "build")):
            shutil.rmtree(os.path.join(PROJECT_ROOT, "build"))
        if os.path.exists(os.path.join(PROJECT_ROOT, "main.spec")):
            os.remove(os.path.join(PROJECT_ROOT, "main.spec"))
        
        # 3. Criar diretório de build
        os.makedirs(DIST_DIR, exist_ok=True)
        
        # 4. Compilar com PyInstaller
        log("Compilando com PyInstaller (isso pode levar alguns minutos)...")
        log("")
        
        cmd = [
            sys.executable,
            "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", "Guns and Boots",
            "--distpath", DIST_DIR,
            "--workpath", os.path.join(BUILD_DIR, "work"),
            "--specpath", BUILD_DIR,
            "--add-data", f"{ASSETS_DIR}{os.pathsep}assets",
            MAIN_FILE
        ]
        
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        log("")
        
        if result.returncode != 0:
            raise RuntimeError("Erro ao compilar com PyInstaller")
        
        # 5. Copiar arquivo de save
        log("Copiando arquivos...")
        if os.path.exists(SAVE_FILE):
            shutil.copy(SAVE_FILE, os.path.join(DIST_DIR, "save.json"))
        
        # 6. Criar inicializador
        launcher_bat = os.path.join(BUILD_DIR, "Jogar.bat")
        with open(launcher_bat, "w") as f:
            f.write(f"""@echo off
cd /d "{DIST_DIR}"
"Guns and Boots.exe"
""")
        
        # 7. Sucesso
        log("")
        log("="*60)
        log("BUILD CONCLUIDO COM SUCESSO!")
        log("="*60)
        log(f"Executavel: {os.path.join(DIST_DIR, 'Guns and Boots.exe')}")
        log(f"Launcher: {launcher_bat}")
        log(f"Tudo em: {BUILD_DIR}")
        log("")
        
    except Exception as e:
        log(f"ERRO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
