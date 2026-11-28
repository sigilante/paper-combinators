"""check_qbc.py: the finite exact computations of S16 ("Convertible Teeth Determine p_K over S but Not over
S, B, C").  Pure Python 3, no imports beyond sys.  Every check is an assertion; the script prints what it checked.

Terms: an atom is a string, an application is a pair (f, x).  Combinators: 'S', 'B', 'C'.  Any other string
is a variable; 's' is the combinator S occurring as data.  Head reduction contracts the spine head when it is S, B or C with at least 3 items, and stops
at a variable head or at an hnf.
"""
import sys
sys.setrecursionlimit(100000)


def A(*xs):
    t = xs[0]
    for x in xs[1:]:
        t = (t, x)
    return t


def show(t):
    if not isinstance(t, tuple):
        return t
    f, x = t
    xs = show(x)
    return show(f) + ' ' + ('(' + xs + ')' if isinstance(x, tuple) else xs)


def size(t):
    return 1 if not isinstance(t, tuple) else size(t[0]) + size(t[1])


def count(t, a):
    return (1 if t == a else 0) if not isinstance(t, tuple) else count(t[0], a) + count(t[1], a)


def occurs(x, t):
    return t == x or (isinstance(t, tuple) and (occurs(x, t[0]) or occurs(x, t[1])))


def spine(t):
    args = []
    while isinstance(t, tuple):
        args.append(t[1])
        t = t[0]
    return t, args[::-1]


COMB = ('S', 'B', 'C')


def contract(h, x, y, z):
    if h == 'S':
        return ((x, z), (y, z))
    if h == 'B':
        return (x, (y, z))
    return ((x, z), y)  # C


def head_run(t, cap):
    """Return (stop head, items, steps, heads, S-frame first items)."""
    h, args = spine(t)
    st = args[::-1]
    k = 0
    heads, sfirst = [], []
    while k < cap and h in COMB and len(st) >= 3:
        if h == 'S':
            sfirst.append(st[-1])
        x, y, z = st.pop(), st.pop(), st.pop()
        heads.append(h)
        nh, na = spine(contract(h, x, y, z))
        st.extend(na[::-1])
        h = nh
        k += 1
    return h, st[::-1], k, ''.join(heads), sfirst


def nf(t):
    """Leftmost-outermost normal form (S, B, C active); used only on terms that normalize."""
    h, args = spine(t)
    while h in COMB and len(args) >= 3:
        nh, na = spine(contract(h, *args[:3]))
        h, args = nh, na + args[3:]
    return A(h, *[nf(u) for u in args]) if args else h


# ---------------------------------------------------------------- the program
IR = A('B', 'C', 'C')


def lam(x, t):
    """lambda-I bracket abstraction with eta; [x]x = Ir.  No K is ever introduced."""
    if t == x:
        return IR
    assert occurs(x, t), 'vacuous abstraction'
    f, a = t
    inf, ina = occurs(x, f), occurs(x, a)
    if a == x and not inf:
        return f
    if inf and ina:
        return A('S', lam(x, f), lam(x, a))
    if ina:
        return A('B', f, lam(x, a))
    return A('C', lam(x, f), a)


def lams(xs, t):
    for x in reversed(xs):
        t = lam(x, t)
    return t


# Data (the pure-S material of p_K) is written with the atom 's', which denotes S as well.  Keeping it apart lets
# the script check that data S never reaches the head, and lets nf() contract code redexes only.
S = 's'
Q = A(S, A(S, S))
G = A(S, Q, Q)


def c(j):
    t = G
    for _ in range(j):
        t = A(Q, t)
    return t


TEM_BODY = A(Q, A(Q, 'd'), A(Q, 'e', A(Q, A(Q, 'd'))), S)
T1_BODY = A(Q, A(Q, 'd'), A(Q, 'd', A(Q, A(Q, 'd'))), S)
T2_BODY = A(Q, 'd', A(G, A(Q, 'd')), S)
EMIT = lams(['e', 'E', 'd', 'C0'], A('E', 'd', 'C0', TEM_BODY))
END0 = lams(['m', 'd', 'C0'], A('m', A(Q, 'd'), A('B', A(EMIT, 'd'), 'C0')))
M0 = lams(['m', 'd', 'C0'], A('C0', A(END0, 'm'), 'd', 'C0', T1_BODY, T2_BODY))
AA = lams(['x', 'f'], A('f', A('x', 'x', 'f')))
TEM = lams(['e', 'd'], TEM_BODY)
T1 = lam('d', T1_BODY)
T2 = lam('d', T2_BODY)
CH0 = A('B', A(EMIT, c(0)), IR)
q = A(AA, AA, M0, c(1), CH0)

print('sizes: Emit %d, End0 %d, M0 %d, A %d, q %d' % tuple(map(size, (EMIT, END0, M0, AA, q))))
print('q atoms: code S %d, data S %d, B %d, C %d' % (count(q, 'S'), count(q, 's'), count(q, 'B'), count(q, 'C')))
assert AA == A('B', A('S', IR), A('S', IR, IR))
assert size(q) == 188 and count(q, 'S') == 15 and count(q, 's') == 82
print('A =', show(AA))
print('q =', show(q))

