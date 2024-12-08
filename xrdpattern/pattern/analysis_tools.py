from typing import Optional

import numpy as np
from matplotlib import pyplot as plt
from tabulate import tabulate
from collections import Counter

from xrdpattern.pattern import XrdPattern, PatternDB
from xrdpattern.xrd import LabelType

# -----------------------------------------

def compute_average_dot_product(patterns : list[XrdPattern]) -> float:
    n = len(patterns)
    normalized_dot_products = []

    def compute_dot_prod(p1: XrdPattern, p2 : XrdPattern):
        _, p1_intensities = p1.get_pattern_data()
        _, p2_intensities = p2.get_pattern_data()
        return np.dot(p1_intensities, p2_intensities)

    for i in range(n):
        for j in range(i + 1, n):
            dot_prod = compute_dot_prod(patterns[i], patterns[j])
            norm_p1_sq = compute_dot_prod(patterns[i], patterns[i])
            norm_p2_sq = compute_dot_prod(patterns[j], patterns[j])

            normed_dot_prod = dot_prod / np.sqrt(norm_p1_sq * norm_p2_sq)
            normalized_dot_products.append(normed_dot_prod)
    return sum(normalized_dot_products) / len(normalized_dot_products)


def multiplot(patterns : list[XrdPattern]):
    labels = [p.get_name() for p in patterns]
    fig, axes = plt.subplots(4, 8, figsize=(20, 10))
    for i, pattern in enumerate(patterns):
        ax = axes[i // 8, i % 8]
        x_values, intensities = pattern.get_pattern_data(apply_standardization=False)
        ax.set_xlabel(r'$2\theta$ (Degrees)')
        ax.plot(x_values, intensities, label='Interpolated Intensity')
        ax.set_ylabel('Intensity')
        ax.set_title(f'({i}){labels[i][:20]}')
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def attribute_histograms(patterns : list[XrdPattern], attrs : list[str], print_counts : bool = False, save_fpath : Optional[str] = None):
    fig, axs = plt.subplots(nrows=(len(attrs) + 1) // 2, ncols=2, figsize=(15, 5 * ((len(attrs) + 1) // 2)))
    axs = axs.flatten()

    def attempt_round(val):
        try:
            return round(val, 2) if isinstance(val, float) else val
        except TypeError:
            return val

    for i, attr in enumerate(attrs):
        keys, counts = get_count_map(patterns=patterns, attr=attr, print_counts=print_counts)
        rounded_keys = [str(attempt_round(key)) for key in keys]
        axs[i].bar(rounded_keys, counts)
        axs[i].set_title(f'Count distribution of {attr}')
        axs[i].set_xlabel(attr)
        axs[i].set_ylabel('Counts')
        axs[i].tick_params(labelrotation=90)

    if len(attrs) % 2 != 0:
        axs[-1].axis('off')
    plt.tight_layout()

    if save_fpath:
        plt.savefig(save_fpath)
    plt.show()


def get_count_map(patterns : list[XrdPattern], attr : str, print_counts : bool) -> (list[str], list[int]):
    def nested_getattr(obj: object, attr_string):
        attr_names = attr_string.split('.')
        for name in attr_names:
            obj = getattr(obj, name)
        return obj

    values = []
    for pattern in patterns:
        try:
            v = nested_getattr(pattern, attr)
            values.append(v)
        except Exception as e:
            print(f'Could not extract attribute "{attr}" from pattern {pattern.get_name()}\n- Reason: {e}')
    if not values:
        raise ValueError(f'No data found for attribute {attr}')

    count_map = Counter(values)
    sorted_counts = sorted(count_map.items(), key=lambda x: x[1], reverse=True)
    keys, counts = zip(*sorted_counts)
    keys, counts = keys[:30], counts[:30]

    if print_counts:
        print(f'-> Count distribution of {attr} in Dataset:')
        for key, value in sorted_counts:
            print(f'- {key} : {value}')

    return keys, counts


def show_label_fractions(dbs: list[PatternDB]):
    db_groups = {}
    for db in dbs:
        three_letter_name = db.name[:4]
        if not three_letter_name in db_groups:
            db_groups[three_letter_name] = [db]
        else:
            db_groups[three_letter_name].append(db)

    merged_dbs = []
    for name, g in db_groups.items():
        merged = PatternDB.merge(dbs=g)
        merged.name = name
        merged_dbs.append(merged)

    table_data = []
    for d in merged_dbs:
        label_counts = {l: 0 for l in LabelType}
        patterns = d.patterns
        for l in LabelType:
            for p in patterns:
                if p.has_label(label_type=l):
                    label_counts[l] += 1
        db_percentages = [label_counts[l] / len(patterns) for l in LabelType]
        table_data.append(db_percentages)

    col_headers = [label.name for label in LabelType]
    row_headers = [db.name for db in merged_dbs]

    table = tabulate(table_data, headers=col_headers, showindex=row_headers, tablefmt='psql')
    print(table)

