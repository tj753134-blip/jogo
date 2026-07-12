# Polícia e Ladrão (jogo de grafos)

Jogo Kivy: controlas a Polícia e tens de apanhar o Ladrão (IA) movendo-te
nó a nó num grafo. A IA do ladrão foge sempre para o vizinho mais distante
do polícia (BFS) — leve, sem machine learning.

**30 níveis gerados automaticamente** (`graphs.py`), com dificuldade
crescente (mais nós, grafos mais "esparsos"). Cada grafo é construído
por um método que garante matematicamente que é sempre possível apanhar
o ladrão (grafo "cop-win"), e o nº de turnos disponíveis é calculado
por teoria dos jogos (turnos mínimos necessários + folga), por isso
nenhum nível é impossível ou tem turnos a menos.

## Como gerar o APK

1. Cria um repositório no GitHub e envia esta pasta inteira (main.py,
   graphs.py, buildozer.spec, .github/workflows/build-apk.yml).
2. Faz push para a branch `main`.
3. Vai a **Actions** no GitHub — o workflow "Build APK" corre automaticamente.
4. Quando terminar (10-20 min na primeira vez), descarrega o APK em
   **Artifacts** → `policia-e-ladrao-apk`.
5. Transfere o `.apk` para o telemóvel e instala (activa "instalar de
   fontes desconhecidas" se pedir).

## Testar localmente (opcional, no PC)

```bash
pip install kivy
python main.py
```

## Estrutura

- `graphs.py` — geração procedimental dos 30 níveis (grafos garantidamente
  vencíveis), BFS, IA do ladrão
- `main.py` — interface Kivy, desenho do grafo/sprites, toques, turnos
- `assets/` — sprites da Polícia e do Ladrão (Kenney, CC0)
- `buildozer.spec` — configuração do build Android
- `.github/workflows/build-apk.yml` — compila o APK automaticamente

## Próximos passos (quando quiseres)

- Mais de 30 níveis: só mudar `NUM_LEVELS` em `graphs.py`
- Guardar progresso/melhor pontuação (nº mínimo de turnos) com SQLite
- Menu de selecção de nível em vez de "próximo nível" sequencial
- Animação de movimento entre nós (em vez de salto instantâneo)
