import csv

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

def load_points_from_csv(filename):
    points = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            x = float(row[0])
            y = float(row[1])
            points.append((x, y))
    return points

if __name__ == "__main__":
    # Load points from a CSV file
    points = load_points_from_csv('data.csv')
    
    # Compute coefficients for quadratic interpolation
    coefficients = compute_quadratic_coefficients(points)
    
    # Save coefficients to a CSV file
    save_coefficients_to_csv(coefficients, 'coefficients.csv')

    print("Coefficients have been saved to 'coefficients.csv'.")