# ---------------------------------------------------------------- passages (Lemma 4), literal outputs
W = ['w1', 'w2', 'w3']
X = 'x'
passages = [
    ('P1', A(IR, 'x', 'y', 'z'), 'x', ['y', 'z'], 'BCC'),
    ('P2', A(AA, 'y', 'f', 'u'), 'f', [A('S', IR, IR, 'y', 'f'), 'u'], None),
    ('P3', A('S', IR, IR, 'x', 'f'), 'x', [A(IR, 'x'), 'f'], None),
    ('P4', A(M0, 'm', 'd', 'C0'), 'C0', [A(END0, 'm'), 'd', A(IR, 'C0'), A(T1, 'd'), A(T2, 'd')], None),
    ('P5', A(END0, 'm', 'd', 'C0'), 'm', [A(Q, 'd'), A('B', 'B', EMIT, 'd', 'C0')], None),
    ('P6a', A('B', 'B', EMIT, 'e', 'R', 'E', 'd', 'C0'), 'R', ['E', 'd', 'C0', A(TEM, 'e', 'd')], None),
    ('P6b', A('B', A(EMIT, 'e'), 'R', 'E', 'd', 'C0'), 'R', ['E', 'd', 'C0', A(TEM, 'e', 'd')], None),
]
NONS = ('B', 'C')
for name, t, hd, items, heads in passages:
    h, st, k, hs, sf = head_run(A(t, *W), 1000)
    assert h == hd and st == items + W, (name, h, [show(u) for u in st])
    if heads:
        assert hs == heads
    first = []
    for u in sf:
        # each S-frame's first item reaches an hnf with head B or C in at most one head step,
        # with no variable ever at the head
        h2, st2, k2, _, _ = head_run(u, 5)
        assert h2 in NONS and len(st2) <= 2 and k2 <= 1, (name, show(u))
        first.append('%s [%s-hnf after %d step]' % (show(u)[:40], h2, k2))
    print('%-3s %2d head steps (%s); output literal as stated; %d S-frames, first items: %s'
          % (name, k, hs, len(sf), '; '.join(first) if first else '-'))

# The templates reduce to the stated pure-S bodies (tooth templates, Section 3)
assert nf(A(TEM, 'e', 'd')) == TEM_BODY and nf(A(T1, 'd')) == T1_BODY and nf(A(T2, 'd')) == T2_BODY
print('Tem e d, T1 d, T2 d reduce to their bodies (d, e variables)')


# ---------------------------------------------------------------- phases (Lemma 5), literally, k < 40
def irk(k, t):
    for _ in range(k):
        t = A(IR, t)
    return t


def main_(k):
    return A('S', IR, IR, irk(k, AA), M0)


def ch(k):
    t = CH0
    for j in range(k):
        t = A('B', 'B', EMIT, c(j + 1), A(IR, t))
    return t


def phase_items(k):
    d = c(k + 1)
    es = [c(0)] + [c(j + 1) for j in range(k)]
    return [A(TEM, e, d) for e in es] + [A(T1, d), A(T2, d)]


K = 40
h, args = spine(q)
st = args[::-1]
steps = 0
below = []
for k in range(K):
    target = A(M0, main_(k), c(k + 1), ch(k))
    th, ta = spine(target)
    while not (h == th and st[::-1][:len(ta)] == ta):
        assert h in COMB and len(st) >= 3 and steps < 10 ** 6
        x, y, z = st.pop(), st.pop(), st.pop()
        nh, na = spine(contract(h, x, y, z))
        st.extend(na[::-1])
        h = nh
        steps += 1
    assert st[::-1][len(ta):] == below, k
    below = phase_items(k) + below
print('the head run of q passes through Phi_0, ..., Phi_%d literally, with the predicted items below (%d steps)'
      % (K - 1, steps))


# ---------------------------------------------------------------- teeth against p_K (S11, Sec. 3)
def pk_teeth(N):
    a = ('Q', 0, 2)
    out = []
    for _ in range(N):
        if a[0] == 'Q':
            _, j, n = a
            out.append(A(c(n), A(c(j), c(n)), S))
            a = ('Q', j - 1, n) if j >= 1 else ('G', n)
        else:
            _, n = a
            out.append(A(c(n + 1), A(c(n), c(n + 1)), S))
            a = ('Q', n - 1, n + 1)
    return out


items = st[::-1][len(ta):]
N = len(items)
teeth = items[::-1]  # tau_1 is the last item
pk = pk_teeth(N)
assert all(nf(teeth[n]) == pk[n] for n in range(N))
print('tau_n(q) reduces to tau_n(p_K) for n <= %d' % N)

# ---------------------------------------------------------------- side facts
# A A is not a fixed-point combinator: A A f ->>h C (C f) (S Ir Ir A f), an hnf with head C
h, st, k, _, _ = head_run(A(AA, AA, 'f'), 10)
assert h == 'C' and st == [A('C', 'f'), A('S', IR, IR, AA, 'f')]
print('A A f ->>h C (C f) (S Ir Ir A f) in %d steps' % k)
# (F2) fails in {S, C}: D D C is mute, D = S (C C) C
D = A('S', A('C', 'C'), 'C')
t = A(D, D, 'C')
h, st, k, hs, _ = head_run(t, 4)
assert A(h, *st) == t and hs == 'SCCC'
print('D D C ->h^4 D D C (heads %s)' % hs)
# Ir x y has an hnf: B C C x y ->h C (C x) y
h, st, k, _, _ = head_run(A(IR, 'x', 'y'), 10)
assert h == 'C' and st == [A('C', 'x'), 'y']
print('B C C x y ->>h C (C x) y, an hnf')
print('all checks passed')
