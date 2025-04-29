import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtMultimedia import QSoundEffect

# Laser class
class Laser:
    speed_increase = 0  # Class variable to track global speed increase

    def __init__(self, x, y, width=100, height=10, base_speed=5):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = base_speed + Laser.speed_increase

    def move(self):
        self.y += self.speed

# Particle class for trail effect
class Particle:
    def __init__(self, x, y, size=5):
        self.x = x
        self.y = y
        self.size = size
        self.life = 20  # Particle lifespan

        # Randomized yellow/orange colors for fiery effect
        r = 255
        g = random.randint(150, 255)
        b = 0
        self.color = QColor(r, g, b)

    def move(self):
        self.y += 3
        self.life -= 1

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laser Dodger Game")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)

        # Player properties
        self.player_x = 400
        self.player_y = 500
        self.player_width = 40
        self.player_height = 40
        self.player_speed = 10

        # Game variables
        self.lasers = []
        self.particles = []
        self.survival_time = 0
        self.laser_level = 1
        self.game_active = False  # Start screen initially

        # Timers
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        self.game_timer.start(30)  # ~33 FPS

        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_laser)
        self.spawn_interval = 1000  # 1 second

        self.score_timer = QTimer()
        self.score_timer.timeout.connect(self.update_score)
        self.score_timer.start(100)

        # Sound effects
        self.background_music = QSoundEffect()
        self.background_music.setSource(QUrl.fromLocalFile("background.wav"))
        self.background_music.setLoopCount(-2)
        self.background_music.setVolume(0.5)

        self.game_over_sound = QSoundEffect()
        self.game_over_sound.setSource(QUrl.fromLocalFile("laser_hit.WAV or laser_hit.wav"))
        self.game_over_sound.setVolume(0.7)

        self.show()

    # Start or restart game logic
    def start_game(self):
        self.reset_game()
        self.game_active = True
        self.background_music.play()
        self.spawn_timer.start(self.spawn_interval)

    def reset_game(self):
        self.player_x = 400
        self.player_y = 500
        self.lasers.clear()
        self.particles.clear()
        self.survival_time = 0
        self.laser_level = 1
        Laser.speed_increase = 0
        self.game_active = False

    # Spawning lasers
    def spawn_laser(self):
        random_x = random.randint(0, self.width() - 100)
        new_laser = Laser(random_x, 0)
        self.lasers.append(new_laser)

    # Main game update loop
    def update_game(self):
        if self.game_active:
            # Move lasers and generate particles
            for laser in self.lasers[:]:
                laser.move()
                particle = Particle(laser.x + laser.width / 2, laser.y + laser.height)
                self.particles.append(particle)

                # Remove lasers off-screen
                if laser.y > self.height():
                    self.lasers.remove(laser)

            # Move and remove particles
            for particle in self.particles[:]:
                particle.move()
                if particle.life <= 0:
                    self.particles.remove(particle)

            self.check_collision()

        self.update()  # Trigger paintEvent

    # Collision detection
    def check_collision(self):
        player_rect = (self.player_x, self.player_y, self.player_width, self.player_height)
        for laser in self.lasers:
            laser_rect = (laser.x, laser.y, laser.width, laser.height)
            if self.rects_collide(player_rect, laser_rect):
                self.game_over()

    def rects_collide(self, rect1, rect2):
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        return not (x1 + w1 < x2 or x1 > x2 + w2 or y1 + h1 < y2 or y1 > y2 + h2)

    def game_over(self):
        self.game_active = False
        self.spawn_timer.stop()
        self.background_music.stop()
        self.game_over_sound.play()

    # Score and laser speed logic
    def update_score(self):
        if self.game_active:
            self.survival_time += 100

            # Instead of hardcoding the times, check if survival_time is a multiple of 100 after a base time (like 150).
            if self.survival_time >= 150 and (self.survival_time - 150) % 100 == 0:
                self.increase_laser_speed()

    def increase_laser_speed(self):
        Laser.speed_increase += 2
        self.laser_level += 1
        # Increase speed of existing lasers
        for laser in self.lasers:
            laser.speed += 2

    # Get laser color based on level
    def get_laser_color(self):
        if self.laser_level <= 2:
            return QColor(255, 0, 0)  # Red
        elif self.laser_level <= 4:
            return QColor(255, 165, 0)  # Orange
        elif self.laser_level <= 6:
            return QColor(138, 43, 226)  # Purple
        else:
            return QColor(255, 20, 147)  # Deep Pink

    # Drawing everything
    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw player
        if self.game_active:
            painter.setBrush(QColor(0, 255, 0))
        else:
            painter.setBrush(QColor(128, 128, 128))
        painter.drawRect(self.player_x, self.player_y, self.player_width, self.player_height)

        # Draw lasers
        painter.setBrush(self.get_laser_color())
        for laser in self.lasers:
            painter.drawRect(laser.x, laser.y, laser.width, laser.height)

        # Draw particles (glowing effect)
        for particle in self.particles:
            painter.setBrush(particle.color)
            painter.drawEllipse(int(particle.x), int(particle.y), particle.size, particle.size)

        # Draw survival time and laser level
        painter.setPen(QColor(255,255, 255))
        painter.drawText(10, 30, f"Time: {self.survival_time / 1000:.1f} seconds")
        painter.drawText(10, 60, f"Laser Level: {self.laser_level}")

        # Start / Game Over screen messages
        if not self.game_active:
            painter.drawText(self.width() // 2 - 80, self.height() // 2, "Press ENTER to Start")
            if self.survival_time > 0:
                painter.drawText(self.width() // 2 - 80, self.height() // 2 + 30, "Game Over! Press R to Restart")

    # Handle key events for movement and game control
    def keyPressEvent(self, event):
        if self.game_active:
            if event.key() == Qt.Key.Key_Left and self.player_x > 0:
                self.player_x -= self.player_speed
            elif event.key() == Qt.Key.Key_Right and self.player_x < self.width() - self.player_width:
                self.player_x += self.player_speed
            elif event.key() == Qt.Key.Key_Up and self.player_y > 0:
                self.player_y -= self.player_speed
            elif event.key() == Qt.Key.Key_Down and self.player_y < self.height() - self.player_height:
                self.player_y += self.player_speed
        else:
            if event.key() == Qt.Key.Key_Return:  # ENTER to start game
                self.start_game()
            elif event.key() == Qt.Key.Key_R:  # R to restart after game over
                self.start_game()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameWindow()
    sys.exit(app.exec())
# Sound effects
    self.background_music = QSoundEffect()
    self.background_music.setSource(QUrl.fromLocalFile("background.wav"))
    self.background_music.setLoopCount(-2)  # <-- fixed here
    self.background_music.setVolume(1.5)
    self.background_music.play()
