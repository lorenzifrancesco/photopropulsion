import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Function to read the CSV file and plot a heatmap
def plot_heatmap_from_csv(csv_file_path, output_image_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Check the structure of the DataFrame
    print("DataFrame head:")
    print(df.head())

    # Plot the heatmap
    plt.figure(figsize=(5, 4))
    sns.heatmap(df, cmap='viridis', annot=False, cbar=True)

    # Add labels and title
    plt.xlabel(r'Frequency Index')
    plt.ylabel(r'Time Index')

    # Save the heatmap to a file
    plt.savefig(output_image_path)

# Example usage
if __name__ == "__main__":
    # Specify the path to your CSV file and the output path for the heatmap image
    csv_file_path = 'results/spectrum.csv'  # Replace with your CSV file path
    output_image_path = 'media/spectrum.png'     # Desired output path for the heatmap image

    # Generate the heatmap
    plot_heatmap_from_csv(csv_file_path, output_image_path)
