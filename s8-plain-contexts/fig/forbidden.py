#!/usr/bin/env python3
"""Forbidden trees of the NCFP type schemes, drawn as spirals (style of ../spiral.py, which is
adapted from S3's fig/spiral.py after Barendregt et al., Dance of the Starlings, Figs. 5.5-5.10).

For a context E != [ ] over S with holes p and closed normal parts, the tree equation T = E[T]
has exactly one solution T_E, a rational tree: unfold the hole to the root of E forever.  This
script draws the prefix of T_E of tree depth DEPTH.  No term is reduced: the tree is built from
the context alone.  (That no closed S-term has this tree is the theorem named in FIGS; the
script does not check it.)

Drawing: application nodes are the corners; the function edge is green and turns left by ALPHA,
the argument edge is blue and turns right by BETA; S leaves are red dots.  A small black ring
marks the nodes at which the whole tree T_E recurs (the root and each unfolded hole), down
to edge length RINGMIN; smaller recurrences are drawn without a ring.  Closed
parts (n) are ordinary finite subtrees.  Edge lengths follow S3's weight rule, with the weights
taken from a prefix LOOK levels deeper than the one drawn, so that the copies of T_E at the
rings are (nearly) similar to the whole figure rather than distorted by the depth cut.

Usage: forbidden.py            all figures of FIGS, one PDF each, plus all.pdf (small multiples)
       forbidden.py CONTEXT DEPTH OUT.pdf   one context; p = hole, n = N (env N, default 'S S')
Environment: ALPHA, BETA, H0 (degrees), FIGW, LOOK, RING (ring radius / edge length), RINGMIN, N."""
import sys, os, math
sys.setrecursionlimit(100000)
HOLE = 'p'
GREEN, BLUE, RED = '#2e7d32', '#1f4e9c', '#c62828'
LOOK = int(os.environ.get('LOOK', '40'))
RING = float(os.environ.get('RING', '0.07'))
RINGMIN = float(os.environ.get('RINGMIN', '0.035'))   # no ring where the incoming edge is shorter

def parse(s, env):
    toks = s.replace('(', ' ( ').replace(')', ' ) ').split()
    def expr(i):
        t = None
        while i < len(toks) and toks[i] != ')':
            if toks[i] == '(':
                u, i = expr(i + 1); i += 1
            else:
                u = env[toks[i]]; i += 1
            t = u if t is None else (t, u)
        return t, i
    t, i = expr(0)
    assert i == len(toks), 'unbalanced'
    return t

class Fig:
    def __init__(self, ctx, depth, n='S S', alpha=50, beta=50, h0=0):
        closed = parse(n, {'S': 'S'})
        self.E = parse(ctx, {'S': 'S', 'p': HOLE, 'n': closed, 'm': closed})
        assert self.E != HOLE and self.E != 'S'
        self.depth, self.alpha, self.beta, self.h0 = depth, math.radians(alpha), math.radians(beta), math.radians(h0)
        self.W = {}
        self.count = 0
    def weight(self, t, r):
        """Number of nodes of the prefix of depth r of the tree at subterm t of E (hole = E)."""
        if t == HOLE: t = self.E
        if t == 'S' or r <= 0: return 1
        k = (id(t), r)
        v = self.W.get(k)
        if v is None:
            v = 1 + self.weight(t[0], r - 1) + self.weight(t[1], r - 1); self.W[k] = v
        return v
    def draw(self, ax, t, x, y, h, L, lw, d):
        """d: tree depth still to draw below this node."""
        if L < 0.003: return
        if t == HOLE:
            from matplotlib.patches import Circle
            if L >= RINGMIN: ax.add_patch(Circle((x, y), RING * L, fill=False, ec='black', lw=max(0.25, 0.45 * lw), zorder=4))
            t = self.E
        if t == 'S':
            ax.plot([x], [y], 'o', color=RED, ms=max(0.5, 2.0 * lw), zorder=3, mec='none'); return
        if d <= 0: return
        self.count += 1
        r = d + LOOK
        wn = self.weight(t, r)
        for child, turn, col in ((t[0], self.alpha, GREEN), (t[1], -self.beta, BLUE)):
            wc = self.weight(child, r - 1)
            f = 0.30 + 0.58 * (wc / wn) ** 0.7          # S3's scale()
            hc = h + turn
            xc, yc = x + L * f * math.cos(hc), y + L * f * math.sin(hc)
            ax.plot([x, xc], [y, yc], color=col, lw=lw, solid_capstyle='round', zorder=1)
            self.draw(ax, child, xc, yc, hc, L * f, lw * (0.95 if wc * 2 > wn else 0.75), d - 1)
    def render(self, ax):
        self.draw(ax, HOLE, 0.0, 0.0, self.h0, 1.0, 1.4, self.depth)
        ax.set_aspect('equal'); ax.axis('off')

