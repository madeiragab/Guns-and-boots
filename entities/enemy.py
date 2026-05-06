import os
import pygame

from entities.character import Character
from entities.projectile import load_bullet_frames
from core.sprite_animator import load_animations_from_folders, SpriteAnimator
from core.paths import get_asset_path


class Enemy(Character):
    """AI-controlled enemy."""

    PROFILES = {
        "GRUNT": {
            "hp": 22, "atk": 5, "defense": 1,
            "sprite": None,
        },
        "HEAVY": {
            "hp": 35, "atk": 8, "defense": 3,
            "sprite": None,
        },
        "SNIPER": {
            "hp": 18, "atk": 10, "defense": 1,
            "sprite": None,
        },
    }

    def __init__(self, profile="GRUNT", level=0):
        # Salva o nome original da pasta para rastreamento (nunca sobrescrito pelo meta)
        self.folder_name = profile
        self.level = level
        # Se o perfil corresponder a um perfil conhecido, usa esses atributos.
        data = self.PROFILES.get(profile)
        display_name = profile
        # Tambem permite sobrescrever atributos com um meta.json opcional dentro da pasta do inimigo
        # Caminho: assets/sprites/Enemy/<profile>/meta.json
        meta_path = None
        try:
            base = get_asset_path("sprites", "Enemy")
            folder = os.path.join(base, profile)
            meta_path = os.path.join(folder, "meta.json")
            if os.path.isfile(meta_path):
                import json
                with open(meta_path, "r", encoding="utf-8") as fh:
                    meta = json.load(fh)
                # mescla meta em data (valores de meta sobrescrevem)
                if data is None:
                    data = {}
                data.update({k: meta[k] for k in ("hp", "atk", "defense") if k in meta})
                # permite renomear (apenas exibicao)
                if "name" in meta:
                    display_name = meta["name"]
        except Exception:
            pass

        if data is None:
            # Perfil desconhecido (provavelmente nome de pasta). Usa padroes sensatos.
            data = {"hp": 22, "atk": 5, "defense": 1, "sprite": None}

        super().__init__(
            name=display_name,
            hp=data["hp"] + level * 5,
            atk=data["atk"] + level * 1,
            defense=data["defense"] + level * 1,
        )
        self.profile = self.folder_name

        # Tenta carregar animacoes de assets/sprites/Enemy/<profile>/
        try:
            base = get_asset_path("sprites", "Enemy")
            path = os.path.join(base, self.folder_name)
            animations = {}
            if os.path.isdir(path):
                animations = load_animations_from_folders(path, scale=1, colorkey=(0, 0, 0), target_size=(160, 160))

            # Se encontrar, inverte os quadros horizontalmente (inimigos olham para a esquerda)
            if animations:
                for k, frames in animations.items():
                    for i, f in enumerate(frames):
                        try:
                            animations[k][i] = pygame.transform.flip(f, True, False)
                        except Exception:
                            pass

        except Exception:
            animations = {}

        if not animations:
            # marcador padrao de reserva
            s = pygame.Surface((160, 160), pygame.SRCALPHA)
            s.fill((80, 80, 80, 255))
            animations = {"idle": [s]}

        self.animator = SpriteAnimator(animations, default="idle", fps=12, return_to_idle=True)

        # Carrega quadros do projetil (invertidos para a direcao do inimigo)
        self.bullet_frames = load_bullet_frames(flip=True)
        self.special_bullet_frames = self.bullet_frames

    def play(self, action):
        action = action if action in self.animator.animations else "idle"
        loop = (action == "idle")
        self.animator.play(action, loop=loop, reset=True)

    def update(self, dt):
        self.animator.update(dt)

    def draw(self, screen, base_pos):
        img = self.animator.get_image()
        from core.sprite_animator import draw as draw_sprite

        draw_sprite(screen, img, base_pos)
