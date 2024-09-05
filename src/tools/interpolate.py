import csv
import matplotlib.pyplot as plt
from scipy.constants import lambda2nu, c
import toml
import numpy as np

def save_coefficients_to_csv(coefficients, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['x', 'y'])  
        writer.writerows(coefficients)

def load_points_from_csv(dir, name):
    points = []
    filename = dir+name+".csv"
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            x = float(row[0])
            y = float(row[1])
            points.append((x, y))
    for i in range(len(points)):
      points[i] = (lambda2nu(points[i][0]*1e-6), points[i][1])
    return points
  
def rescale_points(points, t_rel):
  for i in range(len(points)):
    points[i] = (t_rel * points[i][0], points[i][1])
  return points

def plot_points(dir, name, label):
    plt.figure(figsize=(4, 3))
    plt.plot([p[0]*1e-12 for p in points], [p[1] for p in points], label=label)
    plt.legend()
    plt.xlabel(r"$f$ [THz]")
    plt.ylabel(r"$\alpha$")
    plt.tight_layout()
    # plt.show()
    plt.savefig("media/reflectivity/"+name+".pdf")

if __name__ == "__main__":
    dir = "input/reflectivity/"
    names = ["braggSiN", "braggBN", "gmrSiN", "gmrBN"]
    labels = [r"Bragg SiN", r"Bragg BN", r"GMR SiN", r"GMR BN"] 
    names = ["braggSiN", "gmrSiN"]
    labels = [r"Bragg", r"GMR"]
    config = toml.load('input/si_units.toml')
    P = config['P']
    m = config['m']
    t_rel = m*c**2/P
    f_0 = lambda2nu(1064e-9)
    f_0 = 283.2e12
    cnt = 0
    plt.figure(figsize=(3, 2.5))
    for i, n in enumerate(names):
      points = load_points_from_csv(dir, n)
      # plot_points(points, n, labels[i])
      print(names[i])
      points = rescale_points(points, 1/f_0)
      save_coefficients_to_csv(points, "input/reflectivity/"+ n +"_f.csv")
      cnt += 1
      print([p[0] for p in points])
      plt.plot(np.array([p[0] for p in points]), [p[1] for p in points], label=labels[i])

    plt.xlabel(r"$\omega/\omega_0$")
    plt.ylabel(r"$\alpha_1(\omega)$")
    plt.legend()
    plt.tight_layout()
    plt.savefig("media/reflectivity/spectral_comparison.pdf")