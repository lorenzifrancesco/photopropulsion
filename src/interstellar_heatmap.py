import subprocess
import toml
import os, sys
import shutil

import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import pandas as pd
from scipy.constants import c
import simulation
from simulation import Reflector
from tqdm import tqdm
from matplotlib.colors import LinearSegmentedColormap

def lighten_colormap(cmap, factor=0.5, N=256):
    colors = cmap(np.linspace(0, 1, N))
    white = np.array([1, 1, 1, 1])
    colors = (1 - factor) * colors + factor * white
    return LinearSegmentedColormap.from_list(f"{cmap.name}_light", colors, N)


def plot_interstellar_heatmap(override = False,
                      ratio = True,
                      special = ""):
  if ratio: 
    assert not override 
     
  if ratio:
    ylabel = r'$\Delta v / \Delta v_S$'
  else:
    ylabel = r'$\Delta v/ c$'
  mode_range = [("delay", Reflector.FLAT),
                ("delay", Reflector.M1),
                ("delay", Reflector.M2),
                ("delay", Reflector.M3),
                ("lubin", Reflector.FLAT),
                ]
  panels_pow = [r'(a)', r'(c)']
  panels_eta = [r'(b)', r'(d)']
  panel_pow = panels_pow[0]
  panel_eta = panels_eta[0]
  if ratio:
    label_list = label_list[:-1]
    mode_range = mode_range[:-1]
    color_list = ['r', 
                'g', 
                'b', 
                'm', 
                'orange']
    panel_pow = panels_pow[1]
    panel_eta = panels_eta[1]
    ylims = [0.0, 9.3]
  else:
    ylims = [0, 0.35]
  # n_simulations = len(label_list)
  file = "auto.csv"
  output = "results/"

  ## ETA section ========================
  eta_range = np.linspace(0, 2, 50, dtype=np.float64)
  power_range = np.linspace(10, 100, 25, dtype=np.float64) * 1e9
  l = simulation.Launch()
  l.p_0 = 50.0e9
  l.alpha1 = 0.0
  ## Compute section
  if not os.path.exists("results/v_eta.npy") or override:
      print("Computing...")
      results_matrix = np.zeros(
          (len(power_range), len(eta_range), len(mode_range)), dtype=np.float64)
      for (k, powr) in enumerate(power_range): 
        for (i, eta) in enumerate(eta_range):
            for (j, mode) in enumerate(mode_range):
                l.eta = eta
                l.p_0 = powr
                l.mode = mode[0]
                l.multilayer = mode[1]
                print(f"eta={l.eta:.1e}, mode={str(mode[1]):15}", end="")
                print(f" | tf={l.get_tf():.3e}, ht = 1e-06")
                sys.stdout = open(os.devnull, 'w')
                l.write_config('input/_config.toml')
                results_matrix[k, i, j] = l.run()
                sys.stdout = sys.__stdout__
      print(np.shape(results_matrix))
      np.save("results/v_heatmap.npy", results_matrix)

  results_matrix = np.load("results/v_heatmap.npy")
  
  print("Plotting heatmaps...")
  for j, mode in enumerate(mode_range):
      plt.figure(figsize=(3.5, 3))
      
      if ratio:
          results_matrix[:, :, j] /= results_matrix[:, -1, j]
      
      X, Y = np.meshgrid(power_range, eta_range)
      Z = results_matrix[:, :, j].T  # Transpose for correct orientation
      
      viridis = plt.cm.viridis
      viridis_light = lighten_colormap(viridis, factor=0.35) 
      
      contour = plt.contourf(X, Y, Z, levels=200, cmap=viridis_light)
      contour_lines = plt.contour(X, Y, Z, levels=10, colors='black', linewidths=0.5)
      plt.clabel(contour_lines, inline=True, fontsize=12)
      
      plt.colorbar(contour, label=ylabel)
      plt.ylabel(r'$\eta$')
      plt.xlabel(r'$P_0 \; [GW]$')
      plt.title(f'Mode: {mode[1]}')
      
      name = f"media/v_heatmap_{mode[1]}{special}.png"
      plt.tight_layout()
      plt.savefig(name, dpi=300)
      plt.close()
      print("Heatmap saved as ", name)

    
if __name__ == "__main__":
  for i in range(2):
    if i == 0:
      special = "_rr"
      ratio = True
    else:
      special = ""
      ratio = False
    #
  plot_interstellar_heatmap(
              override = False,
              ratio = False, 
              special = special)
    
  # make this out of the for loop for overriding the values in the files
  # plot_interstellar(todo = ["eta", "pow"],
  #                   override = True,
  #                   ratio = False, 
  #                   special = "")