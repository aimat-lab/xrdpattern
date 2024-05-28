import os
import shutil
from xrdpattern.pattern import XrdPattern
import matplotlib.pyplot as plt

def multiplot(patterns_to_ploat, labels):
    fig, axes = plt.subplots(4, 8, figsize=(20, 10))
    for i, pattern in enumerate(patterns_to_ploat):
        ax = axes[i // 8, i % 8]
        intensity_map = pattern.get_pattern_data(apply_standardization=False)
        x_values, intensities = intensity_map.as_list_pair()
        ax.set_xlabel(r'$2\theta$ (Degrees)')
        ax.plot(x_values, intensities, label='Interpolated Intensity')
        ax.set_ylabel('Intensity')
        ax.set_title(f'({i}){labels[i][:20]}')
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def get_patterns_and_fpaths(root_dir : str):
    pattern_fpath_list = [os.path.join(pattern_root_dir, name) for name in os.listdir(root_dir)]
    pattern_fpath_list = sorted(pattern_fpath_list)

    dir_patterns = []
    dir_fpaths = []
    num_errors, num_successful = 0, 0
    for pattern_fpath in pattern_fpath_list:
        try:
            this_pattern = XrdPattern.load(fpath=pattern_fpath)
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
    pattern_root_dir = '/home/daniel/Drive/Downloads/core'
    output_dir = '/home/daniel/Drive/Downloads/cleaned'
    patterns, fpaths = get_patterns_and_fpaths(root_dir=pattern_root_dir)
    batch_size = 32

    j = 0
    os.makedirs(output_dir, exist_ok=True)
    while j < len(patterns):
        pattern_batch = patterns[j:j + batch_size]
        fpath_batch = fpaths[j:j + batch_size]
        names = [os.path.basename(fpath) for fpath in fpath_batch]
        print(f'Len of fpath, labels = {len(fpaths)}, {len(names)}')
        multiplot(patterns_to_ploat=pattern_batch, labels=names)

        excluded_patterns_str = input(f'Enter patterns to be excluded')
        try:
            nums = excluded_patterns_str.split(',')
            print(f'Nums = {nums}')
            nums = [int(s) for s in nums]
            selected_fpaths = [fpath for i, fpath in enumerate(fpath_batch) if i not in nums]
            for p in selected_fpaths:
                shutil.copy(p, os.path.join(output_dir, os.path.basename(p)))
            j += batch_size
        except Exception as e:
            print(f'Selection failed due to error: {e}. Please retry')
