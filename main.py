import fitz  # PyMuPDF
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import csv

# Function to extract data from the PDF
def extract_coordinates_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    extracted_data = []

    # Loop through all pages
    for page_num in range(len(doc)):
        page = doc[page_num]
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text")
                    bbox = span.get("bbox")  # Coordinates (x0, y0, x1, y1)
                    extracted_data.append({
                        "page": page_num + 1,
                        "text": text,
                        "x0": bbox[0],
                        "y0": bbox[1],
                        "x1": bbox[2],
                        "y1": bbox[3]
                    })

    return extracted_data

# Function to save the extracted data to CSV
def save_to_csv(extracted_data, output_file):
    # Convert list of dictionaries to pandas DataFrame
    df = pd.DataFrame(extracted_data)
    # Save the DataFrame to CSV
    df.to_csv(output_file, index=False)
    messagebox.showinfo("Success", f"Data saved successfully to {output_file}")

# Function to handle file selection and extraction
def open_pdf_and_extract():
    # Open a file dialog to select the PDF file
    pdf_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    
    if pdf_file:
        try:
            # Extract the data from the PDF
            extracted_data = extract_coordinates_from_pdf(pdf_file)
            if extracted_data:
                # Ask where to save the CSV
                output_file = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                           filetypes=[("CSV files", "*.csv")])
                if output_file:
                    # Save the extracted data to CSV
                    save_to_csv(extracted_data, output_file)
            else:
                messagebox.showwarning("No Data", "No data was extracted from the PDF.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    else:
        messagebox.showwarning("No File", "No file was selected.")

# Setup GUI
def setup_gui():
    root = tk.Tk()
    root.title("PDF to CSV Converter")

    # Create a label and button in the GUI
    label = tk.Label(root, text="Select a PDF to extract tabular data and save as CSV", pady=10)
    label.pack()

    button = tk.Button(root, text="Open PDF", command=open_pdf_and_extract, padx=20, pady=10)
    button.pack()

    root.geometry("400x150")
    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    setup_gui()
