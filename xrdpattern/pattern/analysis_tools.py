from typing import Optional

import numpy as np
from matplotlib import pyplot as plt
from tabulate import tabulate
from collections import Counter

from xrdpattern.pattern import XrdPattern
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


def get_counts(patterns : list[XrdPattern], attr : str, sort_by_keys : bool = False):
    values = get_valid_values(patterns, attr)
    count_map = Counter(values)
    if sort_by_keys:
        sorted_counts = sorted(count_map.items(), key=lambda x: x[0])
    else:
        sorted_counts = sorted(count_map.items(), key=lambda x: x[1], reverse=True)
    keys, counts = zip(*sorted_counts)

    return keys, counts


def get_valid_values(patterns : list[XrdPattern], attr : str) -> (list[str], list[int]):
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
    values = [v for v in values if not v is None]

    return values


def show_label_fractions(dbs):
    table_data = []
    for d in dbs:
        label_counts = {l: 0 for l in LabelType}
        patterns = d.patterns
        for l in LabelType:
            for p in patterns:
                if p.has_label(label_type=l):
                    label_counts[l] += 1
        db_percentages = [label_counts[l] / len(patterns) for l in LabelType]
        table_data.append(db_percentages)

    col_headers = [label.name for label in LabelType]
    row_headers = [db.name for db in dbs]

    table = tabulate(table_data, headers=col_headers, showindex=row_headers, tablefmt='psql')
    print(table)