"""Geração procedimental de níveis do jogo Polícia e Ladrão.

Cada grafo é construído de forma que é matematicamente garantido que a
Polícia consegue sempre apanhar o Ladrão (grafo "cop-win"/dismantlable):
cada novo nó é ligado a um nó já existente ("dominador") e, no máximo,
a um subconjunto dos vizinhos desse dominador. Isto garante que existe
sempre uma ordem de remoção de nós que prova que o jogo é vencível,
sem precisar de testar caso a caso.
"""

import math
import random
from collections import deque

NUM_LEVELS = 30
MAX_NODES = 18
ROUND_SLACK = 6  # turnos extra oferecidos além do mínimo teórico


def build_adjacency(edges):
    adj = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    return {k: sorted(v) for k, v in adj.items()}


def bfs_distances(adj, source):
    dist = {source: 0}
    q = deque([source])
    while q:
        u = q.popleft()
        for v in adj.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def farthest_node(adj, source):
    """Nó mais distante da origem - usado para posicionar o ladrão."""
    dist = bfs_distances(adj, source)
    return max(dist, key=dist.get)


def robber_ai_move(adj, cop_pos, robber_pos):
    """Ladrão (em jogo) foge para o vizinho que maximiza a distância
    até à posição actual do polícia. É uma heurística, mais fraca que
    o adversário teórico usado para garantir que o nível é vencível -
    ou seja, na prática o jogador tem sempre alguma folga extra."""
    dist_from_cop = bfs_distances(adj, cop_pos)
    candidates = list(adj.get(robber_pos, [])) + [robber_pos]
    best = max(candidates, key=lambda n: dist_from_cop.get(n, -1))
    return best


def _generate_dismantlable_graph(num_nodes, rng, density):
    """Constrói um grafo conectado e garantidamente 'cop-win'."""
    adj_build = {0: set()}
    order = [0]
    for i in range(1, num_nodes):
        u = rng.choice(order)
        u_neighbors = list(adj_build[u])
        extra_count = 0
        if u_neighbors:
            cap = max(0, int(len(u_neighbors) * density))
            extra_count = rng.randint(0, min(len(u_neighbors), cap)) if cap else 0
        extra = rng.sample(u_neighbors, k=extra_count) if extra_count else []
        new_neighbors = set(extra) | {u}
        adj_build[i] = set()
        for x in new_neighbors:
            adj_build[i].add(x)
            adj_build[x].add(i)
        order.append(i)

    edges = set()
    for a, neighbors in adj_build.items():
        for b in neighbors:
            edges.add(tuple(sorted((a, b))))
    return sorted(edges)


def _circle_positions(num_nodes, rng, jitter=0.08):
    positions = {}
    for i in range(num_nodes):
        angle = 2 * math.pi * i / num_nodes
        base_x = 0.5 + 0.42 * math.cos(angle)
        base_y = 0.5 + 0.42 * math.sin(angle)
        jx = (rng.random() - 0.5) * jitter
        jy = (rng.random() - 0.5) * jitter
        x = min(max(base_x + jx, 0.05), 0.95)
        y = min(max(base_y + jy, 0.05), 0.95)
        positions[i] = (x, y)
    return positions


def _min_rounds_to_win(adj, num_nodes, cop_start, robber_start):
    """Análise retrógrada (teoria dos jogos): nº mínimo de turnos que a
    Polícia precisa para garantir a vitória, mesmo contra o pior Ladrão
    possível. Como o grafo é 'cop-win' por construção, há sempre um
    valor (nunca None)."""
    solved = {(x, x): 0 for x in range(num_nodes)}
    round_num = 0
    while True:
        round_num += 1
        progressed = False
        for c in range(num_nodes):
            for r in range(num_nodes):
                if (c, r) in solved:
                    continue
                found = False
                for c2 in list(adj[c]) + [c]:
                    if c2 == r:
                        found = True
                        break
                    if all((c2, r2) in solved for r2 in list(adj[r]) + [r]):
                        found = True
                        break
                if found:
                    solved[(c, r)] = round_num
                    progressed = True
        if not progressed:
            break
    return solved.get((cop_start, robber_start), num_nodes)


def generate_level(index):
    """Gera um nível reprodutível (mesma seed = mesmo grafo), com
    dificuldade crescente, sempre garantidamente vencível."""
    rng = random.Random(2000 + index)

    num_nodes = min(6 + index, MAX_NODES)
    density = max(0.35 - index * 0.01, 0.05)

    edges = _generate_dismantlable_graph(num_nodes, rng, density)
    adj = build_adjacency(edges)
    positions = _circle_positions(num_nodes, rng)

    cop_start = 0
    robber_start = farthest_node(adj, cop_start)
    optimal_rounds = _min_rounds_to_win(adj, num_nodes, cop_start, robber_start)
    max_rounds = optimal_rounds + ROUND_SLACK

    return {
        "name": f"Nível {index + 1} de {NUM_LEVELS}",
        "nodes": positions,
        "edges": edges,
        "cop_start": cop_start,
        "max_rounds": max_rounds,
    }
