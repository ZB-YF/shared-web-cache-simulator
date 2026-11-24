# Part I — What am I responsible for \- D

**D: Custom Policy design \+ test plan (algorithm design).** Decide the policy rules, write pseudocode, design test scenarios, and analyze the algorithm's strengths and limitations.

**D's question to answer:** *How exactly does our algorithm work, and why might it be effective?* (E's question is: how do we compare algorithms fairly, and what do the results show?)

**Final deliverables:** Custom Policy design document, pseudocode, test cases, and the algorithm-design part of the report.

**Independence rule:** D does not wait for C's LFU or for any code. A, B, C implement; D and E work independently on design/analysis, and D analyzes partial Custom results as they appear.

### Common input/output format agreed by the whole team

- **Request:** `timestamp`, `client_id`, `resource_id` (in our CSVs: `scheme`, `host`, `path`).  
- **Resource:** `resource_id`, `size_bytes`, `origin_latency_ms`.  
- **Per-request simulation result:** `request_id`, `client_id`, `resource_id`, `hit_or_miss`, `response_time_ms`, `evicted_resources`, `cache_used_bytes`.

# Part II — Design and pseudocode

## 1\. What does "better" mean?

The assignment asks us to define "better" ourselves. We define it as follows:

1. **Primary metric: lower average response time.** This is what users actually feel.  
2. **Secondary metric: higher cache-hit ratio.**  
3. **Acknowledged cost:** possibly lower byte-hit ratio, higher origin traffic, and a worse experience for large-object clients (the Media Consumer).

Rationale: FIFO, LRU and LFU look only at time or count. They ignore **resource size** and **origin latency**, yet in `resources.csv` sizes range from 2 KiB to 59 MiB and latencies from 80 ms to 1800 ms. This is exactly the "a large video evicts many small pages" scenario from the assignment.

## 2\. Policy rules: LA-GDSF (Latency-Aware Greedy-Dual-Size-Frequency)

LA-GDSF builds on classic GDSF with two changes for this project: (1) the cost term is the *latency saved by a hit*; (2) an admission filter (bypass).

### 2.1 Priority of each resource (lowest priority is evicted first)

```
H(r) = L + F(r) × C(r) / S(r)
```

&nbsp;

| Symbol | Meaning | Why |
| :---- | :---- | :---- |
| F(r) | Total number of requests for r so far (**not** reset on eviction) | Frequency; keeping history avoids "amnesia" after one eviction |
| C(r) | `origin_latency_ms − 5` (milliseconds saved by one hit) | Directly matches the average-response-time goal |
| S(r) | Resource size in KiB | Benefit per unit of space: small, expensive resources are worth keeping |
| L | Global "inflation" value (initially 0\) | Aging: the H of old resources stops growing while new resources start higher |

**Interpretation:** H estimates how many milliseconds are saved per KiB of cache occupied.

### 2.2 The three cases

On a miss, H is computed **twice**, with different purposes and different values of L. Keep them distinct:

- **H\_cand (candidate priority):** computed **before eviction** using the **current L**. It is used only for the admission comparison and is never stored.  
- **H\_ins (insertion priority):** computed **after the actual eviction, once L has been updated**, using the **new L**. This is the value stored with the resource in the cache.

Procedure:

- **Hit:** F(r)++, recompute H(r) using the current L.  
- **Miss, enough free space:** F(r)++. No eviction occurs and L is unchanged, so H\_ins \= H\_cand; insert directly.  
- **Miss, not enough space:**  
  1. Select the victim set V in ascending order of (H, tie-break: least recently used) until enough space would be freed. This step only *selects*: nothing is deleted and L is unchanged.  
  2. **Admission filter:** if H\_cand \< max{H(v) : v ∈ V}, **do not cache the new resource** (bypass). It is still counted as a miss for response time and origin traffic; nothing is evicted, **L is not updated**, and used space is unchanged. On equality the resource is admitted (strict `<`).  
  3. Otherwise evict V, set `L = max{H(v)}` (L never decreases, hence the max), **then compute H\_ins with the new L** and insert the new resource.  