# name, context, n, depth, theorem (for the small-multiples title), drawing options
# Combs keep the series default ALPHA = BETA = 50; the branching trees use 75/55, which keeps
# the copies of T_E from overlapping.
BR = {'alpha': 75, 'beta': 55}
FIGS = [
    ('01-comb',       'S p',               'S',   18, 'Thm 2',     {}),
    ('02-teeth',      'S n p',             'S S', 18, 'Thm 2',     {}),
    ('03-firstitem',  'S p n',             'S S', 18, 'Thm F',     {}),
    ('04-mixed',      'S n (S p m)',       'S S', 18, 'Thm G',     {}),
    ('05-theta',      'S p p',             'S',   14, 'Thm Θ',     BR),
    ('06-thetaprime', 'S p (S p)',         'S',   14, "Thm Θ′",    BR),
    ('07-N1',         'S (S S p) p',       'S',   14, 'Thm N1',    BR),
    ('08-N2',         'S p (S n p)',       'S S', 14, 'Thm N2',    BR),
    ('09-threehole',  'S (S p p) (S n p)', 'S S', 14, 'Cor. T2',   BR),
    ('10-N12',        'S (S (S n p) p) p', 'S S', 14, 'Thm N12',   BR),
]
def tex(ctx): return 'T = ' + ctx.replace('p', 'T')

if __name__ == '__main__':
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    w = float(os.environ.get('FIGW', '5'))
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) == 4:
        opts = {k: float(os.environ[k.upper()]) for k in ('alpha', 'beta', 'h0') if k.upper() in os.environ}
        F = Fig(sys.argv[1], int(sys.argv[2]), os.environ.get('N', 'S S'), **opts)
        fig, ax = plt.subplots(figsize=(w, w)); F.render(ax)
        fig.savefig(sys.argv[3], bbox_inches='tight', pad_inches=0.02)
        print('ok', sys.argv[3], 'application nodes drawn:', F.count); sys.exit(0)
    for name, ctx, n, depth, thm, opts in FIGS:
        F = Fig(ctx, depth, n, **opts)
        fig, ax = plt.subplots(figsize=(w, w)); F.render(ax)
        out = os.path.join(here, name + '.pdf')
        fig.savefig(out, bbox_inches='tight', pad_inches=0.02); plt.close(fig)
        print('ok', name, tex(ctx), 'n =', n, 'depth', depth, 'application nodes drawn:', F.count)
    fig, axes = plt.subplots(2, 5, figsize=(12.5, 5.6))
    for ax, (name, ctx, n, depth, thm, opts) in zip(axes.flat, FIGS):
        Fig(ctx, depth, n, **opts).render(ax)
        ax.set_title(tex(ctx) + ('' if 'n' not in ctx else '   (n = %s)' % n) + '\n' + thm, fontsize=8)
    fig.savefig(os.path.join(here, 'all.pdf'), bbox_inches='tight', pad_inches=0.05)
    print('ok all.pdf')
