import math
import random
import pygame
from script.bullet import Bullet
from script.particles import Particle
from script.spark import Spark

class PhysicsEntity:
    def __init__ (self, game, e_type, pos, size):
        self.game = game
        self.e_type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up':False, 'down': False, 'right':False, 'left':False}

        self.action=''
        self.anim_offset=(-3,-3)
        self.flip = False
        self.set_action('idle')
        self.last_movement = [0,0]

    def rect(self):
        return pygame.Rect(self.pos[0],self.pos[1], self.size[0], self.size[1])

    #đặt hành động
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.e_type + '/' + self.action].copy()

    #cập nhật vị trí nhân vật
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up':False, 'down': False, 'right':False, 'left':False}

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        self.velocity[1] = min(5, self.velocity[1]+0.1) #điều chỉnh vận tốc rơi

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surf, offset=(0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(),self.flip,False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1]-offset[1]+self.anim_offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size, health=300):
        super().__init__(game, 'player', pos, size)
        self.air_time = 5 # thời gian trên không
        self.jump_count = 2 #số lần nhảy
        self.wall_slide = False #kiểm tra bám tường
        self.dashing = 0 #kiểm tra lướt
        self.health = health #máu
        self.cooldown_skill = 0 # thời gian hồi chiêu
        self.skill_dmg = 50
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1

        #rơi ra khỏi map tự reset
        if self.air_time > 160:
            self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead += 1

        #kiểm tra rơi
        if self.collisions['down']:
            if self.air_time > 5:
                self.game.sfx['landing'].play()
            self.air_time=0
            self.jump_count = 2

        #kiểm tra rơi khi chạm tường
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
                self.air_time = 5
            else:
                self.flip = True
                self.air_time = 5
            self.set_action('wall_slide')

        #nếu rơi không chạm tường
        if not self.wall_slide:
            if self.air_time > 4:
                if self.jump_count == 0:
                    self.set_action('double_jump')
                else:
                    self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        #giảm tốc độ và thời gian hồi dash
        self.stop_dash()

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

        # kiểm tra giảm thời gian hồi chiêu
        if self.cooldown_skill > 0:
            self.cooldown_skill -= 5
        if self.cooldown_skill < 0:
            self.cooldown_skill = 0
    def render(self, surf,offset=(0,0)):
        if abs(self.dashing) <= 50:
            super().render(surf,offset=offset)

    #giảm tốc độ và thời gian hồi dash
    def stop_dash(self):
        if self.dashing > 0 :
            self.dashing = max(0,self.dashing - 1)
        if self.dashing < 0 :
            self.dashing = min(0,self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1 #thời gian hồi lại dash
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity = pvelocity, frame=random.randint(0,7)))
        if abs(self.dashing) in {60,50}:
            for i  in range(20):
                angle = random.random() * math.pi * 2 #góc lướt
                speed = random.random() * 0.5 * 0.5 #tốc độ lướt
                pvelocity = [math.cos(angle)*speed,math.sin(angle)*speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity = pvelocity, frame=random.randint(0,7)))

    #hàm kiểm soát việc nhảy của nhân vật
    def jump_perform(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.game.sfx['jump'].play()
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jump_count = max(0, self.jump_count - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.game.sfx['jump'].play()
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jump_count = max(0, self.jump_count - 1)
                return True

        elif self.jump_count:
            self.velocity[1] = -3 #độ cao khi nhảy
            if self.jump_count == 0:
                self.set_action('double_jump')
                self.game.sfx['jump'].play()
            else:
                self.game.sfx['jump'].play()
                self.set_action('jump')
            self.jump_count -= 1 # giới hạn số lần nhảy
            self.air_time = 5 # thời gian trên không
            return True

    #lướt
    def dash(self):
        if not self.dashing:
            if self.flip:
                self.game.sfx['dash'].play()
                self.dashing = -60
            else:
                self.game.sfx['dash'].play()
                self.dashing = 60

    #nhận sát thương từ npc
    def hit(self, amount = 10):
        self.game.sfx['hit'].play()
        self.game.player.health -= amount
        if self.game.player.health <= 0:
            self.game.dead += 1
            #reset hiệu ứng chuyển cảnh
            self.game.transition = -50
            if self.game.transition:
                transition_surf = pygame.Surface(self.game.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.game.display.get_width() // 2, self.game.display.get_height() // 2), (30 - abs(self.game.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.game.display.blit(transition_surf, (0, 0))
            self.game.player.health = 300
            self.cooldown_skill = 0
        else:
            self.game.dead = 0

    #kiểm soát lượng máu tối đa
    def health_check(self):
        if self.health > 300:
            self.health = 300

    #kỹ năng người chơi
    def skill(self):
        if self.cooldown_skill == 0:
            if self.flip:
                self.game.skills.append(Bullet(self.game,self.rect().centerx, self.rect().centery,-5,0,50))
                for i in range(4):
                    self.game.sparks.append(Spark((self.game.skills[-1].x,self.game.skills[-1].y), random.random() - 0.5 + math.pi, 2 + random.random(),(187, 255, 0)))
                self.cooldown_skill = 500

            elif not self.flip:
                self.game.skills.append(Bullet(self.game,self.rect().centerx, self.rect().centery, 5,0,50))
                for i in range(4):
                    self.game.sparks.append(Spark((self.game.skills[-1].x,self.game.skills[-1].y), random.random() - 0.5, 2 + random.random(),(187, 255, 0)))
                self.cooldown_skill = 500
            self.game.sfx['skill'].play()


# ===== Enemy inheritance refactored with EnemyBase =====

class EnemyBase(PhysicsEntity):
    """Shared base for Enemy, Spec_Enemy, and Boss - eliminates duplication."""

    def __init__(self, game, e_type, pos, size, health=100, dmg=10):
        super().__init__(game, e_type, pos, size)
        self.health = health
        self.dmg = dmg
        self.walking = 0

        # subclass overrides
        self._patrol_chance = 0.01
        self._walking_range = (30, 120)

    # ---------- shared methods ----------

    def take_damage(self, amount=20):
        self.game.sfx['hit'].play()
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        self.game.sfx['hit'].play()
        for i in range(30):
            angle = random.random() * math.pi * 2
            speed = random.random() * 5
            self.game.sparks.append(
                Spark(self.rect().center, angle, 2 + random.random(), (240, 72, 50))
            )
            self.game.particles.append(
                Particle(
                    self.game, 'particle', self.rect().center,
                    velocity=[math.cos(angle + math.pi) * speed * 0.5,
                              math.sin(angle + math.pi) * speed * 0.5],
                    frame=random.randint(0, 7),
                )
            )
        self._remove_from_list()
        self._on_death_extra()

    def _remove_from_list(self):
        self.game.enemies.remove(self)

    def _on_death_extra(self):
        pass

    def _walking_decrement(self):
        return 1

    def patrol_update(self, tilemap, movement=(0, 0), shoot_range=16):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if self.collisions['right'] or self.collisions['left']:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - self._walking_decrement())
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0],
                       self.game.player.pos[1] - self.pos[1])
                if abs(dis[1]) < shoot_range:
                    self._shoot()
        elif random.random() < self._patrol_chance:
            self.walking = random.randint(*self._walking_range)

    def _player_collision(self):
        # player dash hit enemy
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake = max(16, self.game.screenshake)
                self.game.sfx['hit'].play()
                self.take_damage(abs(self.game.player.dashing))
                self.game.player.stop_dash()
                return True

        # enemy collision damages player
        if self.rect().colliderect(self.game.player.rect()) and abs(self.game.player.dashing) < 50:
            self.game.player.health -= 1
            self.game.sfx['ouch'].play()
            if self.game.player.health <= 0:
                self.game.dead += 1
                self.game.transition = -50
                if self.game.transition:
                    transition_surf = pygame.Surface(self.game.display.get_size())
                    pygame.draw.circle(transition_surf, (255, 255, 255),
                                       (self.game.display.get_width() // 2,
                                        self.game.display.get_height() // 2),
                                       (30 - abs(self.game.transition)) * 8)
                    transition_surf.set_colorkey((255, 255, 255))
                    self.game.display.blit(transition_surf, (0, 0))
                self.game.player.health = self.health
                self.game.player.cooldown_skill = 0
            else:
                self.game.dead = 0
            return True
        return False

    def _animate(self, movement):
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')


class Enemy(EnemyBase):
    def __init__(self, game, pos, size, health=150, dmg=15):
        super().__init__(game, 'enemy', pos, size, health=health, dmg=dmg)
        self._patrol_chance = 0.01
        self._walking_range = (30, 120)
        self._shoot_range = 16

    def _shoot(self):
        dis = (self.game.player.pos[0] - self.pos[0],
               self.game.player.pos[1] - self.pos[1])
        if self.flip and dis[0] < 0:
            self.game.sfx['shoot'].play()
            self.game.projectiles.append(
                Bullet(self.game, self.rect().centerx, self.rect().centery, -2, 0, self.dmg)
            )
            for i in range(4):
                self.game.sparks.append(
                    Spark((self.game.projectiles[-1].x, self.game.projectiles[-1].y),
                          random.random() - 0.5 + math.pi, 2 + random.random(), (240, 72, 50))
                )
        elif not self.flip and dis[0] > 0:
            self.game.sfx['shoot'].play()
            self.game.projectiles.append(
                Bullet(self.game, self.rect().centerx, self.rect().centery, 2, 0, self.dmg)
            )
            for i in range(4):
                self.game.sparks.append(
                    Spark((self.game.projectiles[-1].x, self.game.projectiles[-1].y),
                          random.random() - 0.5, 2 + random.random(), (240, 72, 50))
                )

    def update(self, tilemap, movement=(0, 0)):
        self.patrol_update(tilemap, movement=movement, shoot_range=self._shoot_range)
        super().update(tilemap, movement=movement)
        self._animate(movement)
        return self._player_collision()

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        if self.flip:
            surf.blit(
                pygame.transform.flip(self.game.assets['gun'], True, False),
                (self.rect().centerx - 8 - self.game.assets['gun'].get_width() - offset[0],
                 self.rect().centery - offset[1])
            )
        else:
            surf.blit(
                self.game.assets['gun'],
                (self.rect().centerx + 8 - offset[0], self.rect().centery - offset[1])
            )


class Spec_Enemy(EnemyBase):
    def __init__(self, game, pos, size, health=125, healing=150, dmg=15):
        super().__init__(game, 'spec_enemy', pos, size, health=health, dmg=dmg)
        self.healing = healing
        self._patrol_chance = 0.01
        self._walking_range = (30, 40)
        self._shoot_range = 75

    def _on_death_extra(self):
        self.game.player.health += self.healing
        self.game.player.health_check()

    def _remove_from_list(self):
        self.game.spec_enemies.remove(self)

    def _shoot(self):
        self.game.sfx['shoot'].play()
        self.game.projectiles.append(
            Bullet(self.game, self.rect().centerx - 7, self.rect().centery - 7, -2, 0, self.dmg)
        )
        self.game.projectiles.append(
            Bullet(self.game, self.rect().centerx - 7, self.rect().centery, -2, 0, 50)
        )
        for i in range(4):
            self.game.sparks.append(
                Spark((self.game.projectiles[-1].x, self.game.projectiles[-1].y),
                      random.random() - 0.5 + math.pi, 2 + random.random(), (240, 72, 50))
            )
        self.game.sfx['shoot'].play()
        self.game.projectiles.append(
            Bullet(self.game, self.rect().centerx + 7, self.rect().centery - 7, 2, 0, self.dmg)
        )
        self.game.projectiles.append(
            Bullet(self.game, self.rect().centerx + 7, self.rect().centery, 2, 0, 50)
        )
        for i in range(4):
            self.game.sparks.append(
                Spark((self.game.projectiles[-1].x, self.game.projectiles[-1].y),
                      random.random() - 0.5, 2 + random.random(), (240, 72, 50))
            )

    def update(self, tilemap, movement=(0, 0)):
        self.patrol_update(tilemap, movement=movement, shoot_range=self._shoot_range)
        super().update(tilemap, movement=movement)
        self._animate(movement)
        return self._player_collision()

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        g = self.game.assets['gun']
        surf.blit(pygame.transform.flip(g, True, False),
                  (self.rect().centerx - 8 - g.get_width() - offset[0],
                   self.rect().centery - offset[1]))
        surf.blit(g, (self.rect().centerx + 8 - offset[0],
                       self.rect().centery - 8 - offset[1]))
        surf.blit(pygame.transform.flip(g, True, False),
                  (self.rect().centerx - 8 - g.get_width() - offset[0],
                   self.rect().centery - 8 - offset[1]))
        surf.blit(g, (self.rect().centerx + 8 - offset[0],
                       self.rect().centery - offset[1]))


class FlyingEnemy(EnemyBase):
    """Flies in a sine wave pattern, moves toward the player, shoots projectiles."""

    def __init__(self, game, pos, size, health=80, dmg=20):
        super().__init__(game, 'spec_enemy', pos, size, health=health, dmg=dmg)
        self._patrol_chance = 0
        self._walking_range = (0, 0)
        self.anim_offset = (-3, -5)  # offset so it appears higher on screen
        self.shoot_timer = 0
        self.shoot_interval = 120  # frames between shots (~2 seconds at 60fps)
        self._fly_time = random.random() * 100  # staggered start for variety

    def _remove_from_list(self):
        self.game.flying_enemies.remove(self)

    def _shoot(self):
        """Fire a horizontal projectile toward the player's side."""
        self.game.sfx['shoot'].play()
        direction = 2 if not self.flip else -2
        self.game.projectiles.append(
            Bullet(self.game, self.rect().centerx, self.rect().centery, direction, 0, self.dmg)
        )
        spark_angle = random.random() - 0.5 if not self.flip else random.random() - 0.5 + math.pi
        for i in range(4):
            self.game.sparks.append(
                Spark((self.game.projectiles[-1].x, self.game.projectiles[-1].y),
                      spark_angle, 2 + random.random(), (240, 72, 50))
            )

    def update(self, tilemap, movement=(0, 0)):
        self._fly_time += 0.04
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        # horizontal movement toward player at a slow pace
        dx = self.game.player.pos[0] - self.pos[0]
        h_speed = 0.4
        if abs(dx) > 5:
            movement = (h_speed if dx > 0 else -h_speed, 0)
        else:
            movement = (0, 0)

        # sine wave vertical oscillation
        v_movement = math.sin(self._fly_time) * 0.6

        self.pos[0] += movement[0]
        self.pos[1] += v_movement

        # soft horizontal clamp so they do not wander outside the tilemap
        self.pos[0] = max(0, min(self.pos[0], 2000))

        # set flip direction based on movement
        if movement[0] > 0:
            self.flip = False
        elif movement[0] < 0:
            self.flip = True

        self.last_movement = (movement[0], 0)
        self.animation.update()

        # shoot on timer
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            self._shoot()

        # idle / run animation toggle
        if abs(movement[0]) > 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        # check dash collision with player and contact damage
        return self._player_collision()

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)


