"""S9 figure: the right-action graph of S1's 38-element model.

Vertices are the blocks 0..37; there is an edge v -> beta(v, w) for every block w (parallel edges
are drawn once).  Blocks are placed in rows by rank: the length of the longest walk from the block
that avoids the block 36 and the loop at 12.  The script recomputes the rank, compares it with
rkTable of lean-ski (Ski/NcfpC.lean), and asserts the table facts used in the paper.

usage: python3 -I graph.py OUT.pdf      (needs matplotlib; reads fig/s1table.json, the S1 table = lean-ski HnfS.blockTable)
"""
import sys, os, functools
import json
BLOCK = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 's1table.json')))['table']

B = range(38)
BOT = 36
beta = lambda a, b: BLOCK[a][b]
RK = [7, 6, 4, 5, 4, 5, 4, 3, 3, 2, 3, 2, 3, 3, 2, 3, 4, 2, 2, 3, 2, 3, 2, 2, 4, 1, 2, 1, 2, 2, 1, 0,
      2, 3, 1, 2, 0, 1]                                    # Ncfp.rkTable

E = {(v, beta(v, w)) for v in B for w in B}
LOOP = (12, 12)
DAG = sorted(e for e in E if BOT not in e and e != LOOP)   # edges among blocks other than 36
TOBOT = sorted(v for v in B if v != BOT and (v, BOT) in E)

@functools.lru_cache(None)
def rank(v):
    return max((1 + rank(u) for (x, u) in DAG if x == v), default=0)

# the facts used in the paper
assert all(beta(BOT, w) == BOT for w in B)                                  # 36 absorbs
assert all(beta(v, w) != 0 for v in B for w in B)                           # no product is 0
assert [w for w in B if beta(12, w) == 12] == [0]                           # the loop, only by 0
assert [rank(v) for v in B] == RK and RK[BOT] == 0
assert all(rank(u) < rank(v) for (v, u) in DAG)                             # every other edge descends
assert all(beta(0, a) != 12 for a in B)
assert all(a == 0 for a in B for b in B if beta(beta(0, a), b) == 12)

def layout():
    rows = {r: [v for v in B if v != BOT and RK[v] == r] for r in range(8)}
    nb = {v: [] for v in B}
    for (v, u) in DAG:
        nb[v].append(u); nb[u].append(v)
    pos = {}
    def place():
        for r, row in rows.items():
            for i, v in enumerate(row):
                pos[v] = i - (len(row) - 1) / 2
    place()
    for sweep in range(40):                                 # barycentre ordering
        for r in (range(8) if sweep % 2 else range(7, -1, -1)):
            rows[r].sort(key=lambda v: (v != 12, sum(pos[u] for u in nb[v]) / len(nb[v]) if nb[v] else 0, v))
            place()
    return rows, pos

def main(out):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, Circle
    plt.rcParams.update({'font.family': 'serif', 'font.size': 7, 'pdf.fonttype': 42})
    rows, pos = layout()
    DX, DY, R = 0.62, 0.74, 0.19
    xy = {v: (pos[v] * DX, RK[v] * DY) for v in B if v != BOT}
    xy[BOT] = (5.5 * DX, 0.0)
    fig, ax = plt.subplots(figsize=(5.0, 4.3))
    grey, red = '#8a8a8a', '#c0392b'
    for (v, u) in DAG:
        hot = v == 12
        span = RK[v] - RK[u]                                # long edges are bent, to miss the rows between
        bend = 0.0 if span == 1 else (0.10 if xy[u][0] >= xy[v][0] else -0.10)
        ax.add_patch(FancyArrowPatch(xy[v], xy[u], arrowstyle='-|>', mutation_scale=4.5,
                                     connectionstyle='arc3,rad=%g' % bend,
                                     shrinkA=5.6, shrinkB=5.6, lw=0.75 if hot else 0.45,
                                     color='#222222' if hot else grey, zorder=2 if hot else 1))
    for v in TOBOT:
        ax.add_patch(FancyArrowPatch(xy[v], xy[BOT], arrowstyle='-|>', mutation_scale=4.5,
                                     shrinkA=5.6, shrinkB=5.6, lw=0.45, ls=(0, (2, 2)),
                                     color=grey, zorder=1))
    for v, sg in ((12, -1), (BOT, 1)):                      # the two loops
        x, y = xy[v]
        ax.add_patch(FancyArrowPatch((x + sg * 0.10, y + 0.16), (x + sg * 0.10, y - 0.16),
                                     connectionstyle='arc3,rad=%g' % (-2.2 * sg), arrowstyle='-|>',
                                     mutation_scale=5.5, lw=1.1, color=red, zorder=3))
    ax.text(xy[12][0] - 0.52, xy[12][1], r'$w=0$', color=red, va='center', ha='right', fontsize=7)
    ax.text(xy[BOT][0] + 0.52, xy[BOT][1], r'all $w$', color=red, va='center', ha='left', fontsize=7)
    for v in B:
        hot = v in (12, BOT)
        ax.add_patch(Circle(xy[v], R, fc='#fbe9e7' if hot else 'white', ec=red if hot else 'black',
                            lw=1.1 if hot else 0.6, zorder=4))
        ax.text(*xy[v], r'$\bot$' if v == BOT else str(v), ha='center', va='center', zorder=5,
                fontsize=6.5)
    xl = min(x for x, _ in xy.values()) - 0.95
    for r in range(8):
        ax.text(xl, r * DY, str(r), ha='center', va='center', color='#555555', fontsize=7)
    ax.text(xl, 7 * DY + 0.45, 'rank', ha='center', va='center', color='#555555', fontsize=7)
    ax.set_xlim(xl - 0.3, max(x for x, _ in xy.values()) + 1.0)
    ax.set_ylim(-0.4, 7 * DY + 0.65)
    ax.set_aspect('equal'); ax.axis('off')
    fig.savefig(out, bbox_inches='tight', pad_inches=0.02)
    print('blocks 38; edges', len(E), '= DAG', len(DAG), '+ loop at 12 + into 36:', len(TOBOT),
          '+ loop at 36; blocks with an edge to 36:', TOBOT)

if __name__ == '__main__':
    main(sys.argv[1])
