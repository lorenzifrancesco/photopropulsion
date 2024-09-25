import numpy as np
import matplotlib.pyplot as plt
import matplotlib 
from scipy.constants import lambda2nu, e, h

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
    return x_labels, y1_values, y2_values

# Function to plot the data
def plot_data(x_labels, y1_values, y2_values):
    omega_0 = lambda2nu(1064e-9)
    plt.figure(figsize=(4, 3))
    plt.plot(lambda2nu(x_labels)/omega_0, y1_values, color='b')
    plt.axvline(x=0.8, color='r', linestyle='--', linewidth=2)
    plt.axvline(x=1.2, color='r', linestyle='--', linewidth=2)
    # plt.plot(x, y2_values, label='Series 2', color='r')

    # plt.xticks(x, x_labels)  # Set x-axis labels
    plt.xlabel(r'$\omega/\omega_0$')
    plt.ylabel(r'$\alpha_1$')
    plt.xlim((x_labels[0]/omega_0, 1.5))
    plt.grid(False)
    plt.tight_layout()
    plt.savefig("media/bragg.pdf")

# Main execution
file_path = 'input/Si_Vacuum_SiO2.txt'  # Update this path
x_labels, y1_values, y2_values = read_data(file_path)
plot_data(x_labels, y1_values, y2_values)
