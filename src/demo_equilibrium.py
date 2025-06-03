import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

emissivity_file = 'input/reflectivity/M1_f.csv'

try:
    data = pd.read_csv(emissivity_file)
except FileNotFoundError:
    print(f"File {emissivity_file} not found.")

plt.plot(data['x'], data['y'], label='Emissivity', color='blue')
plt.show()