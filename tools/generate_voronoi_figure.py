"""Regenerate Figure 13.4; optional authoring dependencies: numpy and scipy.

Run from the project root. The book itself needs only the generated TikZ file.
Boundary samples approximate the segment-site medial axis. Same-segment ridges
and ridges inside obstacles are removed. Projections and the highlighted route
are computed on the resulting network, not selected by hand.
"""
import heapq
import math
from pathlib import Path

import numpy as np
from scipy.spatial import Voronoi

POLYGONS = [
    [(1.3, 4.1), (2.2, 6.1), (2.9, 4), (2.1, 4.4)],
    [(4.4, 5.7), (5.7, 6.3), (6.7, 5.6), (5.3, 4.7)],
    [(2.1, 1.4), (2, 2.4), (5.8, 2.4), (6.3, 1.3), (4, 1.8)],
]
WALL = [(0, 0), (8, 0), (8, 7), (0, 7)]
SPACING = .008


def foot(p, a, b):
    v = b - a
    t = float(np.clip(np.dot(p - a, v) / np.dot(v, v), 0, 1))
    return a + t * v


def inside(p, polygon):
    x, y = p
    result = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        if (a[1] > y) != (b[1] > y):
            if x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
                result = not result
    return result


def free(p):
    return (0 < p[0] < 8 and 0 < p[1] < 7
            and not any(inside(p, poly) for poly in POLYGONS))


segments, samples, memberships = [], [], []
lookup = {}
for poly in POLYGONS + [WALL]:
    for a, b in zip(poly, poly[1:] + poly[:1]):
        a, b = np.array(a, dtype=float), np.array(b, dtype=float)
        edge_id = len(segments)
        segments.append((a, b))
        n = math.ceil(np.linalg.norm(b - a) / SPACING)
        for t in np.linspace(0, 1, n + 1):
            p = a + t * (b - a)
            key = tuple(np.round(p, 10))
            if key not in lookup:
                lookup[key] = len(samples)
                samples.append(p)
                memberships.append(set())
            memberships[lookup[key]].add(edge_id)

vor = Voronoi(np.array(samples))
vertices = [p.copy() for p in vor.vertices]
edges = []
errors = []
for (s, t), ridge in zip(vor.ridge_points, vor.ridge_vertices):
    if len(ridge) != 2 or -1 in ridge:
        continue
    if memberships[s] & memberships[t]:
        continue  # Artificial normal rays between samples on one straight edge.
    u, v = ridge
    midpoint = (vertices[u] + vertices[v]) / 2
    if not free(midpoint):
        continue
    # Reject transitions between adjacent feature samples whose true nearest
    # contact is the same shared vertex, rather than two distinct contacts.
    candidates = []
    for ids in (memberships[s], memberships[t]):
        feet = [foot(midpoint, *segments[k]) for k in ids]
        candidates.append(min(feet, key=lambda p: np.linalg.norm(p - midpoint)))
    if np.linalg.norm(candidates[0] - candidates[1]) < SPACING:
        continue
    distances = [np.linalg.norm(midpoint - p) for p in candidates]
    nearest = min(np.linalg.norm(midpoint - foot(midpoint, *seg)) for seg in segments)
    errors.append(max(distances) - nearest)
    edges.append((u, v))

# Boundary-sampling error is bounded by half a sampling interval in distance.
assert max(errors) < SPACING, max(errors)


def project(q):
    best = None
    for k, (u, v) in enumerate(edges):
        p = foot(q, vertices[u], vertices[v])
        distance = np.linalg.norm(q - p)
        if best is None or distance < best[0]:
            best = distance, k, p
    _, k, p = best
    u, v = edges.pop(k)
    node = len(vertices)
    vertices.append(p)
    edges.extend([(u, node), (node, v)])
    # Check the entire access segment, including near each endpoint.
    assert all(free(q * (1 - t) + p * t) for t in np.linspace(0, 1, 501))
    return node


qs, qg = np.array([7.6, 4.7]), np.array([.35, 2.2])
rs, rg = project(qs), project(qg)
adj = {}
for u, v in edges:
    w = float(np.linalg.norm(vertices[u] - vertices[v]))
    adj.setdefault(u, []).append((v, w))
    adj.setdefault(v, []).append((u, w))
