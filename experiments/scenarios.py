"""Contributor D's request sequences and frozen custom-policy hit/miss oracles."""
from datetime import datetime, timedelta, timezone
from experiments.workloads import find_resource
from cache_simulator.models import Request

EXPECTED = {
    'T1_oversize': 'MMM',
    'T2_bypass': 'MMMHHHHHHMHHH',
    'T3_freq_vs_recency': 'MHHHMMMH',
    'T4_aging': 'MHHHHMMMMMMMMMHMHMHMHMHHHMHHH',
    'T6_multi_evict': 'MMMHHHMMMH',
}


def scenarios(resources):
    key = lambda host, path: find_resource(resources, host, path)
    a, b, c = key('learn', 'index.html'), key('learn', 'main.css'), key('learn', 'logo')
    d, e, g = key('cdn', 'avatar'), key('pypi', 'warehouse'), key('learn', 'grades')
    f, v = key('learn', 'app.js'), key('video', 'intro')
    sequences = {
        'T1_oversize': [f, v, f],
        'T2_bypass': [a, c, g] * 3 + [e] + [a, c, g],
        'T3_freq_vs_recency': [a, a, a, a, b, d, e, a],
        'T4_aging': [a] * 5 + [b, d, e, c] * 6,
        'T5_tie': [a, c, e, b],
        'T6_multi_evict': [c, g, d, c, g, d, e, b, e, b],
    }
    start = datetime(2026, 10, 26, tzinfo=timezone.utc)
    return {name: [Request(i + 2, start + timedelta(seconds=i), 'c', resource)
                   for i, resource in enumerate(sequence)] for name, sequence in sequences.items()}
