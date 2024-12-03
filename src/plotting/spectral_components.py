import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.cm import get_cmap
from matplotlib.ticker import ScalarFormatter
import toml
import pandas as pd
import subprocess
import seaborn as sns

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
  
def read_speed_from_csv(file_path):
    df = pd.read_csv(file_path)

    # Extract data from the DataFrame
    times =  np.array(df['Time'])
    speeds = np.array(df['Q'])
    total_powers = np.array(df['P'])
    return times, speeds, total_powers
  
def plot_spectral_components(spectrum_path='results/spectrum.csv',
                             speed_path='results/delay.csv'):
    frequencies, powers = read_spectral_components_from_csv(spectrum_path)
    times, speeds, total_powers = read_speed_from_csv(speed_path)
    speeds = speeds[2:]
    times = times[2:]
    total_powers = total_powers[2:]
    sqrt_d = np.sqrt((1-speeds)/(1+speeds))
    print(frequencies.shape, sqrt_d.shape)
    powers = np.where(powers == 0, np.nan, powers)
    frequencies = np.where(frequencies == 0, np.nan, frequencies)
    time_steps = np.arange(powers.shape[0])

    config_path = 'input/config.toml'
    config = toml.load(config_path)
    tf = config['tf']
    
    lw=1.5
    norm = mcolors.Normalize(vmin=np.min(frequencies), vmax=np.max(frequencies))
    tot_frequencies = frequencies.shape[1]
    plt.figure(figsize=(3, 2.5))
    viridis = get_cmap('viridis', tot_frequencies)
    max_power = np.max(powers)
    for j in range(tot_frequencies):
      plt.plot(time_steps/len(time_steps)*tf, frequencies[:, j] * sqrt_d, lw=lw)
    
    # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    # sm.set_array([])
    # plt.colorbar(sm, label='Frequency')
    plt.gca().ticklabel_format(style='sci', axis='both', scilimits=(3, 0))
    plt.xlabel(r'$t/t_\mathrm{rel}$')
    plt.ylabel(r'$\omega_i^\prime/\omega_0$')
    # plt.legend(loc='best')
    # plt.grid(True)
    plt.tight_layout()
    plt.savefig("media/spectrum_lines.pdf")
    
    # plt.figure(figsize=(3, 2.5))
    # powers = np.where(powers == np.nan, 0.0, powers)
    # for i in range(tot_frequencies)[::-1]:
    #     # color = cmap(norm(frequencies[0, i]))
    #     plt.plot(time_steps/len(time_steps)*tf, powers[:, i]*sqrt_d, label=fr'$i = {tot_frequencies - i - 1}$', lw=lw)
    
    # # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    # # sm.set_array([])
    # # plt.colorbar(sm, label='Frequency')
    # # plt.gca().xaxis.set_major_formatter(ScalarFormatter(useMathText=True)) 
    # plt.gca().ticklabel_format(style='sci', axis='both', scilimits=(3 , 0))
    # plt.xlabel(r'$t/t_\mathrm{rel}$')
    # plt.ylabel(r'$\tilde{P_i}/P_0$')
    # # plt.legend(loc='best')
    # # plt.grid(True)
    # plt.tight_layout()
    # plt.savefig("media/spectrum_powers.pdf")

    
    
          
    # # Example data (Replace with your actual data)
    # time = np.linspace(0, 1, 500)
    # amplitude = np.sin(2 * np.pi * 10 * time)

    # # Create a third variable for the z-axis effect (e.g., intensity over time)
    # z = np.linspace(0, 1, 500)  # This could be some measure of depth, intensity, etc.

    # # Create a colormap for the z-axis effect
    # cmap = plt.get_cmap('plasma')

    # # Normalize z for color mapping
    # norm = plt.Normalize(z.min(), z.max())

    # # Plot line with color mapping simulating the z-axis
    # plt.figure(figsize=(8, 6))
    # for i in range(len(time)-1):
    #     plt.plot(time[i:i+2], amplitude[i:i+2], color=cmap(norm(z[i])), lw=2)

    # # Customize the plot to look oscilloscope-like
    # plt.title("Oscilloscope-like Line Plot with Simulated Z-Axis", fontsize=16)
    # plt.xlabel("Time (s)", fontsize=14)
    # plt.ylabel("Amplitude", fontsize=14)

    # # Add a colorbar to show the z-axis values
    # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    # sm.set_array([])
    # cbar = plt.colorbar(sm)
    # cbar.set_label('Z-axis (Intensity)', fontsize=12)

    # # # Display the plot
    # # plt.tight_layout()
    # # plt.show()
    # plt.figure(figsize=(3, 2.5))
    # final_frequencies = powers[-1, :]
    # skip = 1
    # powers = np.where(powers is np.nan, 0.0, powers)
    # for i in range(1):
    #     # color = cmap(norm(frequencies[0, i]))
    #     plt.scatter(frequencies[-1,:], powers[-1, :], marker="x", s=10.5, lw=0.5,  color=viridis(1))
    
    # # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    # # sm.set_array([])
    # # plt.colorbar(sm, label='Frequency')
    # # plt.gca().xaxis.set_major_formatter(ScalarFormatter(useMathText=True)) 
    # # plt.gca().ticklabel_format(style='sci', axis='both', scilimits=(3 , 0))
    # # plt.xlabel(r'$\omega_i/\omega_0$')
    # # plt.ylabel(r'$\tilde{P_i}/P_0$')
    # # # plt.legend(loc='best')
    # # # plt.grid(True)
    # # plt.tight_layout()
    # # plt.savefig("media/power_vs_freq.pdf")
    # # plt.clf()
    # plt.plot(times, sqrt_d)
    # plt.xlabel(r"$t/t_{\mathrm{rel}}$")
    # plt.ylabel(r"$\sqrt{D(t)}$")
    # plt.savefig("media/geo_dynamics/doppler.pdf")
    # plt.clf()
    # # plt.plot(times, speeds)
    # # plt.xlabel(r"$t/t_{\mathrm{rel}}$")
    # # plt.ylabel(r"$\dot{q}(t)/c$")
    # # plt.savefig("media/geo_dynamics/speeds.pdf")
    # # plt.clf()
    # # plt.plot(times, total_powers)
    # # plt.xlabel(r"$t/t_{\mathrm{rel}}$")
    # # plt.ylabel(r"$P(t)$")
    # # plt.savefig("media/geo_dynamics/total_powers.pdf")

rust_compile = 'cargo build --release'
result = subprocess.run(rust_compile, shell=True, capture_output=True, text=True)
rust_program = "./target/release/photopropulsion"
result = subprocess.run([rust_program], capture_output=True, text=True)
file_path = 'results/spectrum.csv'
plot_spectral_components(file_path)