class Boss(EnemyBase):
    def __init__(self, game, pos, size, dmg=6, health=350):
        super().__init__(game, 'boss', pos, size, health=health, dmg=dmg)
        self._patrol_chance = 0.1
        self._walking_range = (30, 100)
        self._shoot_range = 100

    def _walking_decrement(self):
        return 2

    def _remove_from_list(self):
        self.game.bosses.remove(self)

    def _shoot(self):
        self.game.sfx['shoot'].play()
        # Left spread (5 bullets)
        for off_x, off_y in [(7, -28), (0, -21), (-7, -14), (-7, -7), (-7, 0)]:
            self.game.projectiles.append(
                Bullet(self.game, self.rect().centerx + off_x,
                       self.rect().centery + off_y, -2, 0, self.dmg)
            )
        for i in range(4):
            self.game.sparks.append(
                Spark((self.game.projectiles[-1].x, self.game.projectiles[-1].y),
                      random.random() - 0.5 + math.pi, 2 + random.random(), (240, 72, 50))
            )
        self.game.sfx['shoot'].play()
        # Right spread (5 bullets)
        for off_x, off_y in [(-7, -28), (0, -21), (7, -14), (7, -7), (7, 0)]:
            self.game.projectiles.append(
                Bullet(self.game, self.rect().centerx + off_x,
                       self.rect().centery + off_y, 2, 0, self.dmg)
            )
        for i in range(4):
            self.game.sparks.append(
                Spark((self.game.projectiles[-1].x, self.game.projectiles[-1].y),
                      random.random() - 0.5, 2 + random.random(), (240, 72, 50))
            )

    def update(self, tilemap, movement=(0, 0)):
        self.patrol_update(tilemap, movement=movement, shoot_range=self._shoot_range)
        super().update(tilemap, movement=movement)
        self._animate(movement)
        return self._player_collision()

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
