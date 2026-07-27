> 🇧🇷 **Português** · 🇬🇧 [English](README.md)

# Guns and Boots

Um jogo 2D retrofuturista por turnos feito em Python e Pygame — com mecânica de aposta baseada em superaquecimento/travamento da arma, IA inimiga baseada em regras e um sistema de transformação para a batalha final.

**Feito por Gabriel Madeira**

> Projeto desenvolvido para a disciplina de **Tópicos Especiais** do curso de **Ciência da Computação** do **IFSulDeMinas**.

## Documentação

| Documento | O que contém |
|---|---|
| [docs/architecture.pt-BR.md](docs/architecture.pt-BR.md) | Camadas, máquina de estados, loop principal, áudio, sistema de save |
| [docs/combat.pt-BR.md](docs/combat.pt-BR.md) | Todas as fórmulas de combate: chance de acerto, calor/travamento, IA |
| [docs/adding-characters.pt-BR.md](docs/adding-characters.pt-BR.md) | Como adicionar personagens/chefes sem mexer no código |
| [docs/build.pt-BR.md](docs/build.pt-BR.md) | Build do .exe no Windows, APK Android, CI |

---

## Requisitos

```bash
pip install pygame
```

## Como Rodar

```bash
python main.py
```

Instalar as dependências pelo arquivo do projeto:

```bash
pip install -r requirements.txt
```

## Build e Mobile (rápido)

O projeto tem um fluxo de release para desktop e um pacote mobile preparado.

- Rodar localmente (desktop):

```powershell
python main.py
```

- Rodar em modo de simulação mobile (ajusta UI/entrada para toque):

```powershell
python main.py --mobile
```

- Criar um release para Windows (usa o virtualenv do projeto, se existir):

```powershell
.\build.bat
```

- Preparar o pacote mobile (não gera o APK; cria `mobile_package` com instruções):

```powershell
.\build.bat apk
```

Observações:
- Gerar um APK exige toolchains externas (Buildozer ou Briefcase) e não é feito automaticamente pelo `build.bat`.
- O arquivo `mobile_package/README-mobile.txt` traz os passos para continuar em um ambiente Linux/WSL ou outro com suporte a Android.

Controles de toque (modo mobile):
- Toque nos botões de ação na parte de baixo: `ATIRAR`, `COBERTURA`, `ESPECIAL`, `MEDKIT`.
- Menus: toque nos itens para selecionar; os botões `OK` / `DEL` aparecem na tela de digitação do nome.

Teste rápido (smoke test sem interface):

```powershell
& .venv\Scripts\python.exe tools/run_test.py
```
Deve imprimir `RUN_OK` quando bem-sucedido.

---

## Controles

| Tecla | Ação |
|---|---|
| Cima / Baixo | Navegar nos menus |
| Esquerda / Direita | Navegar na seleção de personagem |
| Enter | Confirmar |
| Esc | Voltar / Sair |

---

## Fluxo do Jogo

```text
Tela de Título
  |- (sem save) -> Digitar nome -> Escolher personagem -> Hub
  '- (com save) -> CONTINUAR (nome salvo) ou NOVO JOGO

Hub
  |- BATALHA -> enfrenta inimigos comuns em sequência
  |- TROCAR PERSONAGEM -> volta para a seleção de personagem
  '- SAIR

Batalha vs Inimigos -> Resultado -> próximo inimigo
  '- todos derrotados -> tela de PERIGO -> Batalha de Chefe

Batalha de Chefe -> Resultado
  '- todos os chefes derrotados -> Créditos -> Tela de Título (modo livre salvo)

Modo Livre (após terminar o jogo)
  '- Hub -> BATALHA sorteia um chefe aleatório indefinidamente
```

---

## Sistemas

### Máquina de Estados (`core/state_manager.py`)
Trata todas as telas como estados empilháveis. Suporta `change`, `push` e `pop`. Toda transição de estado avisa o objeto `Game`, para que a trilha sonora seja atualizada automaticamente.

### Sistema de Save (`core/game.py`)
Salva e carrega o progresso pelo `save.json`:
- Nome do jogador
- Personagens desbloqueados
- Chefes derrotados
- Progressão das rodadas de inimigos
- Flag `completed` para o modo pós-jogo

Ao terminar o jogo, o save é mantido com `completed = True` e todos os personagens desbloqueados. O save só é apagado se o jogador escolher `NOVO JOGO` na tela de título.

### Sistema de Combate (`systems/combat.py`)
Combate por turnos com as seguintes ações:

| Ação | Efeito | Calor |
|---|---|---:|
| ATIRAR | `atk + rand(-1,2) - def do inimigo` | +2 |
| COBERTURA | Reduz o dano recebido e diminui a chance de acerto contra o defensor | -3 |
| ESPECIAL | `(atk + rand(2,5) - def) * 2` | +4 |
| MEDKIT | Recupera HP (1 uso por batalha) | 0 |

