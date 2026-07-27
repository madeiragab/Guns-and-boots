> 🇧🇷 **Português** · 🇬🇧 [English](adding-characters.md)

# Adicionando Personagens, Chefes e Inimigos

Os personagens são **descobertos no sistema de arquivos em tempo de execução** — nenhuma alteração de código é necessária. Solte uma pasta nova com a estrutura correta e o jogo a reconhece.

## Estrutura de pastas

```text
assets/sprites/
├─ Players/
│  └─ <NomeDoPersonagem>/       ← nome da pasta = nome dentro do jogo
│     ├─ idle/       idle0.png, idle1.png, ...      (em loop)
│     ├─ shoot/      ...                            (execução única)
│     ├─ cover/      ...
│     ├─ damage/     ...
│     ├─ medkit/     ...
│     └─ special/
│        ├─ anim/    frames da animação do ataque especial
│        └─ bullet/  frames do projétil especial (tamanho natural)
├─ Bosses/
│  └─ <NomeDoChefe>/            ← mesma estrutura de Players
├─ Enemy/                       ← inimigos comuns
├─ field/                       ← cenários de batalha
└─ bullet/                      ← frames do projétil padrão (compartilhado)
```

## Regras e comportamento

- Os **frames** são arquivos PNG carregados em ordem alfabética — use nomes com zeros à esquerda (`idle00.png`, `idle01.png`…) para manter a ordem estável.
- As animações rodam a **12 FPS**; `idle` fica em loop, todas as outras tocam uma vez e voltam ao idle automaticamente.
- Frames de jogador/chefe são escalados para **160×160**; o preto puro `(0, 0, 0)` é usado como colorkey de transparência.
- Pastas ausentes não são problema: se `special/bullet/` não existir, o projétil padrão compartilhado é usado; se um personagem não tiver nenhuma animação, um placeholder sólido é renderizado em vez de o jogo quebrar.
- **Desbloqueio de chefes**: chefes derrotados na campanha se tornam jogáveis — o jogo os desbloqueia pelo nome, então uma pasta em `Bosses/<Nome>` que corresponda a uma pasta `Players/<Nome>` dá ao personagem os visuais de forma de chefe usados na transformação da batalha final.
- O personagem inicial é definido por `DEFAULT_STARTER_PLAYER` em `core/game.py` (padrão: `Pablo`). As escalações obrigatórias de batalha ficam em `states/final_danger_state.py` (`MANDATORY_BOSSES`, `MANDATORY_FINAL_BOSSES`).

## Checklist para um novo personagem jogável

1. Crie `assets/sprites/Players/MeuPersonagem/` com pelo menos uma pasta `idle/`.
2. Adicione `shoot/`, `cover/`, `damage/`, `medkit/`, `special/anim/` e `special/bullet/` conforme produzir a arte.
3. Rode o visualizador de sprites para conferir o resultado:

   ```bash
   python tools/sprite_demo.py
   ```

4. Desbloqueie o personagem no jogo (terminando a campanha) ou adicione-o temporariamente em `unlocked_players` no `save.json` para testar.