- **Resource larger than the cache:** never cached; it does not enter the admission comparison, does not change L, and evicts nothing.

### 2.3 Pseudocode

```
state: cache = {}, used = 0, L = 0, freq = defaultdict(0), now = 0

function PRIORITY(r, L):                   # single formula for H
    return L + freq[r] * (lat[r]-HIT_MS) / (size[r]/1024)

function ACCESS(r):
    now += 1;  freq[r] += 1                # counted on misses too; never reset on eviction
    if r in cache:                         # ---- HIT
        cache[r].last = now
        cache[r].H = PRIORITY(r, L)        # current L
        return HIT, resp = HIT_MS
    # ---- MISS
    resp = lat[r];  origin_traffic += size[r]
    if size[r] > CAPACITY: return MISS     # oversized: never cached
    need = used + size[r] - CAPACITY
    if need <= 0:                          # enough space: no eviction, L unchanged
        insert(r, H = PRIORITY(r, L));  return MISS
    # not enough space: first SELECT victims; delete nothing, do not touch L
    victims = [];  freed = 0
    for v in sorted(cache, key=(H, last)): # lowest H first; ties: least recently used
        if freed >= need: break
        victims.append(v);  freed += size[v]
    H_cand = PRIORITY(r, L)                # (1) candidate H: before eviction, old L, comparison only
    if H_cand < max(H[v] for v in victims):
        return MISS                        # bypass: no eviction, L unchanged, used unchanged
    evict all victims;  used -= freed
    L = max(L, max(H[v] for v in victims)) # (2) update L after the actual eviction
    insert(r, H = PRIORITY(r, L))          # (3) insertion H: recomputed with the updated L
    return MISS
```

> Implementation note (consistent with `proto.py`): the admission comparison calls `_h(key)` once (old L); after eviction and the L update, `_h(key)` is called again and stored in `H[key]`. The expected values of the test cases are therefore unaffected (`python3 test_custom.py` passes).

### 2.4 Why it may work

| Mechanism | Problem solved | Assignment hint |
| :---- | :---- | :---- |
| Dividing by S(r) | A 2 MiB PDF does not push out dozens of 10 KiB pages | Resource size |
| Multiplying by F(r) | Frequently requested resources stay longer | Request frequency |
| C(r) \= latency saved | A slow resource (500 ms origin) is worth more than a fast one (80 ms) | Retrieval cost |
| Inflation value L | Formerly hot resources are eventually evicted (pure LFU cannot do this) | Recency / adaptive behavior |
| Admission filter | One-shot large objects and scans do not pollute the cache | The "video evicts pages" example |

---

# Part III — Full code

All files live in the same folder. `workloads.py` and `test_custom.py` read the provided CSVs from `/mnt/user-data/uploads/` (variable `U`); change `U` to your own path. Python 3 standard library only. This is a **reference prototype** used to validate the design, not the team's official simulator.

## Code 1: `proto.py` — Reference simulator: FIFO / LRU / LFU / Custom (LA-GDSF)

