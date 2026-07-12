"""Polícia e Ladrão - jogo de grafos (Kivy)."""

import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
COP_TEXTURE = CoreImage(os.path.join(ASSETS_DIR, "cop.png")).texture
ROBBER_TEXTURE = CoreImage(os.path.join(ASSETS_DIR, "robber.png")).texture

from graphs import NUM_LEVELS, generate_level, build_adjacency, robber_ai_move

COP_COLOR = (0.2, 0.5, 1, 1)
ROBBER_COLOR = (0.9, 0.2, 0.2, 1)
NODE_COLOR = (0.85, 0.85, 0.85, 1)
NODE_ADJ_COLOR = (0.5, 0.9, 0.5, 1)
EDGE_COLOR = (0.4, 0.4, 0.4, 1)


class GraphCanvas(Widget):
    def __init__(self, status_callback, **kwargs):
        super().__init__(**kwargs)
        self.status_callback = status_callback
        self.level_index = 0
        self.round_count = 0
        self.game_over = False
        self.bind(size=self._redraw, pos=self._redraw)
        self.load_level(0)

    def load_level(self, index):
        self.level_index = index
        level = generate_level(index)
        self.nodes = level["nodes"]
        self.edges = level["edges"]
        self.adj = build_adjacency(self.edges)
        self.cop_pos = level["cop_start"]
        # posição do ladrão: nó mais distante da polícia (via BFS simples)
        self.robber_pos = self._farthest_from(self.cop_pos)
        self.max_rounds = level["max_rounds"]
        self.node_radius = max(14, 30 - len(self.nodes) // 2)
        self.round_count = 0
        self.game_over = False
        self.turn = "cop"
        self._update_status(
            f"{level['name']} - a tua vez (Polícia) - turnos: 0/{self.max_rounds}"
        )
        self._redraw()

    def _farthest_from(self, source):
        dist = {source: 0}
        frontier = [source]
        while frontier:
            nxt = []
            for u in frontier:
                for v in self.adj.get(u, []):
                    if v not in dist:
                        dist[v] = dist[u] + 1
                        nxt.append(v)
            frontier = nxt
        return max(dist, key=dist.get)

    def _node_pixel(self, node_id):
        nx, ny = self.nodes[node_id]
        margin = self.node_radius + 10
        w = max(self.width - 2 * margin, 1)
        h = max(self.height - 2 * margin, 1)
        x = self.x + margin + nx * w
        y = self.y + margin + ny * h
        return x, y

    def _redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            # arestas
            Color(*EDGE_COLOR)
            for a, b in self.edges:
                x1, y1 = self._node_pixel(a)
                x2, y2 = self._node_pixel(b)
                Line(points=[x1, y1, x2, y2], width=2)

            adjacent_to_cop = set(self.adj.get(self.cop_pos, []))

            # nós (bolinhas de fundo, sempre desenhadas primeiro)
            for node_id in self.nodes:
                x, y = self._node_pixel(node_id)
                if node_id in (self.cop_pos, self.robber_pos):
                    Color(1, 1, 1, 1)
                elif node_id in adjacent_to_cop and self.turn == "cop" and not self.game_over:
                    Color(*NODE_ADJ_COLOR)
                else:
                    Color(*NODE_COLOR)
                Ellipse(pos=(x - self.node_radius, y - self.node_radius),
                        size=(self.node_radius * 2, self.node_radius * 2))

            # sprites do polícia e do ladrão por cima dos nós ocupados
            Color(1, 1, 1, 1)
            for node_id, texture in (
                (self.cop_pos, COP_TEXTURE),
                (self.robber_pos, ROBBER_TEXTURE),
            ):
                x, y = self._node_pixel(node_id)
                tw, th = texture.size
                sprite_h = self.node_radius * 2.6
                sprite_w = tw * (sprite_h / th)
                Rectangle(texture=texture,
                          pos=(x - sprite_w / 2, y - sprite_h / 2),
                          size=(sprite_w, sprite_h))

    def on_touch_down(self, touch):
        if self.game_over or self.turn != "cop":
            return super().on_touch_down(touch)
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        for node_id in self.nodes:
            x, y = self._node_pixel(node_id)
            if (touch.x - x) ** 2 + (touch.y - y) ** 2 <= self.node_radius ** 2:
                self._try_move_cop(node_id)
                break
        return True

    def _try_move_cop(self, node_id):
        valid = node_id == self.cop_pos or node_id in self.adj.get(self.cop_pos, [])
        if not valid:
            return
        self.cop_pos = node_id
        self._redraw()

        if self.cop_pos == self.robber_pos:
            self._end_game(won=True)
            return

        self.turn = "robber"
        self._update_status("Vez do ladrão...")
        Clock.schedule_once(self._robber_turn, 0.5)

    def _robber_turn(self, dt):
        if self.game_over:
            return
        self.robber_pos = robber_ai_move(self.adj, self.cop_pos, self.robber_pos)
        self.round_count += 1
        self._redraw()

        if self.cop_pos == self.robber_pos:
            self._end_game(won=True)
            return

        if self.round_count >= self.max_rounds:
            self._end_game(won=False)
            return

        self.turn = "cop"
        self._update_status(
            f"A tua vez (Polícia) - turnos: {self.round_count}/{self.max_rounds}"
        )

    def _end_game(self, won):
        self.game_over = True
        self.turn = None
        if won:
            self._update_status("Apanhaste o ladrão! Vitória da Polícia.")
        else:
            self._update_status("O ladrão escapou! Tenta outra vez.")
        self._redraw()

    def _update_status(self, text):
        self.status_callback(text)

    def next_level(self):
        self.load_level((self.level_index + 1) % NUM_LEVELS)


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.status_label = Label(text="", size_hint=(1, 0.1), font_size="18sp")

        self.graph_canvas = GraphCanvas(self.set_status, size_hint=(1, 0.8))

        button_bar = BoxLayout(size_hint=(1, 0.1), spacing=10, padding=10)
        restart_btn = Button(text="Reiniciar nível")
        restart_btn.bind(on_release=lambda *_: self.graph_canvas.load_level(self.graph_canvas.level_index))
        next_btn = Button(text="Próximo nível")
        next_btn.bind(on_release=lambda *_: self.graph_canvas.next_level())
        button_bar.add_widget(restart_btn)
        button_bar.add_widget(next_btn)

        self.add_widget(self.status_label)
        self.add_widget(self.graph_canvas)
        self.add_widget(button_bar)

    def set_status(self, text):
        self.status_label.text = text


class PoliciaLadraoApp(App):
    title = "Polícia e Ladrão"

    def build(self):
        return MainLayout()


if __name__ == "__main__":
    PoliciaLadraoApp().run()
