"""Portable adaptation of contributor D's seeded synthetic workload generators.

These traces are generated experiments, not instructor-provided browsing data.
Selection order and random calls intentionally match D's prototype.
"""
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
import random
from urllib.parse import urlsplit

from cache_simulator.models import Request

CAPACITIES = (100 * 1024, 500 * 1024, 1024 ** 2, 5 * 1024 ** 2, 10 * 1024 ** 2)
NAMES = ('repetitive', 'sequential', 'mixed', 'scan_pollution')


def find_resource(resources, host_fragment, path_fragment):
    matches = [key for key in resources
               if host_fragment in urlsplit(key).netloc and path_fragment in urlsplit(key).path]
    if len(matches) != 1:
        raise ValueError(f'Expected one resource matching {host_fragment} / {path_fragment}; got {len(matches)}')
    return matches[0]


def generate(resources, workload, seed, count=None):
    if workload not in NAMES:
        raise ValueError(f'Unknown workload: {workload}')
    rng = random.Random(seed)
    key = lambda host, path: find_resource(resources, host, path)
    small = [key('learn', 'index.html'), key('learn', 'main.css'), key('learn', 'logo.svg'),
             key('cdn', 'avatar'), key('learn', 'announcements'), key('learn', 'grades'), key('learn', 'app.js')]
    medium = [key('learn', 'syllabus'), key('library', 'cache-repl'), key('cdn', 'banner'),
              key('mozilla', 'HTTP'), key('mozilla', 'main.js'), key('mozilla', 'main.css'),
              key('pypi', 'warehouse'), key('pypi', 'requests'), key('learn', 'quiz')]
    large = [key('learn', 'lecture07'), key('learn', 'lecture08')]
    video = [key('video', 'intro'), key('video', 'networking')]
    all_resources = list(resources)
    n = count if count is not None else (600 if workload in ('repetitive', 'sequential') else 1200)
    if n < 0:
        raise ValueError('Request count must not be negative')

    def zipf(items, amount, exponent):
        return rng.choices(items, weights=[1 / (i + 1) ** exponent for i in range(len(items))], k=amount)

    trace = []
    if workload == 'repetitive':
        trace = [('student-01', resource) for resource in zipf(small + medium[:3], n, 1.2)]
    elif workload == 'sequential':
        for i in range(n):
            resource = all_resources[i % len(all_resources)] if rng.random() < 0.8 else rng.choice(all_resources)
            trace.append(('student-02', resource))
    elif workload == 'mixed':
        for _ in range(n):
            chance = rng.random()
            if chance < 0.5:
                trace.append(('repetitive', zipf(small + medium[:3], 1, 1.2)[0]))
            elif chance < 0.7:
                resource = (rng.choice(large + video[:1]) if rng.random() < 0.3
                            else rng.choice(large + medium[:2]))
                trace.append(('media', resource))
            else:
                trace.append(('unpredictable', rng.choice(all_resources)))
    else:
        for i in range(n):
            if i % 40 == 39:
                trace.append(('media', rng.choice(large + video)))
            else:
                trace.append(('repetitive', zipf(small, 1, 1.0)[0]))
    start = datetime(2026, 10, 26, 9, tzinfo=timezone.utc)
    return [Request(i + 2, start + timedelta(seconds=i), client, resource)
            for i, (client, resource) in enumerate(trace)]


def write_trace(path: Path, requests):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(('timestamp', 'client_id', 'method', 'scheme', 'host', 'path'))
        for request in requests:
            parts = urlsplit(request.resource_id)
            path_value = parts.path + ('?' + parts.query if parts.query else '')
            writer.writerow((request.timestamp.isoformat(), request.client_id, 'GET',
                             parts.scheme, parts.netloc, path_value))