```py
"""Part D prototype: reference simulator + Custom Policy (LA-GDSF).
Purpose: validate the design on paper-and-code, produce expected outputs for D's test cases.
NOT the team's official simulator (that is A/B/C's)."""
import csv, itertools, random
from collections import OrderedDict, defaultdict

HIT_MS = 5

def load_resources(path):
    res = {}
    for r in csv.DictReader(open(path, newline='')):
        key = (r['host'], r['path'])
        res[key] = dict(size=int(r['size_bytes']), lat=int(r['origin_latency_ms']))
    return res

def load_requests(path):
    return [(r['client_id'], (r['host'], r['path'])) for r in csv.DictReader(open(path, newline=''))]

class Cache:
    def __init__(self, cap, policy, res, **kw):
        self.cap, self.policy, self.res = cap, policy, res
        self.used = 0
        self.t = 0
        self.ins = {}      # key -> insertion seq
        self.last = {}     # key -> last access time
        self.cnt = {}      # key -> count since insertion (LFU)
        # custom policy state
        self.L = 0.0
        self.H = {}
        self.freq = defaultdict(int)   # persistent request count (not reset on eviction)
        self.admission = kw.get('admission', True)
        self.use_lat = kw.get('use_lat', True)

    # ---------- custom priority ----------
    def _h(self, k):
        r = self.res[k]
        cost = (r['lat'] - HIT_MS) if self.use_lat else 1.0
        return self.L + self.freq[k] * cost / (r['size'] / 1024.0)

    def _victim_order(self, protect=None):
        keys = list(self.ins)
        p = self.policy
        if p == 'FIFO':  return sorted(keys, key=lambda k: self.ins[k])
        if p == 'LRU':   return sorted(keys, key=lambda k: self.last[k])
        if p == 'LFU':   return sorted(keys, key=lambda k: (self.cnt[k], self.last[k]))
        if p == 'CUSTOM':return sorted(keys, key=lambda k: (self.H[k], self.last[k]))

    def request(self, key):
        self.t += 1
        r = self.res[key]
        self.freq[key] += 1
        if key in self.ins:
            self.last[key] = self.t; self.cnt[key] += 1
            if self.policy == 'CUSTOM': self.H[key] = self._h(key)
            return True, []
        evicted = []
        if r['size'] > self.cap:
            return False, evicted
        need = self.used + r['size'] - self.cap
        if need > 0:
            order = self._victim_order()
            chosen, freed = [], 0
            for v in order:
                if freed >= need: break
                chosen.append(v); freed += self.res[v]['size']
            if self.policy == 'CUSTOM' and self.admission:
                # (1) H_cand: candidate priority, computed BEFORE eviction with the current (old) L; used only for this comparison
                if self._h(key) < max(self.H[v] for v in chosen):
                    return False, []          # bypass: no eviction, L unchanged, used unchanged
            for v in chosen:
                if self.policy == 'CUSTOM': self.L = max(self.L, self.H[v])   # (2) update L after the actual eviction
                self.used -= self.res[v]['size']
                for d in (self.ins, self.last, self.cnt, self.H): d.pop(v, None)
                evicted.append(v)
        self.ins[key] = self.t; self.last[key] = self.t; self.cnt[key] = 1
        if self.policy == 'CUSTOM': self.H[key] = self._h(key)   # (3) H_ins: recomputed with the updated L
        self.used += r['size']
        return False, evicted

def run(trace, res, cap, policy, **kw):
    c = Cache(cap, policy, res, **kw)
    S = dict(hits=0, n=0, bytes=0, hitbytes=0, origin=0, rt=0, per=defaultdict(lambda: [0, 0, 0]))
    log = []
    for cl, k in trace:
        hit, ev = c.request(k)
        sz, lat = res[k]['size'], res[k]['lat']
        rt = HIT_MS if hit else lat
        S['n'] += 1; S['bytes'] += sz; S['rt'] += rt
        p = S['per'][cl]; p[0] += 1; p[2] += rt
        if hit: S['hits'] += 1; S['hitbytes'] += sz; p[1] += 1
        else: S['origin'] += sz
        log.append((cl, k, hit, ev, c.used))
    S['hit_ratio'] = S['hits'] / S['n']
    S['byte_hit_ratio'] = S['hitbytes'] / S['bytes']
    S['avg_rt'] = S['rt'] / S['n']
    S['per_client'] = {c_: (v[1] / v[0], v[2] / v[0]) for c_, v in S['per'].items()}
    return S, log
```

## Code 2: `workloads.py` — Synthetic workload generators (repetitive, sequential, mixed, scan\_pollution)