cost, parent, queue = {rs: 0.}, {}, [(0., rs)]
while queue:
    d, u = heapq.heappop(queue)
    if d != cost[u]:
        continue
    if u == rg:
        break
    for v, w in adj[u]:
        if d + w < cost.get(v, math.inf):
            cost[v], parent[v] = d + w, u
            heapq.heappush(queue, (d + w, v))
assert rg in cost, 'The projected points must be connected.'
route = [rg]
while route[-1] != rs:
    route.append(parent[route[-1]])
route.reverse()


def fmt(p):
    return f'({p[0]:.5f},{p[1]:.5f})'


def simplify(points, tolerance=.0008):
    if len(points) <= 2:
        return points
    a, b = points[0], points[-1]
    if np.linalg.norm(b - a) < 1e-10:
        return points
    distances = [np.linalg.norm(p - foot(p, a, b)) for p in points[1:-1]]
    k = int(np.argmax(distances)) + 1
    if distances[k - 1] <= tolerance:
        return [a, b]
    return simplify(points[:k + 1])[:-1] + simplify(points[k:])


# Join degree-two ridge vertices into polylines, preserving junctions.
used, chains = set(), []
for start in adj:
    if len(adj[start]) == 2:
        continue
    for nxt, _ in adj[start]:
        if tuple(sorted((start, nxt))) in used:
            continue
        chain, previous, current = [start, nxt], start, nxt
        used.add(tuple(sorted((start, nxt))))
        while len(adj[current]) == 2:
            following = next(v for v, _ in adj[current] if v != previous)
            key = tuple(sorted((current, following)))
            if key in used:
                break
            used.add(key)
            chain.append(following)
            previous, current = current, following
        chains.append(chain)
# Retain any isolated cycles as well.
for u, v in edges:
    if tuple(sorted((u, v))) not in used:
        chains.append([u, v])

out = [r'% Generated by tools/generate_voronoi_figure.py; do not edit by hand.',
       r'\begin{tikzpicture}[scale=.95]',
       r'\draw[line width=3pt,gray!65] (0,0) rectangle (8,7);']
for poly in POLYGONS:
    out.append(r'\filldraw[fill=gray!65] ' + '--'.join(fmt(p) for p in poly) + '--cycle;')
for p, label in [((2.15,5),'1'), ((5.55,5.55),'2'), ((3.3,2.1),'3')]:
    out.append(r'\node[white] at ' + fmt(p) + r' {$\mathcal C_' + label + '$};')
for chain in chains:
    out.append(r'\draw[green!45!black,thick] ' + '--'.join(fmt(p) for p in simplify([vertices[n] for n in chain])) + ';')
out.append(r'\draw[red!75!black,very thick] ' + '--'.join(fmt(p) for p in simplify([vertices[n] for n in route])) + ';')
for n in adj:
    if len(adj[n]) >= 3:
        out.append(r'\filldraw[draw=green!45!black,fill=white] ' + fmt(vertices[n]) + ' circle(.055);')
for q, r, sub, anchor in [(qs, rs, 'S', 'left'), (qg, rg, 'G', 'right')]:
    out.append(r'\draw[red!75!black,dashed,thick] ' + fmt(q) + '--' + fmt(vertices[r]) + ';')
    out.append(r'\fill ' + fmt(q) + r' circle(.045) node[below] {$q_' + sub + '$};')
    out.append(r'\fill[red!75!black] ' + fmt(vertices[r]) + r' circle(.05) node[' + anchor + r'] {$r_' + sub + '$};')
out.append(r'\end{tikzpicture}')
Path('figures/lecture13/roadmap.tex').write_text('\n'.join(out) + '\n', encoding='utf-8')
print(f'{len(samples)} boundary samples; {len(edges)} ridges; {len(chains)} branches.')
print(f'Maximum nearest-feature distance residual: {max(errors):.6f}; spacing {SPACING}.')
print(f'Projections: {vertices[rs]}, {vertices[rg]}; connected route length {cost[rg]:.4f}.')