**Sistema de Calor / Travamento:** quando o calor está `>= 8`, a arma pode travar. A cobertura ajuda a resfriar a arma.

### IA Inimiga (`systems/ai.py`)
IA baseada em regras que considera:
- HP atual -> se cura quando muito ferida
- Calor da arma -> usa cobertura quando superaquecida
- Tipo do inimigo -> chefes usam especiais de forma mais agressiva

O **chefe final** usa um cérebro separado, com pontuação por utilidade: ele detecta janelas de abate garantido, pondera o dano esperado por ação e se mantém levemente imprevisível escolhendo entre opções quase ótimas. Detalhes em [docs/combat.pt-BR.md](docs/combat.pt-BR.md).

### Batalha Final e Forma de Chefe (`entities/final_boss.py`, `states/final_danger_state.py`)
Depois que todos os chefes caem, começa um gauntlet final. Durante a batalha final o jogador pode ativar uma **transformação em forma de chefe, de uso único** — uma mecânica de virada que aumenta os atributos, zera calor/cooldowns e troca os sprites pelos visuais de chefe do personagem. Tudo é revertido ao fim da batalha.

### Animador de Sprites (`core/sprite_animator.py` e `ui/sprite_loader.py`)
Carrega frames PNG de subpastas como `idle`, `shoot`, `cover`, `damage`, `medkit` e `special/anim`. Suporta animações em loop e de execução única com retorno automático ao idle, além de escala, colorkey e FPS configurável.

### Sistema de Projéteis (`entities/projectile.py`)
Os projéteis viajam do atacante até o alvo em tempo real (`0.35s`). O dano só é resolvido quando o projétil alcança o alvo, através do callback `on_hit`.

### Sistema de Áudio (`core/game.py`)
Gerenciado centralmente pelo objeto `Game`:
- `theme.mp3` -> em loop na tela de título e nos créditos
- `battle music1.mp3` / `battle music2.mp3` -> sorteadas para as batalhas
- `bullet.mp3` -> efeito sonoro do tiro comum
- `special.mp3` -> efeito sonoro da habilidade especial

### Personagens e Chefes
Carregados dinamicamente de `assets/sprites/Players/` e `assets/sprites/Bosses/`. Cada pasta de personagem contém suas próprias subpastas de animação. Novos personagens podem ser adicionados criando uma nova pasta, sem alterações no código.

Chefes derrotados são desbloqueados como personagens jogáveis.

---

## Estrutura do Projeto

```text
Guns and boots/
|- main.py                  - ponto de entrada
|- requirements.txt         - dependências
|- README.md
|- .gitignore
|
|- core/                    - camada de engine do jogo
|  |- game.py               - janela, loop principal, áudio, sistema de save
|  |- state_manager.py      - máquina de estados push/pop/change
|  '- sprite_animator.py    - animador de sprites por frames
|
|- entities/                - objetos de gameplay
|  |- character.py          - atributos base, calor, travamento, cobertura
|  |- player.py             - personagem do jogador + forma de chefe
|  |- enemy.py              - inimigos comuns
|  |- boss.py               - chefes
|  |- final_boss.py         - chefes finais
|  '- projectile.py         - projétil animado com callback on_hit
|
|- states/                  - telas / estados do jogo
|  |- base_state.py
|  |- title_state.py        - tela de título
|  |- name_state.py         - digitação do nome
|  |- select_state.py       - seleção de personagem
|  |- hub_state.py          - hub / menu principal
|  |- battle_state.py       - batalha por turnos
|  |- danger_state.py       - transição antes da luta de chefe
|  |- final_danger_state.py - transição antes do gauntlet final
|  |- result_state.py       - tela de resultado da batalha
|  '- credits_state.py      - tela final de créditos
|
|- systems/                 - lógica de gameplay desacoplada
|  |- combat.py             - resolve_action(), chance de acerto, dano
|  '- ai.py                 - IA inimiga baseada em regras
|
|- ui/                      - componentes visuais de interface
|  |- button.py
|  |- healthbar.py
|  |- logbox.py
|  '- sprite_loader.py
|
|- assets/
|  |- sfx/                  - músicas e efeitos sonoros
|  |  |- theme.mp3
|  |  |- battle music1.mp3
|  |  |- battle music2.mp3
|  |  |- bullet.mp3
|  |  '- special.mp3
|  '- sprites/
|     |- Players/           - personagens jogáveis
|     |- Bosses/            - chefes
|     |- Enemy/             - inimigos comuns
|     |- field/             - cenários de batalha
|     '- bullet/            - frames do projétil padrão
|
'- tools/                   - scripts de desenvolvimento
   |- run_combat_debug.py   - simulação de combate no terminal
   |- run_test.py           - smoke test sem interface
   '- sprite_demo.py        - visualizador interativo de sprites
```
