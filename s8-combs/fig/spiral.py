#!/usr/bin/env python3
"""Term spirals in the style of Barendregt et al., Dance of the Starlings, Figs. 5.5-5.10.
Computes a depth-bounded prefix of the infinitary normal form t^inf (the Berarducci tree) of a
closed S-term and draws it: application nodes are the corners, the function edge is green, the
argument edge blue, S leaves are red dots; a function edge turns left by ALPHA and shrinks, so an
infinite left spine winds into a spiral.

Prefix computation (S2, Prop. compute): if t has a head normal form (S1 block != 36), head-reduce
to it and recurse on its items; otherwise head-reduce until the prefix S u_1..u_{m-d} has block
36, after which the last d spine items are final, and recurse on them.
Usage: spiral.py TERM DEPTH OUT.pdf   (TERM in S-notation; A = S S S, T = S S).

S8 additions (this copy; the S3 original is unchanged).  COMB=left|first|right marks a comb in
the drawing: its spine is drawn thick and dark, and the first NLAB teeth carry their sizes.
  left  : the term has no hnf; the spine is the left spine of the root, and the n-th tooth is
          the last item of the n-th stable frame on the head run (computed by teeth()).
  right : q_n ->>h S a_n q_{n+1} (or S q_{n+1}); the spine follows the argument edge.
  first : q_n ->>h S q_{n+1} b_n (or S q_{n+1}); the spine follows the function edge, then the
          argument edge.
The sizes are the numbers of S in the teeth as terms on the head run (comb()), computed
independently of the tree; the tree shows the infinitary normal forms of the teeth.  For
right and first the script stops with an error if the comb ends within the depth drawn.
Environment: ALPHA, BETA, H0 (degrees), ARGD (depth cap of side subtrees), NLAB, FIGW, LABFS;
SPINEF, TOOTHF (if SPINEF > 0: fixed length ratios for spine and tooth edges)."""
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
HMODE = os.environ.get('COMB', '')            # 'right' / 'first': keep that comb spine uncapped
def nf(t, d, budget=[0], on=True):
    """Prefix of t^inf to tree depth d: 'S', CUT, or (l, r).  on: t lies on the comb spine."""
    if d <= 0: return CUT
    args = spine(t)
    if fold(t) != BOT:
        while len(args) > 2: args = head_step(args)
        keep = None
        if on and args and HMODE in ('right', 'first'):
            keep = len(args) - 1 if HMODE == 'right' else 0
        return assemble(args, d, keep=keep)
    # no hnf: wait until the last d items are final
    while True:
        m = len(args)
        if m > d and fold(build(args[:m - d])) == BOT: break
        args = head_step(args)
        budget[0] += 1
        if budget[0] > 2_000_000: raise RuntimeError('step budget')
    return assemble(args[-d:], d, infinite=True)
def assemble(items, d, infinite=False, keep=None):
    """Spine node chain: root's argument is the last item.  For an infinite spine only the last
    d items are drawn and the rest of the spine is cut."""
    node = CUT if infinite else 'S'
    k = len(items)
    # depth of the node holding items[i] (0-based) is k-1-i from the root; its argument has depth +1
    for i, it in enumerate(items):
        depth_here = k - 1 - i
        if i == keep: node = (node, nf(it, d - depth_here - 1))
        else: node = (node, nf(it, min(d - depth_here - 1, ARGD), on=False))
    return node
SZ = {}
def size(t):
    """Number of S in t (memoized by identity; terms share subterms)."""
    if t == 'S': return 1
    k = id(t)
    r = SZ.get(k)
    if r is not None and r[0] is t: return r[1]
    v = size(t[0]) + size(t[1]); SZ[k] = (t, v); return v
def teeth(t, n):
    """Sizes of the first n teeth of an hnf-less term: a frame is stable when the frame without
    its last item has block BOT; the last item of the first stable frame is the tooth, and the
    run continues with the rest."""
    assert fold(t) == BOT
    args, out = spine(t), []
    while len(out) < n:
        if fold(build(args[:-1])) == BOT: out.append(size(args.pop()))
        else: args = head_step(args)
    return out
def comb(t, n, mode):
    """Tooth sizes (None for a one-item hnf) of the first n steps of a right or first-item comb."""
    out = []
    for _ in range(n):
        if fold(t) == BOT: raise RuntimeError('comb ends: no hnf')
        args = spine(t)
        while len(args) > 2: args = head_step(args)
        if not args: raise RuntimeError('comb ends: S')
        if len(args) == 1: out.append(None); t = args[0]
        elif mode == 'right': out.append(size(args[0])); t = args[1]
        else: out.append(size(args[1])); t = args[0]
    return out