```py
import random
from proto import *
U='/mnt/user-data/uploads/'
RES=load_resources(U+'resources.csv')
K={k[1].split('/')[-1] or k[1]:k for k in RES}   # short names (note: two main.css -> handled below)
def key(host_sub,path_sub):
    return [k for k in RES if host_sub in k[0] and path_sub in k[1]][0]
SMALL=[key('learn','index.html'),key('learn','main.css'),key('learn','logo.svg'),key('cdn','avatar'),
       key('learn','announcements'),key('learn','grades'),key('learn','app.js')]
MED=[key('learn','syllabus'),key('library','cache-repl'),key('cdn','banner'),key('mozilla','HTTP'),
     key('mozilla','main.js'),key('mozilla','main.css'),key('pypi','warehouse'),key('pypi','requests'),key('learn','quiz')]
LARGE=[key('learn','lecture07'),key('learn','lecture08')]
VIDEO=[key('video','intro'),key('video','networking')]
ALL=list(RES)

def zipf(items,n,rng,s=1.0):
    w=[1/(i+1)**s for i in range(len(items))]
    return rng.choices(items,weights=w,k=n)

def repetitive(rng,n=600):
    return [('student-01',k) for k in zipf(SMALL+MED[:3],n,rng,1.2)]
def sequential(rng,n=600):
    pool=ALL[:]; out=[]
    for i in range(n):
        out.append(('student-02',pool[i%len(pool)] if rng.random()<0.8 else rng.choice(pool)))
    return out
def mixed(rng,n=1200):
    out=[]
    for i in range(n):
        r=rng.random()
        if r<0.5:   out.append(('repetitive',zipf(SMALL+MED[:3],1,rng,1.2)[0]))
        elif r<0.7: out.append(('media',rng.choice(LARGE+VIDEO[:1]) if rng.random()<0.3 else rng.choice(LARGE+MED[:2])))
        else:       out.append(('unpredictable',rng.choice(ALL)))
    return out
def scan_pollution(rng,n=1200):
    """hot set of small pages + periodic one-shot large-object bursts (the 'video evicts pages' example)"""
    out=[]; vids=LARGE+VIDEO
    for i in range(n):
        if i%40==39: out.append(('media',rng.choice(vids)))
        else: out.append(('repetitive',zipf(SMALL,1,rng,1.0)[0]))
    return out
WORKLOADS=dict(repetitive=repetitive,sequential=sequential,mixed=mixed,scan_pollution=scan_pollution)
CAPS=[100*1024,500*1024,1024**2,5*1024**2,10*1024**2]
```

## Code 3: `scen.py` — Hand-checkable test scenarios T1–T4, T6

```py
from workloads import *
def k(h,p): return key(h,p)
A=k('learn','index.html');B=k('learn','/static/main.css');C=k('learn','logo');D=k('cdn','avatar');E=k('pypi','warehouse')
G=k('learn','grades');F=k('learn','app.js');V=k('video','intro')
N={A:'A',B:'B',C:'C',D:'D',E:'E',G:'G',F:'F',V:'V'}
CAP=102400   # 100 KiB
SC={
'T1_oversize':[F,V,F],
'T2_bypass':[A,C,G]*3+[E]+[A,C,G],
'T3_freq_vs_recency':[A,A,A,A,B,D,E,A],
'T4_aging':[A]*5+[B,D,E,C]*6,
'T6_multi_evict':[C,G,D,C,G,D,E,B,E,B],
}
if __name__=='__main__':
    for n,t in SC.items():
        print('\n',n,''.join(N[x] for x in t))
        for pol in ['LRU','LFU','CUSTOM']:
            S,log=run([('c',x) for x in t],RES,CAP,pol)
            print(' ',pol.ljust(6),' '.join(f"{N[l[1]]}:{'H' if l[2] else 'M'}"+(f"(-{''.join(N[e] for e in l[3])})" if l[3] else '') for l in log),f"| hits={S['hits']}")
```

## Code 4: `test_custom.py` — Test runner with assertions

