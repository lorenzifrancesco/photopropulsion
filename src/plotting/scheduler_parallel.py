import subprocess
import toml
import os
import shutil

import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import pandas as pd

from concurrent.futures import ProcessPoolExecutor, as_completed

p1_range = np.linspace(0.001, 1.0, 4)  # percent of the lower frequency laser
p2_range = np.linspace(0.0, 1.0, 4)  # reflectivity

configurations = [[{} for _ in p2_range] for _ in p1_range]
results_matrix = np.zeros((len(p1_range), len(p2_range)))

mode = "delay.csv"
output = "results/"

for (i, p1) in enumerate(p1_range):
    for (j, p2) in enumerate(p2_range):
        # print(i)
        # print(j)
        configurations[i][j] = {
            "q": float(p1),
            "q_prime": 0.0,
            "p": 1.0,
            "delta": 0.0,
            "t": 0.0,
            # very high value to allow the termination due to stationary state detection.
            "tf": 100.0,
            "alphart": float(p2),
            "l_diffraction": 0.05,
            "mode": mode,
            "output": output
        }

rust_program = "./target/release/photopropulsion"
print("Running the Rust program in ", rust_program)

def run_simulation(i, j, config):
    config_file_path = f"input/config_{i}_{j}.toml"

    with open(config_file_path, "w") as config_file:
        toml.dump(config, config_file)

    result = subprocess.run(
        [rust_program, config_file_path], capture_output=True, text=True)

    output = result.stdout.strip()
    lines = output.splitlines()
    print(lines[-2])
    last_line = lines[-1].strip()

    try:
        result_float = float(last_line)
        return i, j, result_float
    except ValueError as e:
        print(f"Failed to convert the last line to float: {e}")
        return i, j, None


tasks = [(i, j, configurations[i][j]) for i in range(len(p1_range))
         for j in range(len(p2_range))]

num_workers = max(1, os.cpu_count() - 12)
with ProcessPoolExecutor(max_workers=num_workers) as executor:
    futures = [executor.submit(run_simulation, i, j, config)
               for (i, j, config) in tasks]

    for future in as_completed(futures):
        i, j, result_float = future.result()
        if result_float is not None:
            print(result_float)
            results_matrix[i, j] = result_float

# Plotting
df = pd.DataFrame(results_matrix, index=p1_range, columns=p2_range)
plt.figure(figsize=(3, 2.5))
ax = sns.heatmap(df, annot=False, cmap='viridis',
                 fmt=".2f", cbar=True, square=True)
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
plt.tight_layout()
plt.savefig("media/heatmap.pdf")


P1, P2 = np.meshgrid(p1_range, p2_range)

plt.figure(figsize=(3, 2.5))
contour = plt.contourf(P1, P2, results_matrix, cmap='viridis', levels=20)
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

plt.tight_layout()
plt.savefig("media/contour.pdf")
