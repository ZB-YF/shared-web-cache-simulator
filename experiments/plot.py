"""Create standalone figures from integrated simulator batch outputs."""
import argparse
import csv
from pathlib import Path
from statistics import mean, stdev


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=Path('report/figures'))
    args = parser.parse_args()
    # Plotting is optional; the simulator and all correctness tests use only the standard library.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import ScalarFormatter

    with (args.results_dir / 'summary.csv').open(newline='') as stream:
        summary = list(csv.DictReader(stream))
    with (args.results_dir / 'runs.csv').open(newline='') as stream:
        runs = list(csv.DictReader(stream))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    names = ('repetitive', 'sequential', 'mixed', 'scan_pollution')
    policies = ('FIFO', 'LRU', 'LFU', 'CUSTOM')
    colors = dict(FIFO='#68778b', LRU='#2b6cb0', LFU='#b7791f', CUSTOM='#168166', CUSTOM_NOADM='#9656a6')
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.grid': True, 'grid.alpha': 0.2, 'figure.dpi': 140})

    def save(fig, name):
        fig.savefig(args.output_dir / (name + '.png'), bbox_inches='tight')
        fig.savefig(args.output_dir / (name + '.svg'), bbox_inches='tight')
        plt.close(fig)

    def series(workload, policy):
        return sorted([r for r in summary if r['workload'] == workload and r['policy'] == policy],
                      key=lambda r: int(r['capacity_bytes']))

    for ablation in (False, True):
        fig, axes = plt.subplots(2, 2, figsize=(11, 7), layout='constrained')
        selected = ('CUSTOM', 'CUSTOM_NOADM') if ablation else policies
        for ax, workload in zip(axes.flat, names):
            for policy in selected:
                rows = series(workload, policy)
                x = [int(r['capacity_bytes']) / 1024 for r in rows]
                y = [float(r['average_response_time_ms_mean']) for r in rows]
                deviation = [float(r['average_response_time_ms_sample_stddev']) for r in rows]
                label = 'Custom without admission' if policy == 'CUSTOM_NOADM' else policy
                ax.plot(x, y, marker='o', label=label, color=colors[policy])
                ax.fill_between(x, [max(0, v - s) for v, s in zip(y, deviation)],
                                [v + s for v, s in zip(y, deviation)], color=colors[policy], alpha=0.1)
            ax.set(title=workload.replace('_', ' ').title(), xlabel='Cache capacity (KiB)',
                   ylabel='Average response time (ms)')
            ax.set_xscale('log', base=2)
            ax.set_xticks(x)
            ax.xaxis.set_major_formatter(ScalarFormatter())
        handles, labels = axes.flat[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='outside lower center', ncols=len(selected), frameon=False)
        title = 'Admission-filter ablation' if ablation else 'Policy comparison by cache capacity'
        fig.suptitle(title + '\nSynthetic workloads; mean over 10 seeds; shading = one sample standard deviation')
        save(fig, 'admission_ablation' if ablation else 'latency_by_capacity')

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), layout='constrained')
    rows = {r['policy']: r for r in summary if r['workload'] == 'mixed' and int(r['capacity_bytes']) == 5 * 1024 ** 2}
    panels = [('average_response_time_ms_mean', 1, 'Average response (ms)', 'Lower is better'),
              ('byte_hit_ratio_mean', 100, 'Byte-hit ratio (%)', 'Higher is better'),
              ('origin_traffic_bytes_mean', 1 / 1048576, 'Origin traffic (MiB)', 'Lower is better')]
    for ax, (field, scale, ylabel, direction) in zip(axes, panels):
        values = [float(rows[policy][field]) * scale for policy in policies]
        ax.bar(policies, values, color=[colors[policy] for policy in policies])
        ax.set(ylabel=ylabel, title=direction)
        for i, value in enumerate(values):
            ax.annotate(f'{value:.1f}', (i, value), xytext=(0, 4), textcoords='offset points', ha='center', fontsize=9)
        ax.margins(y=0.18)
    fig.suptitle('Mixed workload at 5 MiB: response-time gains have a traffic cost\nMeans over 10 synthetic seeds')
    save(fig, 'mixed_tradeoffs')

    fig, ax = plt.subplots(figsize=(8, 4.6), layout='constrained')
    clients = ('media', 'repetitive', 'unpredictable')
    for offset, policy in [(-0.18, 'LRU'), (0.18, 'CUSTOM')]:
        values, errors = [], []
        for client in clients:
            sample = [float(r['avg_rt_' + client]) for r in runs
                      if r['workload'] == 'mixed' and int(r['capacity_bytes']) == 5 * 1024 ** 2 and r['policy'] == policy]
            values.append(mean(sample))
            errors.append(stdev(sample) if len(sample) > 1 else 0)
        positions = [i + offset for i in range(len(clients))]
        ax.bar(positions, values, width=0.34, label=policy, color=colors[policy], yerr=errors, capsize=3)
        for x, value, error in zip(positions, values, errors):
            ax.annotate(f'{value:.1f}', (x, value + error), xytext=(0, 4), textcoords='offset points', ha='center', fontsize=9)
    ax.set_xticks(range(len(clients)), clients)
    ax.set(ylabel='Average response time (ms)',
           title='Client fairness trade-off: mixed workload at 5 MiB\nMean over 10 seeds; error bars = sample standard deviation')
    ax.margins(y=0.18)
    ax.legend(frameon=False)
    save(fig, 'mixed_client_latency')
    print(f'Created four figures in PNG and SVG under {args.output_dir}')


if __name__ == '__main__':
    main()
