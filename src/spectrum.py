import pandas as pd
import matplotlib.pyplot as plt

def plot_spectrum_from_csv(csv_file):
    df = pd.read_csv(csv_file)
    
    print(df.head())
    if 'F' not in df.columns or 'P' not in df.columns:
        raise ValueError("CSV file must contain 'F' and 'P' columns")
    
    x = df['F']
    y = df['P']
    
    # Plot the data
    plt.figure(figsize=(4, 3))
    plt.scatter(x, y[::-1], linestyle='-', color='b', marker="+")
    plt.xlabel(r'$F$')
    plt.ylabel(r'$P(t_f)$')
    plt.tight_layout()
    plt.savefig("media/spectrum.pdf")

if __name__ == "__main__":
    csv_file = 'results/spectrum.csv'  # Change this to the path of your CSV file
    plot_spectrum_from_csv(csv_file)
