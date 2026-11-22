#!/usr/bin/env python3
"""Term spirals in the style of Barendregt et al., Dance of the Starlings, Figs. 5.5-5.10.
Computes a depth-bounded prefix of the infinitary normal form t^inf (the Berarducci tree) of a
closed S-term and draws it: application nodes are the corners, the function edge is green, the
argument edge blue, S leaves are red dots; a function edge turns left by ALPHA and shrinks, so an
infinite left spine winds into a spiral.

Prefix computation (S2, Prop. compute): if t has a head normal form (S1 block != 36), head-reduce
to it and recurse on its items; otherwise head-reduce until the prefix S u_1..u_{m-d} has block
36, after which the last d spine items are final, and recurse on them.
Usage: spiral.py TERM DEPTH OUT.pdf   (TERM in S-notation, e.g. "A A A" with A = S S S)."""
import sys, os, math
sys.path.insert(0, os.path.expanduser('~/Code/ski/notes/checks/s15/cert'))
from s1tables import beta, BOT
sys.setrecursionlimit(100000)
FM = {}
def fold(t):
    if t == 'S': return 0
    k = id(t)
    r = FM.get(k)
    if r is not None and r[0] is t: return r[1]
    v = beta(fold(t[0]), fold(t[1])); FM[k] = (t, v); return v
def spine(t):
    a = []
    while t != 'S': a.append(t[1]); t = t[0]
    return a[::-1]
def build(args, h='S'):
    for x in args: h = (h, x)
    return h
def head_step(args):
    x, y, z = args[0], args[1], args[2]
    return spine(x) + [z, (y, z)] + args[3:]
CUT = '...'
ARGD = int(os.environ.get('ARGD', '99'))   # depth cap for side subtrees
def nf(t, d, budget=[0]):
    """Prefix of t^inf to tree depth d: 'S', CUT, or (l, r)."""
    if d <= 0: return CUT
    args = spine(t)
    if fold(t) != BOT:
        while len(args) > 2: args = head_step(args)
        return assemble(args, d)
    # no hnf: wait until the last d items are final
    while True:
        m = len(args)
        if m > d and fold(build(args[:m - d])) == BOT: break
        args = head_step(args)
        budget[0] += 1
        if budget[0] > 2_000_000: raise RuntimeError('step budget')
    return assemble(args[-d:], d, infinite=True)
def assemble(items, d, infinite=False):
    """Spine node chain: root's argument is the last item.  For an infinite spine only the last
    d items are drawn and the rest of the spine is cut."""
    node = CUT if infinite else 'S'
    k = len(items)
    # depth of the node holding items[i] (0-based) is k-1-i from the root; its argument has depth +1
    for i, it in enumerate(items):
        depth_here = k - 1 - i
        node = (node, nf(it, min(d - depth_here - 1, ARGD)))
    return node
def parse(s, env):
    toks = s.replace('(', ' ( ').replace(')', ' ) ').split()
    def expr(i):
        t = None
        while i < len(toks) and toks[i] != ')':
            if toks[i] == '(':
                u, i = expr(i + 1); i += 1
            else:
                u = env[toks[i]] if toks[i] in env else 'S'; i += 1
            t = u if t is None else (t, u)
        return t, i
    return expr(0)[0]

ALPHA = math.radians(float(os.environ.get('ALPHA', '50')))   # function edge turns left
BETA = math.radians(float(os.environ.get('BETA', '50')))     # argument edge turns right
GREEN, BLUE, RED = '#2e7d32', '#1f4e9c', '#c62828'
W = {}
def weight(t):
    """Number of drawn nodes below t (memoized by identity)."""
    if t == 'S' or t == CUT: return 1
    k = id(t)
    if k in W and W[k][0] is t: return W[k][1]
    v = 1 + weight(t[0]) + weight(t[1]); W[k] = (t, v); return v
def scale(w, wn):
    """Edge length factor: heavy children (infinite spines) long, light ones short."""
    x = w / wn
    return 0.30 + 0.58 * x ** 0.7
def draw(ax, t, x, y, h, L, lw):
    if t == CUT or L < 0.003: return
    if t == 'S':
        ax.plot([x], [y], 'o', color=RED, ms=max(0.5, 2.0 * lw), zorder=3, mec='none'); return
    wn = weight(t)
    for child, turn, col in ((t[0], ALPHA, GREEN), (t[1], -BETA, BLUE)):
        if child == CUT: continue
        f = scale(weight(child), wn)
        hc = h + turn
        xc, yc = x + L * f * math.cos(hc), y + L * f * math.sin(hc)
        ax.plot([x, xc], [y, yc], color=col, lw=lw, solid_capstyle='round')
        draw(ax, child, xc, yc, hc, L * f, lw * (0.95 if weight(child) * 2 > wn else 0.75))
if __name__ == '__main__':
    term, depth, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    env = {'A': ('S', 'S') , 'T': ('S', 'S')}
    env['A'] = (('S', 'S'), 'S')
    t = parse(term, env)
    tree = nf(t, depth)
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5, 5))
    draw(ax, tree, 0.0, 0.0, math.radians(float(os.environ.get('H0', '0'))), 1.0, 1.4)
    ax.set_aspect('equal'); ax.axis('off')
    fig.savefig(out, bbox_inches='tight', pad_inches=0.02)
    print('ok', out)
