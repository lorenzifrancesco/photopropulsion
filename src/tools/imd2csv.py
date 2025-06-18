#!/usr/bin/env python3
"""
Convert IMD data file from wavelength (nm) to normalized frequency CSV format.
Normalizes frequency to Nd:YAG laser reference frequency (1064 nm).
"""

import sys
import csv
import re

def convert_imd_to_csv(input_file, output_file):
    """
    Convert IMD data file to normalized frequency CSV format.
    
    Args:
        input_file (str): Path to input IMD data file
        output_file (str): Path to output CSV file
    """
    
    # Reference wavelength for Nd:YAG laser (nm)
    ref_wavelength = 1064.0
    
    # Speed of light (for frequency calculations)
    c = 299792458  # m/s
    
    # Calculate reference frequency
    ref_frequency = c / (ref_wavelength * 1e-9)  # Hz
    
    data_started = False
    converted_data = []
    
    try:
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                # if not line or line.startswith(';'):
                    # continue
                
                # Check for the Lambda header line and validate units
                if 'Lambda' in line:
                    # Use regex to find [nm] or other units in brackets
                    unit_match = re.search(r'\[([^\]]+)\]', line)
                    if unit_match:
                        unit = unit_match.group(1).strip()
                        if unit != 'nm':
                            raise ValueError(f"Error: Expected wavelength unit [nm], but found [{unit}]")
                    else:
                        raise ValueError("Error: No wavelength unit found in Lambda header")
                    
                    data_started = True
                    continue
                
                # Process data lines (after Lambda header is found)
                if data_started:
                    # Split by comma or tab (flexible parsing)
                    if ',' in line:
                        parts = [p.strip() for p in line.split(',') if p.strip()]
                    elif '\t' in line:
                        parts = [p.strip() for p in line.split('\t') if p.strip()]
                    else:
                        parts = [p for p in line.split() if p.strip()]
                    # print("ciao")
                    # print(parts)
                    if len(parts) >= 2:
                        try:
                            wavelength = float(parts[0].strip())
                            amplitude = float(parts[1].strip())
                            
                            # Convert wavelength to frequency
                            frequency = c / (wavelength * 1e-9)  # Hz
                            
                            # Normalize to reference frequency
                            normalized_freq = frequency / ref_frequency
                            
                            converted_data.append([normalized_freq, amplitude])
                            
                        except ValueError as e:
                            print(f"Warning: Could not parse line '{line}': {e}")
                            continue
    
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return False
    except Exception as e:
        print(f"Error reading input file: {e}")
        return False
    
    # Write converted data to CSV
    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['x', 'y'])
            # Write data
            writer.writerows(converted_data)
        
        print(f"Successfully converted {len(converted_data)} data points")
        print(f"Output saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False

def main():
    """Main function to handle command line arguments"""
    
    if len(sys.argv) != 3:
        print("Usage: python imd2csv.py <input_file> <output_file>")
        print("Example: python imd2csv.py data.txt output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"Converting '{input_file}' to '{output_file}'...")
    print(f"Reference wavelength: 1064 nm (Nd:YAG laser)")
    
    success = convert_imd_to_csv(input_file, output_file)
    
    if success:
        print("Conversion completed successfully!")
    else:
        print("Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()