```py
"""Part D: Custom Policy test cases (T1-T4, T6 + reference trace). Run: python3 test_custom.py"""
from scen import *
U = '/mnt/user-data/uploads/'   # change if your files are elsewhere

def hm(t, pol):
    S, log = run([('c', x) for x in t], RES, CAP, pol)
    return ''.join('H' if l[2] else 'M' for l in log), log, S

FROZEN = {  # expected Custom hit/miss sequences (derived by hand, then frozen)
 'T1_oversize': 'MMM',
 'T2_bypass': 'MMMHHHHHHMHHH',
 'T3_freq_vs_recency': 'MHHHMMMH',
 'T4_aging': 'MHHHHMMMMMMMMMHMHMHMHMHHHMHHH',
 'T6_multi_evict': 'MMMHHHMMMH',
}
for name, exp in FROZEN.items():
    got, _, _ = hm(SC[name], 'CUSTOM')
    assert got == exp, (name, got, exp)
    print('PASS', name)

# T1: oversized resources are never cached
_, log, _ = hm(SC['T1_oversize'], 'CUSTOM'); assert all(l[4] == 0 for l in log)
# T2: a one-shot E must not push out the hot set A/C/G (bypass); LRU cannot do this
assert hm(SC['T2_bypass'], 'CUSTOM')[0][-3:] == 'HHH' and hm(SC['T2_bypass'], 'LRU')[0][-3:] != 'HHH'
# T4: Custom eventually evicts the formerly hot A via aging; LFU never evicts A
_, logc, _ = hm(SC['T4_aging'], 'CUSTOM'); _, logl, _ = hm(SC['T4_aging'], 'LFU')
assert any(A in l[3] for l in logc) and not any(A in l[3] for l in logl)
# invariant: used <= capacity at every step
for n, t in SC.items():
    assert all(l[4] <= CAP for l in hm(t, 'CUSTOM')[1])
# reference trace
tr = load_requests(U + 'requests_reference.csv')
S, _ = run(tr, RES, CAP, 'CUSTOM')
assert S['hits'] == 7 and abs(S['avg_rt'] - 68.667) < 0.01, S['hits']
print('PASS reference trace: hits=7, avg_rt=%.2f ms, origin=%d bytes' % (S['avg_rt'], S['origin']))
print('ALL TESTS PASSED')
```

## Code 5: `make_results.py` — Generates results\_D.csv for E

```py
"""Generate results_D.csv for E (mean of 10 random seeds)"""
from workloads import *
import csv, statistics
POL=[('FIFO',{}),('LRU',{}),('LFU',{}),('CUSTOM',dict(admission=True)),('CUSTOM_noadm',dict(admission=False))]
rows=[]
for wn,wf in WORKLOADS.items():
    for cap in CAPS:
        for name,kw in POL:
            m=defaultdict(list)
            for s in range(10):
                S,_=run(wf(random.Random(s)),RES,cap,name.split('_')[0],**kw)
                for q in ('hit_ratio','byte_hit_ratio','avg_rt','origin'): m[q].append(S[q])
                for c,(h,rt) in S['per_client'].items(): m['hr:'+c].append(h); m['rt:'+c].append(rt)
            base=dict(workload=wn,cap_KiB=cap//1024,policy=name,**{q:round(statistics.mean(m[q]),4) for q in ('hit_ratio','byte_hit_ratio','avg_rt','origin')})
            base['origin_MiB']=round(base.pop('origin')/1048576,3)
            for c in sorted({k[3:] for k in m if k.startswith('hr:')}):
                base['hit_ratio_'+c]=round(statistics.mean(m['hr:'+c]),4); base['avg_rt_'+c]=round(statistics.mean(m['rt:'+c]),2)
            rows.append(base)
keys=sorted({k for r in rows for k in r},key=lambda x:(not x in('workload','cap_KiB','policy'),x))
with open('results_D.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['workload','cap_KiB','policy','hit_ratio','byte_hit_ratio','avg_rt','origin_MiB']+[k for k in keys if k.startswith(('hit_ratio_','avg_rt_'))]); w.writeheader(); w.writerows(rows)
print(len(rows),'rows')
```

## How to run

