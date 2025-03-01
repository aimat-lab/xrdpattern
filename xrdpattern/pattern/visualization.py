from collections import Counter

import matplotlib.colors
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable

from xrdpattern.tools.spg_converter import SpacegroupConverter
from .pattern import XrdPattern



# -----------------------------------------

def multiplot(patterns : list[XrdPattern], start_idx : int):
    labels = [p.get_name() for p in patterns]
    fig, axes = plt.subplots(4, 8, figsize=(20, 10))
    for i, pattern in enumerate(patterns):
        ax = axes[i // 8, i % 8]
        x_values, intensities = pattern.get_pattern_data(apply_standardization=False)
        ax.set_xlabel(r'$2\theta$ (Degrees)')
        ax.plot(x_values, intensities, label='Interpolated Intensity')
        ax.set_ylabel('Intensity')
        ax.set_title(f'({i+start_idx}){labels[i][:20]}')
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def define_spg_ax(patterns: list[XrdPattern], ax: Axes):
    keys, counts = get_counts(patterns=patterns, attr='primary_phase.spacegroup')
    keys, counts = keys[:30], counts[:30]

    spgs = [int(k) for k in keys]
    spg_formulas = [f'${SpacegroupConverter.to_formula(spg, mathmode=True)}$' for spg in spgs]
    ax.bar(spg_formulas, counts)
    ax.tick_params(labelbottom=True, labelleft=True)  # Enable labels
    ax.set_title(f'(a)', loc='left')
    ax.set_ylabel(f'No. patterns')
    ax.set_xticklabels(spg_formulas, rotation=90)


def define_recorded_angles_ax(patterns: list[XrdPattern], ax: Axes):
    values = get_valid_values(patterns=patterns, attr='angular_resolution')
    ax.set_title(f'(b)', loc='left')
    ax.hist(values, bins=10, range=(0, 0.1), edgecolor='black')
    ax.set_xlabel(r'Angular resolution $\Delta(2\theta)$ [$^\circ$]')
    ax.set_yscale('log')
    ax.set_ylabel(f'No. patterns')


def define_angle_start_stop_ax(patterns: list[XrdPattern], density_ax: Axes, top_marginal: Axes, right_marginal: Axes, cmap_ax: Axes, attach_colorbar: bool):
    start_data = get_valid_values(patterns=patterns, attr='startval')
    end_data = get_valid_values(patterns=patterns, attr='endval')
    start_angle_range = (0, 60)
    end_angle_range = (0, 180)

    # noinspection PyTypeChecker
    h = density_ax.hist2d(start_data, end_data, bins=(10, 10), range=[list(start_angle_range), list(end_angle_range)],
                          norm=matplotlib.colors.LogNorm())
    density_ax.set_xlabel(r'Smallest recorded $2\theta$ [$^\circ$]')
    density_ax.set_ylabel(r'Largest recorded $2\theta$ [$^\circ$]')
    density_ax.set_xlim(start_angle_range)
    density_ax.set_ylim(end_angle_range)

    density_ax.xaxis.set_major_locator(MaxNLocator(4))
    xticks = density_ax.get_xticks()
    density_ax.set_xticks(xticks[:-1])



    if attach_colorbar:
        divider = make_axes_locatable(density_ax)
        cax = divider.append_axes('right', size='5%', pad=0.0)
        plt.colorbar(h[3], cax=cax, orientation='vertical')

    else:
        plt.colorbar(h[3], cax=cmap_ax, orientation='vertical', location='left')
        cmap_ax.set_ylabel(f'No. patterns')

    top_marginal.hist(start_data, bins=np.linspace(*start_angle_range, num=10), edgecolor='black')
    top_marginal.set_title(f'(c)', loc='left')
    top_marginal.set_yscale('log')
    top_marginal.tick_params(axis="x", labelbottom=False, which='both', bottom=False)

    if attach_colorbar:
        divider = make_axes_locatable(top_marginal)
        cax = divider.append_axes('right', size='5%', pad=0.0)
        cax.axis('off')

        divider = make_axes_locatable(right_marginal)
        cax = divider.append_axes('left', size='15%', pad=0.0)
        cax.axis('off')

    else:
        divider = make_axes_locatable(cmap_ax)
        cax = divider.append_axes('right', size=0.8, pad=0.0)
        cax.axis('off')

    right_marginal.hist(end_data, bins=np.linspace(*end_angle_range, num=10), orientation='horizontal',edgecolor='black')
    right_marginal.set_xscale('log')
    right_marginal.tick_params(axis="y", labelleft=False, which='both', left=False)


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