"""Plot the instructor-provided fixed-trace experiments without altering results."""
import argparse
import csv
from pathlib import Path

WORKLOADS = ('sequential', 'repetitive', 'mixed')
POLICIES = ('FIFO', 'LRU', 'LFU', 'CUSTOM')
COLORS = {'FIFO': '#68778b', 'LRU': '#2869a6', 'LFU': '#ad7617', 'CUSTOM': '#168166'}


def read_rows(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True, help='A new or empty directory')
    args = parser.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        parser.error('Output directory must be new or empty')
    runs = read_rows(args.results_dir / 'runs.csv')
    clients = read_rows(args.results_dir / 'per_client.csv')
    popularity = read_rows(args.results_dir / 'characterization/resource_popularity.csv')
    characterization = read_rows(args.results_dir / 'characterization/summary.csv')
    oversized = read_rows(args.results_dir / 'characterization/oversized_requests.csv')
    capacities = sorted({int(row['capacity_bytes']) for row in runs})
    expected = {(w, c, p) for w in WORKLOADS for c in capacities for p in POLICIES}
    actual = [(r['workload'], int(r['capacity_bytes']), r['policy']) for r in runs]
    if not capacities or len(actual) != len(set(actual)) or set(actual) != expected or 5242880 not in capacities:
        parser.error('Plots require three workloads, all four primary policies, and a 5 MiB capacity')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.rcParams.update({'font.size': 9, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.grid': True,
                         'grid.alpha': 0.2, 'axes.axisbelow': True, 'figure.dpi': 150})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    lookup = {(r['workload'], int(r['capacity_bytes']), r['policy']): r for r in runs}
    cap_labels = [f'{c / 1024:g} KiB' if c < 1048576 else f'{c / 1048576:g} MiB'
                  for c in capacities]

    def save(fig, name):
        for extension in ('png', 'svg'):
            fig.savefig(args.output_dir / f'{name}.{extension}', bbox_inches='tight')
        plt.close(fig)

    def legend(fig, axes):
        handles, labels = axes.flat[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='outside lower center', ncols=4, frameon=False)

    # Characterization: rank distributions preserve identity in the companion CSV.
    fig, axes = plt.subplots(2, 2, figsize=(8, 5.5), layout='constrained')
    shades = ('#2869a6', '#ad7617', '#168166')
    summaries = {r['workload']: r for r in characterization}
    for workload, color in zip(WORKLOADS, shades):
        rows = sorted((r for r in popularity if r['workload'] == workload), key=lambda r: int(r['rank']))
        axes[0, 0].plot([int(r['rank']) for r in rows],
                        [100 * float(r['request_share']) for r in rows],
                        marker='.', label=workload.title(), color=color)
    axes[0, 0].set(xlabel='Resource popularity rank', ylabel='Share of requests (%)',
                   title='Popularity concentration')
    axes[0, 0].legend(frameon=False)
    volumes = [int(summaries[w]['requested_bytes']) / 1048576 for w in WORKLOADS]
    axes[0, 1].bar(WORKLOADS, volumes, color=shades)
    axes[0, 1].set(ylabel='Requested data (MiB)', title='Total requested volume')
    for i, value in enumerate(volumes):
        axes[0, 1].annotate(f'{value:,.1f}', (i, value), xytext=(0, 4),
                           textcoords='offset points', ha='center')
    axes[0, 1].margins(y=0.18)
    for workload, color in zip(WORKLOADS, shades):
        rows = {int(r['capacity_bytes']): r for r in oversized if r['workload'] == workload}
        axes[1, 0].plot(range(len(capacities)),
                       [int(rows[c]['oversized_resource_requests']) for c in capacities],
                       marker='o', label=workload.title(), color=color)
    axes[1, 0].set_xticks(range(len(capacities)), cap_labels, rotation=20)
    axes[1, 0].set(ylabel='Requests larger than capacity', title='Uncacheable requests by capacity')
    client_ids = sorted({r['client_id'] for r in clients})
    bottoms = [0] * 3
    palette = plt.get_cmap('tab10')
    for index, client in enumerate(client_ids):
        values = []
        for workload in WORKLOADS:
            row = next(r for r in clients if r['workload'] == workload and r['client_id'] == client
                       and int(r['capacity_bytes']) == 5242880 and r['policy'] == 'FIFO')
            values.append(int(row['request_count']))
        axes[1, 1].bar(WORKLOADS, values, bottom=bottoms, label=client, color=palette(index))
        bottoms = [a + b for a, b in zip(bottoms, values)]
    axes[1, 1].set(ylabel='Requests', title='Client request counts')
    axes[1, 1].legend(fontsize=7, ncols=2, frameon=False)
    fig.suptitle('Instructor-provided workload characterization\nOne resource metadata file; popularity ranks are workload specific')
    save(fig, 'workload_characteristics')

    panels = [('hit_ratio', 100, 'Cache-hit ratio (%)'),
              ('byte_hit_ratio', 100, 'Byte-hit ratio (%)'),
              ('average_response_time_ms', 1, 'Average response (ms)'),
              ('origin_traffic_bytes', 1 / 1048576, 'Origin traffic (MiB)'),
              ('cache_evictions', 1, 'Evicted resources'),
              ('average_cache_utilization', 100, 'Average cache utilization (%)')]
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.7), layout='constrained')
    for ax, (field, scale, label) in zip(axes.flat, panels):
        for index, policy in enumerate(POLICIES):
            x = [i + (index - 1.5) * 0.2 for i in range(3)]
            y = [float(lookup[(w, 5242880, policy)][field]) * scale for w in WORKLOADS]
            ax.bar(x, y, width=0.19, label=policy, color=COLORS[policy])
        ax.set_xticks(range(3), [w.title() for w in WORKLOADS])
        ax.set(ylabel=label)
    legend(fig, axes)
    fig.suptitle('Policy comparison at 5 MiB\nOne deterministic replay per policy and instructor-provided trace')
    save(fig, 'policy_comparison_5mib')

    for filename, fields in (
        ('capacity_effects', [('hit_ratio', 100, 'Cache-hit ratio (%)'),
                              ('average_response_time_ms', 1, 'Average response (ms)')]),
        ('capacity_storage', [('origin_traffic_bytes', 1 / 1048576, 'Origin traffic (MiB)'),
                              ('cache_evictions', 1, 'Evicted resources'),
                              ('average_cache_utilization', 100, 'Average utilization (%)')]),
    ):
        fig, axes = plt.subplots(3, len(fields), figsize=(5 * len(fields), 8.7), layout='constrained', squeeze=False)
        for row_index, workload in enumerate(WORKLOADS):
            for col_index, (field, scale, label) in enumerate(fields):
                ax = axes[row_index, col_index]
                for policy in POLICIES:
                    y = [float(lookup[(workload, c, policy)][field]) * scale for c in capacities]
                    ax.plot(range(len(capacities)), y, marker='o', markersize=4,
                            label=policy, color=COLORS[policy])
                ax.set_xticks(range(len(capacities)), cap_labels, rotation=20)
                ax.set(ylabel=label, title=workload.title())
        legend(fig, axes)
        fig.suptitle('Impact of cache capacity\nInstructor-provided fixed traces; capacities are distinct configurations')
        save(fig, filename)

    # A compact capacity figure fits the four-page technical report.
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.9), layout='constrained', squeeze=False)
    for ax, workload in zip(axes.flat, WORKLOADS):
        for policy in POLICIES:
            ax.plot(range(len(capacities)),
                    [float(lookup[(workload, c, policy)]['average_response_time_ms']) for c in capacities],
                    marker='o', markersize=4, label=policy, color=COLORS[policy])
        ax.set_xticks(range(len(capacities)), cap_labels, rotation=40)
        ax.tick_params(axis='x', labelsize=7)
        ax.set(ylabel='Average response (ms)', title=workload.title())
    legend(fig, axes)
    fig.suptitle('Average response time by cache capacity')
    save(fig, 'capacity_latency')

    mixed = [r for r in clients if r['workload'] == 'mixed' and int(r['capacity_bytes']) == 5242880]
    fig, axes = plt.subplots(2, 1, figsize=(11, 6.7), layout='constrained', squeeze=False)
    for ax, (field, scale, label) in zip(axes.flat,
                                       [('hit_ratio', 100, 'Cache-hit ratio (%)'),
                                        ('average_response_time_ms', 1, 'Average response (ms)')]):
        for index, policy in enumerate(POLICIES):
            y = [float(next(r for r in mixed if r['policy'] == policy and r['client_id'] == c)[field]) * scale
                 for c in client_ids]
            x = [i + (index - 1.5) * 0.2 for i in range(len(client_ids))]
            ax.bar(x, y, width=0.19, label=policy, color=COLORS[policy])
        ax.set_xticks(range(len(client_ids)), client_ids)
        ax.set(ylabel=label)
    legend(fig, axes)
    fig.suptitle('Individual clients: mixed workload at 5 MiB\nClients share one cache; these are observed request outcomes')
    save(fig, 'mixed_clients_5mib')
    print(f'Created six figures in PNG and SVG: {args.output_dir}')


if __name__ == '__main__':
    main()