def comb_path(sizes, mode):
    """Spine of an hnf comb as edge sides (0 function, 1 argument), with a flag per edge: does a
    tooth hang at the node the edge leaves?  S q: one argument edge.  S a q: the argument edge;
    the tooth a hangs below the function edge.  S q b: function edge, then argument edge; the
    tooth b hangs at the first node."""
    path, flag = [], []
    for s_ in sizes:
        if s_ is None: path += [1]; flag += [False]
        elif mode == 'right': path += [1]; flag += [True]
        else: path += [0, 1]; flag += [True, False]
    return tuple(path), tuple(flag)
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
DGREEN, DBLUE = '#0b3d0b', '#0b2a66'   # comb spine
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
def draw(ax, t, x, y, h, L, lw, path=(), labels=(), flag=()):
    """path: the comb spine below this node, a tuple of 0 (function edge) / 1 (argument edge);
    labels: tooth sizes still to be written, one per tooth met along the spine."""
    if t == CUT or L < 0.003: return
    if t == 'S':
        ax.plot([x], [y], 'o', color=RED, ms=max(0.5, 2.0 * lw), zorder=3, mec='none'); return
    wn = weight(t)
    for side, (child, turn, col, dark) in enumerate(((t[0], ALPHA, GREEN, DGREEN), (t[1], -BETA, BLUE, DBLUE))):
        if child == CUT: continue
        on = bool(path) and path[0] == side
        tooth = bool(path) and not on and flag[0]
        f = scale(weight(child), wn)
        if SPINEF and on: f = SPINEF          # fixed ratio along the comb spine
        if SPINEF and tooth: f = TOOTHF
        hc = h + turn
        xc, yc = x + L * f * math.cos(hc), y + L * f * math.sin(hc)
        ax.plot([x, xc], [y, yc], color=dark if on else col, lw=2.6 * lw if on else lw,
                solid_capstyle='round', zorder=2 if on else 1)
        if on:
            draw(ax, child, xc, yc, hc, L * f, lw * 0.95, path[1:], labels[1:] if flag[0] else labels, flag[1:])
        elif tooth:
            if labels and labels[0] is not None:
                # the tooth hangs here: write its size beyond the corner, opposite the tooth
                r = 0.045 + 0.10 * L
                ax.text(x - r * math.cos(hc), y - r * math.sin(hc), str(labels[0]), fontsize=LABFS,
                        ha='center', va='center', color='black', zorder=4)
            draw(ax, child, xc, yc, hc, L * f, lw * 0.6)
        else:
            draw(ax, child, xc, yc, hc, L * f, lw * (0.95 if weight(child) * 2 > wn else 0.75))
LABFS = float(os.environ.get('LABFS', '7'))     # label font size
SPINEF = float(os.environ.get('SPINEF', '0'))   # 0: weight-based lengths, as in S3
TOOTHF = float(os.environ.get('TOOTHF', '0.5'))
if __name__ == '__main__':
    term, depth, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    env = {'A': ('S', 'S') , 'T': ('S', 'S')}
    env['A'] = (('S', 'S'), 'S')
    t = parse(term, env)
    tree = nf(t, depth)
    mode = os.environ.get('COMB', '')
    nlab = int(os.environ.get('NLAB', '8'))
    path, labels, flag = (), (), ()
    if mode == 'left':
        path = (0,) * depth; flag = (True,) * depth; labels = tuple(teeth(t, max(nlab, depth)))
    elif mode in ('right', 'first'):
        labels = tuple(comb(t, depth, mode)); path, flag = comb_path(labels, mode)
    if labels: print('tooth sizes', list(labels))
    labels = tuple(v if i < nlab else None for i, v in enumerate(labels))
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    w = float(os.environ.get('FIGW', '5'))
    fig, ax = plt.subplots(figsize=(w, w))
    draw(ax, tree, 0.0, 0.0, math.radians(float(os.environ.get('H0', '0'))), 1.0, 1.4, path, labels, flag)
    ax.set_aspect('equal'); ax.axis('off')
    fig.savefig(out, bbox_inches='tight', pad_inches=0.02)
    print('ok', out)
