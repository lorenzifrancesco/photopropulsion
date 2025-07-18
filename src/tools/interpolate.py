import csv
import matplotlib.pyplot as plt
from scipy.constants import lambda2nu, c
import toml
import numpy as np
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if event.is_directory:
            return 
        print(f"File {event.src_path} has been modified.")
        self.callback(event.src_path)
        
def save_coefficients_to_csv(coefficients, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['x', 'y'])
        writer.writerows(coefficients)


def find_file(filename, search_dir):
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.startswith(filename):
                return os.path.join(root, file)
    return None


def determine_file_type(dir, filename):
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.startswith(filename):  # Match filename regardless of extension
                file_path = os.path.join(root, file)
    if file_path.endswith(".csv"):
        return "csv"
    elif file_path.endswith(".txt"):
        return "txt"


def load_points(dir, name, mode="auto"):
  if mode =="auto":
    mode = determine_file_type(dir, name)
  if mode=="txt":
    return load_points_from_txt(dir, name)
  elif mode=="csv":
    return load_points_from_csv(dir, name)

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


def load_points_from_txt(dir, name):
    points = []
    with open(dir+name+".txt", 'r') as file:
        for line in file:
            if not line.startswith(";"):  # Skip lines that start with ";"
                parts = line.split()
                # First column for x-axis
                points.append(
                    (lambda2nu(float(parts[0].strip()) * 1e-6), float(parts[1].strip())))
    return points


def rescale_points(points, t_rel):
    for i in range(len(points)):
        points[i] = (t_rel * points[i][0], points[i][1])
    return points

# TODO check
def rescale_wavelengths_to_f0(points, xx):
    for i in range(len(points)):
        points[i] = (xx / points[i][0], points[i][1])
    return points


def execute_code(file_path):
    print(f"Executing code for {file_path}...")
    try:
      dir = '/home/lorenzi/sw/xop2.3/'
    #   names = ["DE", "M1", "M2", "M3"]
      names = ["slab_e1"]
      labels = [r"$\mathrm{M}_{\mathrm{DE}}$", r"$\mathrm{M}_{\mathrm{1}}$", r"$\mathrm{M}_{\mathrm{2}}$", r"$\mathrm{M}_{\mathrm{3}}$"]
      ls = ["-", ":", "--", "-."]
      colors = ["gray", "g", "b", "m"]
      config = toml.load('input/si_units.toml')
      P = config['P']
      m = config['m']
      t_rel = m*c**2/P
      f_0 = lambda2nu(1064e-9)
      # f_0 = 283.2e12
      cnt = 0
      plt.figure(figsize=(3, 2.6))
      for i, n in enumerate(names):
          points = load_points(dir, n, mode="txt")
          # print(names[i])
          # print(points)
          points = rescale_points(points, c/(f_0))
          if n == "DE":
            # need to multiply by the mirror to total 
            # surface ratio
            m2s = 0.9
            for j, p in enumerate(points):
              points[j] = (p[0], p[1]*m2s)
          print(points)
          save_coefficients_to_csv(points, "input/reflectivity/freq/" + n + "_f.csv")
          cnt += 1
          # print([p[0] for p in points])
          xaxis = np.array([p[0] for p in points])
          if i>0: # exclude the DE
            plt.plot(xaxis, 
                    [p[1] for p in points],
                    label=labels[i],
                    ls=ls[i], 
                    lw =1.1, 
                    color=colors[i])
          else:
            yvals = [p[1] for p in points]
            plt.plot(xaxis, 
                    np.where(xaxis<1.12, yvals , np.nan),
                    label=labels[i],
                    ls=ls[i], 
                    lw =1.1, 
                    color=colors[i])
            
      max_alpha1 = np.max([i[1] for i in points])
      flat_coefficients = [(i[0], 1.0) for i in points]
      save_coefficients_to_csv(flat_coefficients, "input/reflectivity/freq/FLAT_f.csv")
      plt.axvspan(xmin=1.06, xmax=0.542, ymin=0,
                    ymax=1, color='orange', alpha=0.2)
      plt.xlabel(r"$\omega/\omega_0$")
      plt.xlim(0.1, 1.4)
      plt.ylabel(r"$\alpha(\omega)$")
      plt.legend()
      plt.tight_layout()
      plt.savefig("media/reflectivity/spectral_comparison.pdf")
    except Exception as e: 
      print("Error happened in executing the update!")
      print(e)
      raise e
    
if __name__ == "__main__":
    execute_code('/home/lorenzi/sw/xop2.3/')
    exit()
    event_handler = FileChangeHandler(execute_code)
    observer = Observer()
    observer.schedule(event_handler, path='/home/lorenzi/sw/xop2.3/', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()