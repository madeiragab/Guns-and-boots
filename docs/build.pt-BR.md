> 🇧🇷 **Português** · 🇬🇧 [English](build.md)

# Guia de Build

## Desktop (executável Windows)

Caminho rápido — a partir da raiz do projeto:

```bat
build.bat
```

Ou manualmente:

```bash
python build.py
```

O que ele faz: compila o jogo com o **PyInstaller** (instalando-o se estiver ausente), copia `assets/` e `save.json` e cria um lançador. Saída:

```text
build_output/
├─ dist/
│  ├─ Guns and Boots.exe
│  ├─ assets/
│  └─ save.json
├─ Jogar.bat        ← dê dois cliques para jogar
└─ README.txt
```

Para atualizar o executável após mudanças no código, basta rodar `build.bat` de novo.

Requisitos: Python 3.7+, pygame (o PyInstaller é instalado automaticamente).

## Mobile (APK Android)

O APK é gerado com o **Buildozer**, que exige Linux (ou WSL):

```bash
pip install buildozer cython
buildozer android debug     # o primeiro build baixa o SDK/NDK do Android — demorado
```

O APK aparece em `bin/`. As configurações (nome do pacote, requisitos, orientação) ficam em `buildozer.spec` — veja `buildozer.spec.example` para um ponto de partida comentado.

No Windows você pode preparar o pacote mobile sem gerar o APK:

```bat
build.bat apk
```

Isso cria `mobile_package/` com instruções para finalizar o build em uma máquina Linux/WSL.

### Build na CI

O `.github/workflows/build-android.yml` gera um APK de debug no GitHub Actions (**disparo manual**: *Actions → Build Android APK → Run workflow*) e o publica como artefato. O build é pesado (SDK + NDK do Android), então não roda a cada push.

## Simulação mobile no desktop

Para testar a interface de toque sem um aparelho:

```bash
python main.py --mobile
```

Resolução em retrato, zonas de toque mapeadas para a navegação por teclado e botões de ação na tela (`ATIRAR`, `COBERTURA`, `ESPECIAL`, `MEDKIT`).

## Smoke test

Verificação de sanidade sem interface (útil na CI e antes de releases):

```bash
python tools/run_test.py
```

Imprime `RUN_OK` em caso de sucesso.
