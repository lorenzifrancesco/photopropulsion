import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd

def select_file():
    # Open a file dialog to select a CSV file
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        has_header = messagebox.askyesno("Header", "Does the CSV file have a header?")
        
        df = pd.read_csv(file_path, delimiter=';', decimal=',', header=0 if has_header else None)
        
        text_box.delete('1.0', tk.END)
        text_box.insert(tk.END, df.to_string(index=False))

        convert_button.config(state=tk.NORMAL)
        app.file_path = file_path
        app.df = df
        app.has_header = has_header

def convert_file():
    output_file_path = app.file_path.replace('.csv', '_converted.csv')
    app.df.to_csv(output_file_path, sep=',', decimal='.', index=False, header=app.has_header)
    messagebox.showinfo("Success", f"File converted and saved as {output_file_path}")

app = tk.Tk()
app.title("CSV Converter")

text_box = tk.Text(app, height=20, width=80)
text_box.pack(padx=10, pady=10)

select_button = tk.Button(app, text="Select CSV File", command=select_file)
select_button.pack(pady=5)

convert_button = tk.Button(app, text="Convert and Save", command=convert_file, state=tk.DISABLED)
convert_button.pack(pady=5)
app.mainloop()
