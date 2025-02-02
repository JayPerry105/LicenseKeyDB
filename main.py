import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# Database Initialization
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


# Add a new license
def add_license():
    machine_id = entry_machine_id.get()
    license_type = entry_license_type.get()
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


# Load licenses into the table
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


# Delete selected license
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


# Clear input fields
def clear_fields():
    entry_machine_id.delete(0, tk.END)
    entry_license_type.delete(0, tk.END)
    entry_issue_date.delete(0, tk.END)
    entry_license_key.delete(0, tk.END)


# GUI Setup
root = tk.Tk()
root.title("License Key Database App")
root.geometry("800x500")
root.configure(bg="#2C2F33")  # Dark Gray Background
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(5, weight=1)

style = ttk.Style()
style.configure("TButton", background="#7289DA", foreground="white", font=("Arial", 10, "bold"))
style.configure("Treeview", background="#23272A", foreground="white", fieldbackground="#23272A")
style.map("TButton", background=[("active", "#5865F2")])

# Labels and Entry Fields
tk.Label(root, text="Machine ID:", bg="#2C2F33", fg="white").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
tk.Label(root, text="License Type:", bg="#2C2F33", fg="white").grid(row=1, column=0, sticky="ew", padx=5, pady=5)
tk.Label(root, text="Issue Date (YYYY-MM-DD):", bg="#2C2F33", fg="white").grid(row=2, column=0, sticky="ew", padx=5,
                                                                               pady=5)
tk.Label(root, text="License Key:", bg="#2C2F33", fg="white").grid(row=3, column=0, sticky="ew", padx=5, pady=5)

entry_machine_id = tk.Entry(root)
entry_machine_id.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
entry_license_type = tk.Entry(root)
entry_license_type.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
entry_issue_date = tk.Entry(root)
entry_issue_date.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
entry_license_key = tk.Entry(root)
entry_license_key.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

# Buttons
tk.Button(root, text="Add License", command=add_license, bg="#7289DA", fg="white").grid(row=4, column=0, padx=5, pady=5,
                                                                                        sticky="ew")
tk.Button(root, text="Delete License", command=delete_license, bg="#7289DA", fg="white").grid(row=4, column=1, padx=5,
                                                                                              pady=5, sticky="ew")
tk.Button(root, text="Clear Fields", command=clear_fields, bg="#7289DA", fg="white").grid(row=4, column=2, padx=5,
                                                                                          pady=5, sticky="ew")

# Table to display data
tree = ttk.Treeview(root, columns=("ID", "Machine ID", "License Type", "Issue Date", "License Key", "Date Created"),
                    show="headings")
for col in ("ID", "Machine ID", "License Type", "Issue Date", "License Key", "Date Created"):
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=120, stretch=True)

tree.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

# Make treeview columns expand with window
for col in tree["columns"]:
    tree.column(col, stretch=True)

# Initialize Database and Load Data
init_db()
load_licenses()

# Run Application
root.mainloop()
