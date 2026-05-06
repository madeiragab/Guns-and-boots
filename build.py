#!/usr/bin/env python3
"""
Build script para compilar o jogo em exe usando PyInstaller.
Uso: python build.py
"""

import os
import shutil
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(PROJECT_ROOT, "build_output")
DIST_DIR = os.path.join(BUILD_DIR, "dist")
MAIN_FILE = os.path.join(PROJECT_ROOT, "main.py")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
SAVE_FILE = os.path.join(PROJECT_ROOT, "save.json")
SAVE_DST = os.path.join(DIST_DIR, "save.json")

def print_status(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")

def install_pyinstaller():
    """Instala PyInstaller se nao estiver instalado."""
    try:
        import PyInstaller
        print("[OK] PyInstaller ja esta instalado")
    except ImportError:
        print_status("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def clean_build():
    """Limpa build anterior."""
    print_status("Limpando build anterior...")
    
    for path in [BUILD_DIR, os.path.join(PROJECT_ROOT, "build"), os.path.join(PROJECT_ROOT, "main.spec")]:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"[OK] Removido: {path}")
            except Exception as e:
                print(f"[AVISO] {e}")

def build_exe():
    """Compila o exe com PyInstaller."""
    print_status("Compilando exe com PyInstaller...")
    
    os.makedirs(BUILD_DIR, exist_ok=True)
    os.makedirs(os.path.join(BUILD_DIR, "build_temp"), exist_ok=True)
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "-F", "-w",
        "--name", "Guns and Boots",
        "--distpath", DIST_DIR,
        "--workpath", os.path.join(BUILD_DIR, "build_temp"),
        "--specpath", BUILD_DIR,
        "--add-data", ASSETS_DIR + os.pathsep + "assets",
        MAIN_FILE
    ]
    
    print("[DEBUG] Executando PyInstaller...")
    result = subprocess.call(cmd)
    if result != 0:
        raise RuntimeError(f"PyInstaller falhou com codigo: {result}")
    print("\n[OK] Compilacao concluida!")

def copy_files():
    """Copia save.json e cria launcher."""
    print_status("Finalizando...")
    
    os.makedirs(DIST_DIR, exist_ok=True)
    
    if os.path.exists(SAVE_FILE):
        shutil.copy(SAVE_FILE, SAVE_DST)
        print("[OK] Save copiado")
    else:
        with open(SAVE_DST, "w", encoding="utf-8") as f:
            f.write('{' + '\n')
            f.write('  "unlocked_players": ["Pablo"],\n')
            f.write('  "defeated_bosses": [],\n')
            f.write('  "defeated_final_bosses": [],\n')
            f.write('  "defeated_enemies": [],\n')
            f.write('  "enemy_round": 0,\n')
            f.write('  "player_name": "",\n')
            f.write('  "completed": false\n')
            f.write('}' + '\n')
        print("[OK] Save padrao criado")
    
    launcher = os.path.join(BUILD_DIR, "Jogar.bat")
    with open(launcher, "w") as f:
        f.write(f'@echo off\ncd /d "{DIST_DIR}"\nstart "" "Guns and Boots.exe"\n')
    print(f"[OK] Launcher criado: {launcher}")
    
    readme = os.path.join(BUILD_DIR, "README.txt")
    with open(readme, "w") as f:
        f.write("GUNS AND BOOTS\n\nExecute Jogar.bat para jogar.\nPara recompilar: python build.py\n")
    print(f"[OK] README criado")

def main():
    try:
        print_status("GUNS AND BOOTS - BUILD EXE")
        install_pyinstaller()
        clean_build()
        build_exe()
        copy_files()
        
        print_status("SUCESSO!")
        print(f"[INFO] Executavel: {os.path.join(DIST_DIR, 'Guns and Boots.exe')}")
        print(f"[INFO] Para jogar: {os.path.join(BUILD_DIR, 'Jogar.bat')}\n")
        return 0
        
    except Exception as e:
        print_status(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
