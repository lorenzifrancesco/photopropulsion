import subprocess
import toml
import os
import shutil

import csv
import numpy as np
import matplotlib.pyplot as plt

p1_range = np.linspace(0.0, 1.0, 10) # percent of the lower frequency laser WTF no. Power, for example
p2_range = np.linspace(0.0, 1.0, 10) # reflectivity

results_matrix = np.zeros((len(p1_range), len(p2_range)))

mode = "delay.csv"
output = "results/"

# Define the list of configurations
configurations = []
for i in enumerate(p1_range):
  for j in enumerate(p2_range):
    configurations.append({"q": 0.01, "q_prime": 0.0, "p":p1_range[i], "delta":0.0, "t":0.0, "tf":2.5, "alphart":p2_range[j]})

rust_program = "./target/debug/photopropulsion"

for i, config in enumerate(configurations):
    with open("config.toml", "w") as config_file:
        toml.dump(config, config_file)
    
    result = subprocess.run([rust_program], capture_output=True)
    
    if result.returncode != 0:
        print(f"Error running Rust program with configuration {i}: {result.stderr.decode()}")
        continue
    
    output_file = f"output_{i}.csv"
    shutil.move("output.csv", output_file)
    
    print(f"Configuration {i} processed, output saved to {output_file}")