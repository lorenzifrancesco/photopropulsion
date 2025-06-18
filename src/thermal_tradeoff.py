import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import toml
import subprocess
import simulation
import matplotlib.cm as cm
cmap = cm.get_cmap('Set1')

compute = 0
plotting = ["p_compare", "qdot_compare"]
figsize = (2.5, 2.3)

output = "results/"
l = simulation.Launch()
l.multilayer = simulation.Reflector.FLAT
l.alpha2 = 1.0
l.mode = "delay"
l.p_0 = 50e9
l.t_f = 500
l.d_sail = 100

# 3e6 for short, 3e9 for long. Medium: 1e9
l.q_0 = 3e6  # Change to 3e9 for long, 1e9 for medium

