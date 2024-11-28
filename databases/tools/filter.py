import os
import shutil

from xrdpattern.parsing import Formats
from xrdpattern.pattern import XrdPattern, PatternDB
import matplotlib.pyplot as plt

def multiplot(patterns_to_ploat, labels):
    fig, axes = plt.subplots(4, 8, figsize=(20, 10))
    for i, pattern in enumerate(patterns_to_ploat):
        ax = axes[i // 8, i % 8]
        x_values, intensities = pattern.get_pattern_data(apply_standardization=False)
        ax.set_xlabel(r'$2\theta$ (Degrees)')
        ax.plot(x_values, intensities, label='Interpolated Intensity')
        ax.set_ylabel('Intensity')
        ax.set_title(f'({i}){labels[i][:20]}')
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def get_patterns_and_fpaths(root_dirpath : str, max_patterns : int = 10000):
    pattern_fpath_list = PatternDB.get_xrd_fpaths(dirpath=root_dirpath, select_suffixes=Formats.get_all_suffixes())
    pattern_fpath_list = pattern_fpath_list[:max_patterns]

    dir_patterns = []
    dir_fpaths = []
    num_errors, num_successful = 0, 0
    for pattern_fpath in pattern_fpath_list:
        try:
            this_pattern = XrdPattern.load(fpath=pattern_fpath, mute=True)
            dir_fpaths.append(pattern_fpath)
            dir_patterns.append(this_pattern)
            print(f'{num_successful}/{len(pattern_fpath_list)} Pattern parsed successfully')
            num_successful += 1
        except:
            print(f'Error loading pattern at {pattern_fpath}')
            num_errors += 1
    print(f'Finished parsing with {num_errors} errors')

    return dir_patterns, dir_fpaths


if __name__ == "__main__":
    pattern_root_dir = '/home/daniel/aimat/opXRD/raw/hodge_alwen_1'
    output_dir = '/home/daniel/Drive/Downloads/cleaned'
    patterns, fpaths = get_patterns_and_fpaths(root_dirpath=pattern_root_dir)
    batch_size = 32

    j = 0
    os.makedirs(output_dir, exist_ok=True)
    while j < len(patterns):
        pattern_batch = patterns[j:j + batch_size]
        fpath_batch = fpaths[j:j + batch_size]
        names = [os.path.basename(fpath) for fpath in fpath_batch]
        print(f'Len of fpath, labels = {len(fpaths)}, {len(names)}')
        multiplot(patterns_to_ploat=pattern_batch, labels=names)

        prompt = input(f'Press enter to continue')
        j += batch_size
