import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Function to read the CSV file and plot a heatmap
def plot_heatmap_from_csv(csv_file_path, output_image_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Check the structure of the DataFrame
    print("DataFrame head:")
    print(df.head())
    results_matrix = df.to_numpy()
    p1_range = np.linspace(0, 1, len(results_matrix[0, :])) # frequency
    p2_range = np.linspace(0, 1, len(results_matrix[:, 0])) # time
    P1, P2 = np.meshgrid(p1_range, p2_range)
    
    plt.figure(figsize=(3, 2.5))
    contour = plt.contourf(P1, P2, results_matrix, cmap='viridis', levels=5)
    cbar = plt.colorbar(contour, label=r'$\dot{q}_\infty$')
    plt.xlabel(r'$\alpha$')
    plt.ylabel(r'$q_0$')
    num_xticks = 5  # Number of xticks you want
    xtick_positions = np.linspace(p1_range.min(), p1_range.max(), num_xticks)
    xtick_labels = [fr"${pos:.2f}$" for pos in xtick_positions]
    plt.xticks(xtick_positions, xtick_labels)
    num_yticks = 5  # Number of yticks you want
    ytick_positions = np.linspace(p2_range.min(), p2_range.max(), num_yticks)
    ytick_labels = [fr"${pos:.2f}$" for pos in ytick_positions]
    plt.yticks(ytick_positions, ytick_labels)
    num_cbar_ticks = 5  # Number of colorbar ticks you want
    cbar_ticks = np.linspace(results_matrix.min(),
                            results_matrix.max(), num_cbar_ticks)
    cbar_tick_labels = [rf"${tick:.2f}$" for tick in cbar_ticks]
    cbar.set_ticks(cbar_ticks)
    cbar.set_ticklabels(cbar_tick_labels)
    plt.xlabel(r"$\omega/\omega_0$")
    plt.ylabel(r"$t/t_f$")
    plt.tight_layout()
    plt.savefig(output_image_path)


# Example usage
if __name__ == "__main__":
    csv_file_path = 'results/spectrum.csv'
    output_image_path = 'media/spectrum.pdf'

    plot_heatmap_from_csv(csv_file_path, output_image_path)
