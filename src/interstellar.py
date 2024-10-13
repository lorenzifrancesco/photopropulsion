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

mode_range = [("delay", Reflector.FLAT),
              ("delay", Reflector.M1),
              ("delay", Reflector.M2),
              ("delay", Reflector.M3),
              ("lubin", Reflector.FLAT),
              ]
color_list = ['r', 
              'g', 
              'b', 
              'm', 
              'c', 
              'orange']
ls_list = ['-', 
            ':', 
            '--', 
            '-.', 
            '--',
            '--', 
            '-']
label_list = [r'${\mathrm{F}}$',
              r'${\mathrm{M1}}$',
              r'${\mathrm{M2}}$',
              r'${\mathrm{M3}}$',
              r'${\mathrm{S}}$']
n_simulations = len(label_list)
alpha1 = 1.0
file = "auto.csv"
output = "results/"

todo = ["eta", "pow"]

## ETA section ========================
if "eta" in todo:
  override = 0
  eta_range = np.linspace(0, 2, 50, dtype=np.float64)
  l = simulation.Launch()
  l.p_0 = 50.0e9

  ## Compute section
  if not os.path.exists("results/v_eta.npy") or override:
      print("Computing...")
      results_matrix = np.zeros(
          (len(eta_range), len(mode_range)), dtype=np.float64)

      for (i, eta) in tqdm(enumerate(eta_range)):
          for (j, mode) in enumerate(mode_range):
              with open("input/config.toml", "w") as config_file:
                  l.eta = eta
                  l.mode = mode[0]
                  l.multilayer = mode[1]
                  sys.stdout = open(os.devnull, 'w')
                  l.write_config('input/config.toml')
                  results_matrix[i, j] = l.run()
                  sys.stdout = sys.__stdout__
      print(np.shape(results_matrix))
      np.save("results/v_eta.npy", results_matrix)

  results_matrix = np.load("results/v_eta.npy")
  print("Plotting...")

  # single line
  plt.figure(figsize=(3, 2.5))
  np.set_printoptions(precision=10)
  for (j, alpha) in enumerate(mode_range):
      plt.plot(eta_range, results_matrix[:, j],
                color=color_list[j], ls=ls_list[j], lw=1.5, label=label_list[j])

  td_fom = 2 * l.p_0 * alpha1/(3e8 * (l.sail_mass *(1+eta_range))) * l.t_f / c
  td_fom[td_fom > 1] = np.nan
  plt.plot(eta_range, td_fom,
            color=color_list[n_simulations], ls=ls_list[n_simulations], lw=1.5, label=r'${\mathrm{NR}}$')

  plt.xlabel(r'$\eta$')
  plt.ylabel(r'$\Delta v / c$')
  num_xticks = 5
  plt.legend(labelspacing=0.1)
  plt.tight_layout()
  plt.savefig("media/delta_v_p.pdf")
  print("Done eta.")

## POWER section =====================
if "pow" in todo:
  override = 1
  power_range = np.linspace(0, 100, 30, dtype=np.float64) * 1e9
  l = simulation.Launch()
  l.eta = 0.0
  if not os.path.exists("results/v_pow.npy") or override:
      print("Computing...")
      results_matrix = np.zeros(
          (len(power_range), len(mode_range)), dtype=np.float64)

      for (i, power) in tqdm(enumerate(power_range)):
          for (j, mode) in enumerate(mode_range):
              with open("input/config.toml", "w") as config_file:
                  l.p_0 = power
                  l.mode = mode[0]
                  l.multilayer = mode[1]
                  sys.stdout = open(os.devnull, 'w')
                  l.write_config('input/config.toml')
                  results_matrix[i, j] = l.run()
                  sys.stdout = sys.__stdout__
      print(np.shape(results_matrix))
      np.save("results/v_pow.npy", results_matrix)

  results_matrix = np.load("results/v_pow.npy")
  print("Plotting...")
  # single line
  plt.figure(figsize=(3, 2.5))
  np.set_printoptions(precision=10)
  for (j, alpha) in enumerate(mode_range):
      plt.plot(power_range, results_matrix[:, j],
                color=color_list[j], ls=ls_list[j], lw=1.5, label=label_list[j])

  td_fom = 2 * power_range * alpha1 / \
      (c**2 * (l.sail_mass * (1 + l.eta))) * l.t_f
  td_fom[td_fom > 1] = np.nan
  plt.plot(power_range, td_fom,
            color=color_list[n_simulations], ls=ls_list[n_simulations], lw=1.5, label=r'${\mathrm{NR}}$')

  plt.xlabel(r'$P_0$')
  plt.ylabel(r'$\Delta v / c$')
  num_xticks = 5
  xtick_positions = np.linspace(
      power_range.min(), power_range.max(), num_xticks)
  plt.gca().ticklabel_format(style='sci', axis='x', scilimits=(3, 0))
  plt.legend(labelspacing=0.1)
  plt.tight_layout()
  plt.savefig("media/delta_v_pow.pdf")
  print("Done power.")