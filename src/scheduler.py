import subprocess
import toml
import os
import shutil

import csv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

p1_range = np.linspace(0.0, 1.0, 10) # percent of the lower frequency laser 
p2_range = np.linspace(0.0, 1.0, 10) # reflectivity

configurations = [[{} for _ in p2_range] for _ in p1_range]
results_matrix = np.zeros((len(p1_range), len(p2_range)))

mode = "delay.csv"
output = "results/"

# Define the list of configurations
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
      "tf":2.5, 
      "alphart":float(p2),
      "mode":mode,
      "output":output
      }

rust_program = "./target/debug/photopropulsion"

for (i, p1) in enumerate(p1_range):
  for (j, p2) in enumerate(p2_range):
    with open("input/config.toml", "w") as config_file:
        toml.dump(configurations[i][j], config_file)

    result = subprocess.run([rust_program], capture_output=True, text=True)
    output = result.stdout.strip()  # Strip leading/trailing whitespace
    lines = output.splitlines()  # Split into lines
    last_line = lines[-1].strip()
    try:
      # Convert the last line to a float
      result_float = float(last_line)
      print(result_float)
      results_matrix[i, j] = result_float
      
    except ValueError as e:
      print(f"Failed to convert the last line to float: {e}")
      
df = pd.DataFrame(results_matrix, index=p1_range, columns=p2_range)
plt.figure(figsize=(3, 2.5))
sns.heatmap(df, annot=True, cmap='viridis', fmt=".2f", cbar=True, square=True)
plt.xlabel('Reflectivity (p2)')
plt.ylabel('Laser Percent (p1)')
plt.show()