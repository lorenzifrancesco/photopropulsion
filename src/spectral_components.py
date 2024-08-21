import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.cm import get_cmap

def read_spectral_components_from_csv(file_path):
    frequencies = []
    powers = []
    
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Read and ignore the header
        
        row_count = 0
        for row in reader:
            # Determine if the row is for frequencies or powers
            if row_count % 2 == 0:  # Frequencies (even index)
                frequencies.append(list(map(float, row)))
            else:  # Powers (odd index)
                powers.append(list(map(float, row)))
            row_count += 1
    return np.array(frequencies), np.array(powers)

def plot_spectral_components(file_path):
    frequencies, powers = read_spectral_components_from_csv(file_path)
    powers = np.where(powers == 0, np.nan, powers)
    frequencies = np.where(frequencies == 0, np.nan, frequencies)
    time_steps = np.arange(powers.shape[0])

    # cmap = get_cmap('rainbow')
    norm = mcolors.Normalize(vmin=np.min(frequencies), vmax=np.max(frequencies))
    
    plt.figure(figsize=(6, 4))
    
    for i in range(frequencies.shape[1]):
        # color = cmap(norm(frequencies[0, i]))
        plt.plot(time_steps/len(time_steps), frequencies[:, i], label=f'Component {i + 1}')
    
    # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    # sm.set_array([])
    # plt.colorbar(sm, label='Frequency')
    
    plt.xlabel(r'$t/t_f$')
    plt.ylabel(r'$\omega/\omega_0$')
    # plt.legend(loc='best')
    # plt.grid(True)
    plt.tight_layout()
    plt.savefig("media/spectrum_lines.pdf")

file_path = 'results/spectrum.csv'
plot_spectral_components(file_path)
