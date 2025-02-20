import csv
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from datetime import datetime

# initialize main app window
root = tk.Tk()
root.title("License Key Database App")
root.geometry("800x500")
root.configure(bg="#2C2F33")
root.grid_rowconfigure(5, weight=1)
root.grid_columnconfigure(0, weight=1)

# db initialization
def init_db():
    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS licenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        machine_id TEXT NOT NULL,
                        license_type TEXT NOT NULL,
                        issue_date TEXT NOT NULL,
                        license_key TEXT NOT NULL UNIQUE,
                        date_of_creation TEXT DEFAULT (DATE('now'))
                    )''')
    conn.commit()
    conn.close()

# function to clear input fields
def clear_fields():
    entry_machine_id.delete(0, tk.END)
    combo_license_type.set('')  # Clear the combobox
    entry_issue_date.delete(0, tk.END)
    entry_license_key.delete(0, tk.END)

# function to refresh table
def refresh_table():
    load_licenses()

# function to add a new license
def add_license():
    machine_id = entry_machine_id.get()
    license_type = combo_license_type.get()
    issue_date = entry_issue_date.get()
    license_key = entry_license_key.get()
    date_of_creation = datetime.now().strftime("%Y-%m-%d")

    if not all([machine_id, license_type, issue_date, license_key]):
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        conn = sqlite3.connect("licenses.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO licenses (machine_id, license_type, issue_date, license_key, date_of_creation) VALUES (?, ?, ?, ?, ?)",
            (machine_id, license_type, issue_date, license_key, date_of_creation))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "License added successfully!")
        clear_fields()
        load_licenses()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "License Key must be unique!")


# function to load licenses into the table
def load_licenses():
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM licenses")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        tree.insert("", "end", values=row)


# function to delete selected license
def delete_license():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a license to delete!")
        return

    license_id = tree.item(selected_item)['values'][0]
    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM licenses WHERE id=?", (license_id,))
    conn.commit()
    conn.close()
    load_licenses()
    messagebox.showinfo("Success", "License deleted successfully!")


# function to search licenses by Machine ID
def search_by_machine_id():
    machine_id = entry_machine_id.get()
    if not machine_id:
        messagebox.showerror("Error", "Machine ID not found!")
        return

    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM licenses WHERE machine_id=?", (machine_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        messagebox.showerror("Error", "Machine ID not found!")
        return

    for row in tree.get_children():
        tree.delete(row)

    for row in rows:
        tree.insert("", "end", values=row)


# function to edit the selected license
def edit_license():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a license to edit!")
        return

    license_data = tree.item(selected_item)['values']

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit License")
    edit_window.geometry("400x300")

    tk.Label(edit_window, text="Machine ID:").pack()
    edit_machine_id = tk.Entry(edit_window)
    edit_machine_id.pack()
    edit_machine_id.insert(0, license_data[1])

    tk.Label(edit_window, text="License Type:").pack()
    edit_license_type = ttk.Combobox(edit_window, values=["ACT", "VC", "DPocket", "RDI"])
    edit_license_type.pack()
    edit_license_type.set(license_data[2])

    tk.Label(edit_window, text="Issue Date:").pack()
    edit_issue_date = tk.Entry(edit_window)
    edit_issue_date.pack()
    edit_issue_date.insert(0, license_data[3])

    tk.Label(edit_window, text="License Key:").pack()
    edit_license_key = tk.Entry(edit_window)
    edit_license_key.pack()
    edit_license_key.insert(0, license_data[4])

    def save_changes():
        conn = sqlite3.connect("licenses.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE licenses SET machine_id=?, license_type=?, issue_date=?, license_key=? WHERE id=?",
                       (edit_machine_id.get(), edit_license_type.get(), edit_issue_date.get(), edit_license_key.get(),
                        license_data[0]))
        conn.commit()
        conn.close()
        load_licenses()
        edit_window.destroy()

    tk.Button(edit_window, text="Save", command=save_changes).pack()
    tk.Button(edit_window, text="Discard Changes", command=edit_window.destroy).pack()

# function to set current date in issue date field
def set_current_date():
    entry_issue_date.delete(0, tk.END)
    entry_issue_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

def backup_to_csv():
    # create directory if not already there
    directory = "C:/License Logs"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # define file path with current date/time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"{directory}/LicenseKeyBackup_{current_time}.csv"

    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM licenses")
    rows = cursor.fetchall()
    conn.close()

    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([i[0] for i in cursor.description])
        writer.writerows(rows)

    messagebox.showinfo("Success", f"Backup successful! File saved to {file_path}")


def load_from_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return  # user cancels the open dialog

    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()

    with open(file_path, "r") as file:
        reader = csv.reader(file)
        headers = next(reader)
        for row in reader:
            cursor.execute("INSERT INTO licenses (machine_id, license_type, issue_date, license_key, date_of_creation) VALUES (?, ?, ?, ?, ?)",
                           (row[1], row[2], row[3], row[4], row[5]))

    conn.commit()
    conn.close()
    load_licenses()
    messagebox.showinfo("Success", "Data loaded successfully!")


# labels and entry fields
frame_top = tk.Frame(root, bg="#2C2F33")
frame_top.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

for i in range(4):
    frame_top.grid_columnconfigure(i, weight=1)

tk.Label(frame_top, text="Machine ID:", bg="#2C2F33", fg="white").grid(row=0, column=0, padx=10, pady=5, sticky="ew")
entry_machine_id = tk.Entry(frame_top)
entry_machine_id.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

tk.Label(frame_top, text="License Type:", bg="#2C2F33", fg="white").grid(row=0, column=2, padx=10, pady=5, sticky="ew")
combo_license_type = ttk.Combobox(frame_top, values=["ACT", "VC", "DPocket", "RDI"])
combo_license_type.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

tk.Label(frame_top, text="Issue Date (YYYY-MM-DD):", bg="#2C2F33", fg="white").grid(row=1, column=0, padx=10, pady=5, sticky="ew")
entry_issue_date = tk.Entry(frame_top, width=10)  # Set a specific width for the entry field
entry_issue_date.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
tk.Button(frame_top, text="Today", command=set_current_date, bg="#2d3f7d", fg="white", width=5).grid(row=2, column=1, padx=10, pady=0, sticky="w")

tk.Label(frame_top, text="License Key:", bg="#2C2F33", fg="white").grid(row=1, column=2, padx=10, pady=5, sticky="ew")
entry_license_key = tk.Entry(frame_top)
entry_license_key.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

# table and scrollbar
frame_table = tk.Frame(root)
frame_table.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
frame_table.grid_rowconfigure(0, weight=1)
frame_table.grid_columnconfigure(0, weight=1)

scrollbar = ttk.Scrollbar(frame_table, orient="vertical")
scrollbar.pack(side="right", fill="y")

tree = ttk.Treeview(frame_table, columns=("ID", "Machine ID", "License Type", "Issue Date", "License Key", "Date Created"), show="headings", yscrollcommand=scrollbar.set)

tree.heading("ID", text="ID")
tree.column("ID", anchor="center", width=50, stretch=False)  # Adjusted width for ID column

for col in ("Machine ID", "License Type", "Issue Date", "License Key", "Date Created"):
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=120, stretch=True)

tree.pack(expand=True, fill="both")
scrollbar.config(command=tree.yview)

# buttons
frame_buttons = tk.Frame(root, bg="#2C2F33")
frame_buttons.grid(row=6, column=0, columnspan=4, sticky="ew", padx=10, pady=10)

for i in range(4):
    frame_buttons.grid_columnconfigure(i, weight=1)

tk.Button(frame_buttons, text="Add License", command=add_license, bg="#1d8036", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
tk.Button(frame_buttons, text="Delete License", command=delete_license, bg="#7d1711", fg="white").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
tk.Button(frame_buttons, text="Edit License", command=edit_license, bg="#2d3f7d", fg="white").grid(row=0, column=2, padx=5, pady=5, sticky="ew")
tk.Button(frame_buttons, text="Search", command=search_by_machine_id, bg="#2d3f7d", fg="white").grid(row=0, column=3, padx=5, pady=5, sticky="ew")
tk.Button(frame_buttons, text="Refresh", command=refresh_table, bg="#2d3f7d", fg="white").grid(row=0, column=4, padx=5, pady=5, sticky="ew")
tk.Button(frame_buttons, text="Backup to CSV", command=backup_to_csv, bg="#8b8d9e", fg="black").grid(row=1, column=3, padx=0, pady=10, sticky="e")
tk.Button(frame_buttons, text="Load from CSV", command=load_from_csv, bg="#8b8d9e", fg="black").grid(row=1, column=4, padx=3, pady=10, sticky="w")

# initialize db and load data
init_db()
load_licenses()

# run app
root.mainloop()