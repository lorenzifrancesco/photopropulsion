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

p1_range = np.linspace(0.001, 0.2, 3) # percent of the lower frequency laser 
p2_range = np.linspace(0.0, 1.0, 10) # reflectivity
mode = "delay.csv"
output = "results/"

if not os.path.exists("results/terminal_vel.npy") or True:
  print("Computing...")
  configurations = [[{} for _ in p2_range] for _ in p1_range]
  results_matrix = np.zeros((len(p1_range), len(p2_range)))
  for (i, p1) in enumerate(p1_range):
    for (j, p2) in enumerate(p2_range):
      # print(i)
      # print(j)
      configurations[i][j] = {
        "q": float(p1), 
        "q_prime": 0.0, 
        "p":1.0, 
        "delta":0.0, 
        "t":0.0,
        "tf":100.0, # very high value to allow the termination due to stationary state detection.
        "alphart":float(p2),
        "l_diffraction":0.05,
        "mode":mode,
        "output":output
        }

  rust_program = "./target/release/photopropulsion"
  print("Running the Rust program in ", rust_program)

  for (i, p1) in enumerate(p1_range):
    for (j, p2) in enumerate(p2_range):
      with open("input/config.toml", "w") as config_file:
          toml.dump(configurations[i][j], config_file)

      result = subprocess.run([rust_program], capture_output=True, text=True)
      output = result.stdout.strip()
      lines = output.splitlines()
      print(lines[-2])
      last_line = lines[-1].strip()
      try:
        result_float = float(last_line)
        print(i, j, result_float)
        results_matrix[i, j] = result_float
        
      except ValueError as e:
        print(f"Failed to convert the last line to float: {e}")
        
  print(np.shape(results_matrix))
  np.save("results/terminal_vel.npy", results_matrix)
  
print("Plotting...")
results_matrix = np.load("results/terminal_vel.npy")
print(np.shape(results_matrix))

df = pd.DataFrame(results_matrix, index=p1_range, columns=p2_range)
plt.figure(figsize=(3, 2.5))
ax = sns.heatmap(df, annot=False, cmap='viridis', fmt=".2f", cbar=True, square=True)
plt.xlabel(r'$q_0$')
plt.ylabel(r'$\alpha$')
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
print(np.shape(P1))
plt.figure(figsize=(3, 2.5))
contour = plt.contourf(P1, P2, results_matrix, cmap='viridis', levels=20)
cbar = plt.colorbar(contour, label=r'$\dot{q}_\infty$')

# ax = plt.contour(P1, P2, results_matrix, colors='k', levels=10, linestyles='--')

plt.xlabel(r'$q_0$')
plt.ylabel(r'$\alpha$')
# plt.xticks(np.round(p1_range, 2))  # X-axis ticks formatted to 2 decimal places
# plt.yticks(np.round(p2_range, 2))# ax.set_xticklabels([f"{x:.2f}" for x in df.columns], 

num_xticks = 5  # Number of xticks you want
xtick_positions = np.linspace(p1_range.min(), p1_range.max(), num_xticks)
xtick_labels = [fr"${pos:.2f}$" for pos in xtick_positions]
plt.xticks(xtick_positions, xtick_labels)
num_yticks = 5  # Number of yticks you want
ytick_positions = np.linspace(p2_range.min(), p2_range.max(), num_yticks)
ytick_labels = [fr"${pos:.2f}$" for pos in ytick_positions]
plt.yticks(ytick_positions, ytick_labels)
num_cbar_ticks = 5  # Number of colorbar ticks you want
cbar_ticks = np.linspace(results_matrix.min(), results_matrix.max(), num_cbar_ticks)
cbar_tick_labels = [rf"${tick:.2f}$" for tick in cbar_ticks]
cbar.set_ticks(cbar_ticks)
cbar.set_ticklabels(cbar_tick_labels)

plt.tight_layout()
plt.savefig("media/contour.pdf")

color_list = ['r', 'b', 'g', 'm', 'orange']
ls_list = ['-', '--', ':', '-.', '-.']

plt.figure(figsize=(3, 2.5))
for i in range(len(p1_range)): 
  plt.plot(p2_range, results_matrix[i, :], color=color_list[i], ls=ls_list[i], lw=1.5, label=rf"{p1_range[i]:.2f}")
  
cbar = plt.colorbar(contour, label=r'$\dot{q}_\infty$')
plt.xlabel(r'$\alpha$')
plt.ylabel(r'$\dot{q}_\infty$')

num_xticks = 5  # Number of xticks you want
xtick_positions = np.linspace(p2_range.min(), p2_range.max(), num_xticks)
xtick_labels = [fr"${pos:.2f}$" for pos in xtick_positions]
plt.xticks(xtick_positions, xtick_labels)

plt.tight_layout()
plt.savefig("media/terminal_lines.pdf")