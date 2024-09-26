import numpy as np
import matplotlib.pyplot as plt
import matplotlib 
from scipy.constants import lambda2nu, c, e, h, Boltzmann

def planck(t, wl):
  intensity = (2 * h * lambda2nu(wl)**3) / (c**2) * 1 / (np.exp(h * lambda2nu(wl) / (Boltzmann * t)) - 1)
  return intensity

# Function to read the data from the file
def read_data(file_path):
    x_labels = []
    y1_values = []
    y2_values = []

    with open(file_path, 'r') as file:
        for line in file:
            if not line.startswith(";"):  # Skip lines that start with ";"
                parts = line.split()
                x_labels.append(float(parts[0].strip()))  # First column for x-axis
                y1_values.append(float(parts[1].strip()))  # Second column
                y2_values.append(float(parts[2].strip()))  # Third column
    x_labels =   np.array(x_labels)[::1] * 1e-6
    y1_values = np.array(y1_values)[::1]
    y2_values = np.array(y2_values)[::1]
    print(x_labels.shape, y1_values.shape, y2_values.shape) 
    print("maximum value of the reflectivity", np.max(y1_values))
    return x_labels, y1_values, y2_values

# Function to plot the data
def plot_data(x_labels, y1_values, y2_values, name):
    lambda_0 = 1064e-9
    omega_0 = lambda2nu(lambda_0)
    if name=="absorp":
      lw = 3
      def fuu(x): return x/lambda_0
    else:
      lw = 1
      def fuu(x): return lambda2nu(x)/omega_0
    fig, ax1 = plt.subplots(figsize=(4, 2.5))
    ax1.plot(fuu(x_labels), y1_values, label=r"M$1$", linewidth=1,  color='b')
    ax1.plot(fuu(x_labels), y2_values, label=r'M$2$', linewidth=lw,  color='r')
    # ax1.axvline(x=0.8, linestyle=':', linewidth=1)
    # ax1.axvline(x=1.2, linestyle=':', linewidth=1)
    # plt.xticks(x, x_labels)  # Set x-axis labels
    if name == "absorp":
      ax1.set_ylim((0.0, 0.01))
      plt.xlabel(r"$\lambda/\lambda_0$")
      ax1.set_ylabel(r'$\rho$')
      plt.axvspan(0.8, 1.2, color='gray', alpha=0.5)
      ax2 = ax1.twinx()
      for i in range(3)[::-1]:
        y = planck(100*5*(i+1), x_labels)
        print(y)
        ax2.plot(fuu(x_labels), y, linestyle="--", label=str(100*5*(i+1)))
      ax2.set_ylabel(r'$I(\omega) \, [\mathrm{Wm}^{-2}\mathrm{sr}^{-1}]$')
    else: 
      plt.xlabel(r'$\omega/\omega_0$')
      plt.ylabel(r'$\alpha_1$')
    # plt.xlim((x_labels[0]/omega_0, 1.5))
    plt.grid(False)
    plt.legend()
    plt.tight_layout()
    plt.savefig("media/reflectivity/"+str(name)+".pdf")
    
    if name != "absorp":
      plt.figure(figsize=(2, 1.8))
      plt.plot(fuu(x_labels), y1_values, label=r"M$1$", color='b')
      plt.plot(fuu(x_labels), y2_values, label=r'M$2$', color='r')
      plt.axvline(x=0.8, linestyle='--', linewidth=1)
      plt.axvline(x=1.2, linestyle='--', linewidth=1)
      # plt.xticks(x, x_labels)  # Set x-axis labels
      plt.xlabel(r'$\omega/\omega_0$')
      plt.ylabel(r'$\alpha_1$')
      plt.xlim((0.65, 1.35))
      plt.grid(False)
      plt.legend()
      plt.tight_layout()
      plt.savefig("media/reflectivity/"+str(name)+"_zoom.pdf")

# Main execution
# file_path_mio = 'input/Si_Vacuum_SiO2.txt'
file_path_mio = 'input/Si_Vacuum_ZnTe.txt'
file_path_tung = 'input/Si3N4_Vacuum.txt'
x_labels, y1_values_mio, y2_values_mio = read_data(file_path_mio)
x_labels, y1_values_tung, y2_values_tung = read_data(file_path_tung)
plot_data(x_labels, y1_values_mio, y1_values_tung, name="reflec")
plot_data(x_labels, y2_values_mio, y2_values_tung, name="absorp")