```
python3 test_custom.py      # runs all test cases; prints PASS lines and "ALL TESTS PASSED"
python3 scen.py             # prints per-request H/M sequences for LRU, LFU, Custom on each scenario
python3 make_results.py     # regenerates results_D.csv (10 seeds x 4 workloads x 5 capacities x 5 policy variants)
```

Reference-trace check against the official expected CSVs: running `proto.py`'s `run()` with `FIFO`, `LRU` and `LFU` on `requests_reference.csv` (capacity 102400\) reproduces every hit/miss in `expected_fifo.csv`, `expected_lru.csv`, `expected_lfu.csv`.

---

# Part IV — Test cases, results, and report text

## 1\. Parameters and suggested ablations (for C/E)

| Variant | Setting | Purpose |
| :---- | :---- | :---- |
| CUSTOM (main) | cost \= latency − 5, bypass enabled | Main results in the report |
| CUSTOM\_noadm | bypass disabled | Measure the contribution of the admission filter |
| Optional: cost \= 1 | Degenerates to GDSF (frequency/size only) | Measure the contribution of the latency term (`use_lat=False` in the prototype) |

&nbsp;Test cases (5 scenarios \+ reference trace)

Common configuration: 100 KiB capacity, 5 ms hit latency. Resource abbreviations: A \= index.html (32 KiB), B \= main.css (42 KiB), C \= logo.svg (14 KiB), D \= avatar (24 KiB), E \= warehouse.css (57 KiB), G \= grades (7 KiB), F \= app.js (186 KiB), V \= intro video (57 MiB). Run with `python3 test_custom.py` (all pass). The Custom H/M sequences were derived by hand and then frozen.

| ID | Request sequence | What it checks | Expected Custom result (H \= hit, M \= miss) | Comparison |
| :---- | :---- | :---- | :---- | :---- |
| T1 Oversized | F V F | F and V exceed 100 KiB and are never cached; used stays 0 | `MMM` | Same for all standard policies |
| T2 Admission filter | (A C G)×3, E, A C G | A one-shot E (57 KiB) must not push out the hot set | `MMMHHHHHH M HHH`; E is bypassed and the hot set then hits (9 hits) | LRU 6 hits, LFU 8 hits |
| T3 Frequency vs recency | A A A A B D E A | The frequently used A must survive later scanning | `MHHHMMMH` (4 hits); A stays | LRU 3 hits (A evicted) |
| T4 Aging | A×5, then (B D E C)×6 cycle | A formerly hot resource (A) is eventually evicted and stops occupying space | 14 hits in total; A is evicted at step 20 (`E:M(-A)`) | LFU only 4 hits and **never evicts A** (pollution); LRU 4 hits |
| T6 Multi-eviction | C G D C G D E B E B | Eviction/rejection logic when space is short; used ≤ capacity | `MMMHHHMMMH` (4 hits) | LRU 5 hits (honest note: Custom is not the best here) |
| Reference trace | requests\_reference.csv | Comparison on the official 15-step trace | **7 hits, 68.67 ms average, 292 KiB origin traffic** | FIFO 3 / 95.33; LRU 3 / 92.33; LFU 4 / 84.33 |

**Reference trace step by step (Custom):** at steps 6 and 9 (D and E) the new resource is bypassed because its H\_cand is lower than its victims'. At step 11, D has H \= 2×90/24 \= 7.5 \> B's 3×85/42 ≈ 6.07, so B is evicted and D inserted. At step 15, B evicts D. Hits occur at steps 4, 5, 7, 8, 10, 12, 14\. Note: the reference trace has no official expected output for a custom policy; these are our own results. **The official implementation by A/C should match `proto.py` on these 15 steps**, which makes them a regression test for Custom.

## 2\. Pilot results (synthetic workloads, mean of 10 random seeds)

