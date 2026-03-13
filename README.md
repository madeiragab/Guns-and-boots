# Guns and Boots

Jogo tático 2D por turnos com estética retro-futurista, desenvolvido em Python com Pygame.

**Feito por Gabriel Madeira**

> Projeto desenvolvido para a disciplina de **Tópicos Especiais** do curso de **Ciência da Computação** do **IFSulDeMinas**.

---

## Requisitos

```
pip install pygame
```

## Como rodar

```
python main.py
```

---

## Controles

| Tecla       | Ação                          |
|-------------|-------------------------------|
| ↑ / ↓       | Navegar menus                 |
| ← / →       | Navegar seleção de personagem |
| ENTER       | Confirmar                     |
| ESC         | Voltar / Sair                 |

---

## Fluxo do jogo

```
Título
  ├── (sem save) → Digitar nome → Escolher personagem → Hub
  └── (com save) → CONTINUAR (nome salvo) ou NOVO JOGO

Hub
  ├── BATALHA        → enfrenta inimigos comuns em sequência
  ├── TROCAR PERSONAGEM → volta para seleção de personagem
  └── SAIR

Batalha vs inimigos → Resultado → próximo inimigo
  └── todos derrotados → tela PERIGO → Batalha vs Chefe

Batalha vs Chefe → Resultado
  └── todos os chefes derrotados → Créditos → Título (modo livre salvo)

Modo Livre (após zerar):
  └── Hub → BATALHA sorteia chefe aleatório indefinidamente
```

---

## Sistemas

### State Machine (`core/state_manager.py`)
Gerencia todas as telas como estados empilháveis. Suporta `change` (troca), `push` (empilha) e `pop` (desempilha). A cada transição, notifica o objeto `Game` para trocar a trilha sonora automaticamente.

### Save System (`core/game.py`)
Salva e carrega progresso em `save.json`:
- Nome do jogador
- Personagens desbloqueados
- Chefes derrotados
- Round de inimigos
- Flag `completed` (jogo zerado)

Ao zerar, o save é **mantido** com `completed = True` e todos os personagens desbloqueados. O save só é **apagado** se o jogador escolher "NOVO JOGO" na tela de título.

### Sistema de Combate (`systems/combat.py`)
Combate por turnos com as ações:

| Ação        | Efeito                                           | Calor |
|-------------|--------------------------------------------------|-------|
| ATIRAR      | `atk + rand(-1,2) - def` do inimigo              | +2    |
| COBERTURA   | Reduz dano recebido; chance de acerto cai 50%    | -3    |
| ESPECIAL    | `(atk + rand(2,5) - def) × 2`                   | +4    |
| MEDKIT      | Recupera HP (1 uso por batalha)                  |  0    |

**Sistema de Calor / Jam:** calor ≥ 8 gera chance de a arma travar (10% no 8, +15% por ponto acima). Cobertura resfria a arma.

### IA dos Inimigos (`systems/ai.py`)
IA baseada em regras que considera:
- HP atual → cura se < 30%
- Calor da arma → cobertura se superaquecida
- Tipo (Chefe vs normal) → chefes usam especial com mais frequência

### Sprite Animator (`core/sprite_animator.py` e `ui/sprite_loader.py`)
Carrega frames PNG de subpastas (idle, shoot, cover, damage, medkit, special/anim) e anima em loop ou one-shot com retorno automático ao idle. Suporta escala, colorkey e FPS configurável.

### Projetil (`entities/projectile.py`)
Projetis voam do atirador ao alvo em tempo real (0.35s). O dano só é resolvido ao atingir o alvo via callback `on_hit`, separando a animação visual da lógica de combate.

### Sistema de Áudio (`core/game.py`)
Gerenciado centralmente pelo objeto `Game`:
- **theme.mp3** → toca em loop no Título e Créditos
- **battle music1/2.mp3** → escolhida aleatoriamente a cada batalha
- **bullet.mp3** → SFX de tiro normal
- **special.mp3** → SFX de habilidade especial

### Personagens e Chefes
Carregados dinamicamente das pastas `assets/sprites/Players/` e `assets/sprites/Bosses/`. Cada pasta de personagem contém subpastas de animação. Novos personagens são adicionados só criando a pasta — nenhuma alteração de código necessária.

Chefes derrotados são desbloqueados como personagens jogáveis.

---

## Estrutura do projeto

```
main.py
core/
    game.py              – janela, loop principal (60 FPS), áudio, save
    state_manager.py     – máquina de estados push/pop/change
    sprite_animator.py   – animador de sprites por frames
    state_manager.py     – gerenciador de estados
entities/
    character.py         – stats base, calor, jam, cobertura
    player.py            – personagem controlado pelo jogador
    enemy.py             – inimigos comuns (carregados de pasta)
    boss.py              – chefes (carregados de pasta)
    projectile.py        – projetil animado com callback on_hit
states/
    base_state.py        – classe base dos estados
    title_state.py       – Título (com menu continuar/novo jogo)
    name_state.py        – Digitar nome
    select_state.py      – Seleção de personagem
    hub_state.py         – Menu principal / hub
    battle_state.py      – Batalha por turnos
    danger_state.py      – Tela de transição para chefe
    result_state.py      – Resultado da batalha
    credits_state.py     – Créditos finais
systems/
    combat.py            – resolve_action(), hit chance, dano
    ai.py                – IA rule-based dos inimigos
ui/
    button.py            – botão navegável
    healthbar.py         – barra de HP com cor dinâmica
    logbox.py            – log de combate
    sprite_loader.py     – carregador/animador de sprites para UI
assets/
    fonts/
    sfx/
        theme.mp3
        battle music1.mp3
        battle music2.mp3
        bullet.mp3
        special.mp3
    sprites/
        Players/         – personagens jogáveis (pasta por personagem)
        Bosses/          – chefes (pasta por chefe)
        Enemy/           – inimigos comuns (pasta por tipo)
        field/           – fundos de batalha (escolhido aleatoriamente)
        bullet/          – frames do projetil padrão
```

---

## Agradecimentos

ChatGPT, Professor Ricardo, e os amigos: Caruzo, Eliandro, Guel

| OVERCHARGE | atk + rand(2,5) – enemy.def               | +4   |
| MEDKIT     | +10 HP (limited to 3 per battle)          |  0   |

Heat ≥ 8 → chance of weapon jam (attack fails).
