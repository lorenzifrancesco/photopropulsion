import csv
import matplotlib.pyplot as plt
from scipy.constants import lambda2nu

def compute_quadratic_coefficients(points):
    coefficients = []
    
    for i in range(len(points) - 2):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        x2, y2 = points[i + 2]
        
        a0 = y0
        a1 = (y1 - y0) / (x1 - x0)
        a2 = ((y2 - y0) / (x2 - x0) - (y1 - y0) / (x1 - x0)) / (x2 - x1)
        
        coefficients.append((a0, a1, a2, x0, x1, x2))
    
    return coefficients

def save_coefficients_to_csv(coefficients, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['a0', 'a1', 'a2', 'x0', 'x1', 'x2'])  
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
    plt.figure(figsize=(4, 3))
    plt.plot([lambda2nu(p[0] * 1e-6)*1e-12 for p in points], [p[1] for p in points], label=name)
    plt.legend()
    plt.xlabel(r"$f$ [THz]")
    plt.ylabel(r"$\alpha$")
    plt.tight_layout()
    # plt.show()
    plt.savefig("media/reflectivity/"+name+".pdf")
    return points

if __name__ == "__main__":
    dir = "input/reflectivity/"
    names = ["braggSiN", "braggBN", "gmrSiN", "gmrBN"]
    for n in names:
      points = load_points_from_csv(dir, n)