| Workload / capacity | Metric | FIFO | LRU | LFU | Custom |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Repetitive, 1 MiB | Hit ratio / avg response (ms) | 0.80 / 36.0 | 0.83 / 33.0 | 0.90 / 25.0 | **0.95 / 19.5** |
| Sequential, 1 MiB | Hit ratio / avg response (ms) | 0.14 / 333 | 0.14 / 334 | 0.32 / 304 | **0.64 / 251** |
| Mixed, 1 MiB | Hit ratio / avg response (ms) | 0.44 / 224 | 0.46 / 223 | 0.58 / 211 | **0.69 / 193** |
| Mixed, 5 MiB | Origin traffic (MiB) | 3111 | 3103 | 3107 | 3133 (worse) |
| Mixed, 5 MiB | Byte-hit ratio | 0.091 | 0.093 | 0.092 | 0.084 (worse) |

When the capacity is large enough (e.g., ≥ 5 MiB for Repetitive and Scan workloads) all four policies are identical: every hot resource fits, so the replacement policy no longer matters. This is itself a finding about how capacity changes the relative performance of policies.

**Per client (Mixed, 5 MiB; hit ratio / average response in ms):**

| Policy | media | repetitive | unpredictable |
| :---- | :---- | :---- | :---- |
| LRU | 0.65 / 297 | 0.82 / 29 | 0.51 / 240 |
| Custom | 0.63 / **327** | 0.98 / 7 | 0.81 / 188 |

Custom greatly helps the overall workload and the other two clients, but the **media client gets slightly worse**. This is a direct "yes" to the assignment's question "Can a policy improve overall performance while making one client's experience worse?"

## 3\. Strengths, limitations, and applicable conditions

**Strengths**

- Lowest average response time on workloads with a small hot set plus occasional large objects (Mixed, Scan\_pollution) and on cyclic scans, the classic weakness of LRU/FIFO (Sequential).  
- Unlike LFU, it is not held hostage by formerly popular objects (T4).

**Limitations (must be acknowledged in the report)**

1. **Bias toward small resources:** large resources (lecture PDFs, videos) almost never enter the cache, so byte-hit ratio and origin traffic can be worse and the Media client is slightly hurt.  
2. **A higher hit ratio does not imply lower traffic:** the policy optimizes hit count/time, not bytes. This is a direct example for the assignment's questions 1 and 2\.  
3. **Extra metadata:** F (including for evicted resources) and H are stored per resource; eviction requires ordering. A naive implementation costs O(n log n) per eviction; a min-heap reduces it to O(log n).  
4. **Depends on known origin latency:** if latency estimates are inaccurate, C(r) is distorted.  
5. **No explicit fairness mechanism:** fairness could be added (e.g., per-client weighting) but is not part of the main version. **The report must not claim a fairness design.**  
6. The numbers above come from **our own synthetic workloads**, not the instructor's traces; the conclusions must be re-checked against the official data produced by C.

## 4\. Interface suggestions for A / C (non-blocking)

- Inputs the policy needs: resource `size_bytes`, `origin_latency_ms`, logical time, and the global request count `freq[r]` (**increment it on misses too, before the decision, and never reset it on eviction**).  
- A "compute victims without committing" step is required, because the admission filter inspects the victims before deciding whether to bypass. A bypass must be logged as MISS, evicted \= `-`, used unchanged.  
- Hit response time is fixed at 5 ms; in Custom, C(r) \= latency − 5\.  
- When H values are equal, break ties by least recently used so different implementations agree.  
- Compute H\_cand with the old L and H\_ins with the updated L, exactly as in §5.2/§5.3.  
- Regression test: the results of `proto.py` on the reference trace are in §4.

## 5\. Self-check against the division-of-labor table

| Requirement | Status |
| :---- | :---- |
| 2–3 design ideas, then pick one | Candidates: (1) LRU \+ size threshold, (2) GDSF \+ latency (chosen), (3) per-client quota-based fair cache. Chosen (2) because it maps directly to the primary metric and is explainable |
| Complete rules \+ pseudocode | §2 |
| At least 5 test scenarios | §4 (T1–T4, T6 \+ reference trace) |
| Capacity / eviction rule checks | `test_custom.py` includes the used ≤ capacity invariant |
| Pros/cons per workload, capacity sensitivity | §5, §6 |
| Custom Policy section of the report | §8 |

&nbsp;