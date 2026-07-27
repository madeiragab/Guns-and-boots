> 🇧🇷 **Português** · 🇬🇧 [English](combat.md)

# Sistema de Combate

Todas as regras vivem em `systems/combat.py` e `entities/character.py`. Tudo abaixo descreve o comportamento exato do código.

## Ações

A cada turno, um combatente escolhe uma entre quatro ações:

| Ação | Efeito | Calor | Observações |
|---|---|---:|---|
| **ATIRAR** | `atk + rand(-1, 2) − def` de dano (mín. 1) | +2 | Pode travar quando superaquecida |
| **ESPECIAL** | `(atk + rand(2, 5) − def, mín. 1) × 2` de dano | +4 | Cooldown de 2 turnos, mesmo em erro/travamento |
| **COBERTURA** | Bloqueia: −2 de dano recebido e metade da chance de acerto inimiga | −3 | Consumida pelo próximo acerto recebido |
| **MEDKIT** | Cura +10 de HP | 0 | 1 por batalha (reposto por `reset_for_battle`) |

## Chance de acerto

```text
chance = 0.75 + (atacante.atk − defensor.def) × 0.03
chance = clamp(chance, 0.20, 0.95)
se o defensor estiver em cobertura: chance × 0.5
```

Um atacante forte contra um defensor fraco tem teto de 95%; mesmo um confronto desesperador mantém um piso de 20% — nenhum ataque é garantido nem impossível.

## Calor e travamento

O calor é a mecânica de risco/recompensa que impede que sair atirando ATIRAR/ESPECIAL seja sempre o ideal:

- O calor tem teto de **10**. ATIRAR soma 2, ESPECIAL soma 4, COBERTURA remove 3.
- Com **calor ≥ 8** a arma pode **travar** ao disparar:

  | Calor | Chance de travar |
  |---:|---:|
  | 8 | 10% |
  | 9 | 25% |
  | 10 | 40% |

- Um ATIRAR travado desperdiça o turno (+1 de calor). Um ESPECIAL travado desperdiça o turno **e** dispara o cooldown de 2 turnos (+2 de calor).

O loop ideal, portanto, é: pressionar com tiros, ficar de olho no medidor de calor e intercalar COBERTURA — o que ao mesmo tempo resfria a arma, absorve dano e reduz pela metade a chance de acerto do próximo ataque inimigo.

## IA inimiga (`systems/ai.py`)

### Inimigos comuns e chefes

Regras de prioridade, avaliadas de cima para baixo:

1. **HP < 30% e tem medkit** → 65% de chance de se curar.
2. **Calor ≥ 8** → 55% de chance de se cobrir.
3. Caso contrário, um sorteio ponderado:
   - inimigo comum: 70% atirar / 20% cobertura / 10% especial;
   - **chefe**: 45% atirar / 20% cobertura / **35% especial** (mais agressivo);
   - se o especial estiver em cooldown: 75% atirar / 25% cobertura.

### Chefe final (pontuação por utilidade)

O chefe final usa um cérebro diferente (`_choose_final_boss_action`):

1. **Janelas de abate garantido** — se um tiro ou especial pode finalizar o jogador neste turno, ele sempre executa.
2. **Sobrevivência** — abaixo de 25% de HP ele se cura (ou se cobre antes, se estiver superaquecido); com calor ≥ 9 ele resfria, ocasionalmente punindo um jogador ferido com um especial mesmo assim.
3. Caso contrário, cada ação disponível recebe uma **pontuação de dano esperado** (`_expected_damage`) ajustada pelo contexto: especiais valem mais contra um jogador saudável, atirar em quem está coberto é penalizado, curar-se com HP alto é fortemente penalizado.
4. Ele então sorteia entre todas as ações que estejam dentro de 1,0 ponto da melhor pontuação — jogo forte que permanece levemente imprevisível.

## Forma de chefe do jogador (virada na batalha final)

Durante a luta contra o chefe final o jogador pode ativar uma **transformação de uso único** (`Player.activate_final_boss_form`):

- HP máximo × 1,6 + 20 (no mínimo +35), cura total;
- ATK +5 (no mínimo ×1,5), DEF +2 (no mínimo ×1,4);
- +1 medkit, calor zerado, cooldowns limpos;
- sprites e projéteis trocam para a pasta de Chefe correspondente.

Atributos e visuais são restaurados após a batalha (`revert_from_boss_form`).
