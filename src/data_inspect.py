import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                            QWidget, QLabel, QScrollArea, QMessageBox, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)

class DragDropPlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('CSV/TXT Drag & Drop Plotter')
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Create reset button
        self.reset_button = QPushButton('🔄 Reset / Load New File')
        self.reset_button.clicked.connect(self.reset_application)
        self.reset_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color: #007bff;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.reset_button.hide()  # Initially hidden
        
        button_layout.addStretch()
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Create scroll area for plots
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        
        # Create instructions label
        self.instructions = QLabel()
        self.instructions.setText(
            "📊 Drag and drop CSV or TXT files here to plot all columns\n\n"
            "• Supports CSV files with comma separation\n"
            "• Supports TXT files with tab or space separation\n"
            "• Creates separate plots for each numeric column\n"
            "• Automatically detects headers"
        )
        self.instructions.setAlignment(Qt.AlignCenter)
        self.instructions.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                background-color: #f0f0f0;
                border: 2px dashed #ccc;
                border-radius: 10px;
                padding: 40px;
                margin: 20px;
            }
        """)
        
        layout.addWidget(self.instructions)
        layout.addWidget(self.scroll_area)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
        """)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1:
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith(('.csv', '.txt')):
                    event.accept()
                    return
        event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.load_and_plot_file(file_path)
    
    def clear_plots(self):
        # Clear existing plots
        for i in reversed(range(self.scroll_layout.count())):
            child = self.scroll_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
    
    def load_and_plot_file(self, file_path):
        try:
            # Hide instructions and show reset button
            self.instructions.hide()
            self.reset_button.show()
            
            # Clear existing plots
            self.clear_plots()
            
            # Load data based on file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext == '.txt':
                # Try different separators for txt files
                try:
                    df = pd.read_csv(file_path, sep='\t')
                except:
                    try:
                        df = pd.read_csv(file_path, sep=' ', skipinitialspace=True)
                    except:
                        df = pd.read_csv(file_path, sep=None, engine='python')
            
            # Add file info label
            file_info = QLabel(f"📁 File: {os.path.basename(file_path)} | Rows: {len(df)} | Columns: {len(df.columns)}")
            file_info.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: bold;
                    color: #333;
                    background-color: #e8f4fd;
                    border: 1px solid #bee5eb;
                    border-radius: 5px;
                    padding: 10px;
                    margin: 10px;
                }
            """)
            self.scroll_layout.addWidget(file_info)
            
            # Get numeric columns
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_columns:
                QMessageBox.warning(self, "No Numeric Data", 
                                  "No numeric columns found in the file to plot.")
                return
            
            # Create plots for each numeric column
            for col in numeric_columns:
                self.create_plot(df, col)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading file:\n{str(e)}")
    
    def create_plot(self, df, column):
        # Create plot canvas
        canvas = PlotCanvas(width=10, height=6)
        
        # Create the plot
        ax = canvas.fig.add_subplot(111)
        
        # Remove any NaN values
        data = df[column].dropna()
        
        if len(data) == 0:
            ax.text(0.5, 0.5, f'No valid data for {column}', 
                   transform=ax.transAxes, ha='center', va='center')
        else:
            # Create line plot with index (no markers)
            ax.plot(data.index, data.values, linewidth=2, alpha=0.8)
            ax.set_title(f'{column}', fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Index', fontsize=12)
            ax.set_ylabel(column, fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Add some styling
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#ccc')
            ax.spines['bottom'].set_color('#ccc')
        
        canvas.fig.tight_layout()
        
        # Add canvas to layout
        self.scroll_layout.addWidget(canvas)
        
        # Update the display
        canvas.draw()
    
    def reset_application(self):
        # Clear all plots
        self.clear_plots()
        
        # Show instructions again
        self.instructions.show()
        
        # Hide reset button
        self.reset_button.hide()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = DragDropPlotter()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()