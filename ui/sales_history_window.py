import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.db_utils import get_connection

class SalesHistoryWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Sales History (Monthly)")
        self.geometry("800x500")

        # --- Month filter
        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=6)
        tk.Label(filter_frame, text="Month (YYYY-MM):", font=("Arial", 11)).pack(side=tk.LEFT)
        self.month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        tk.Entry(filter_frame, textvariable=self.month_var, width=8).pack(side=tk.LEFT, padx=4)
        tk.Button(filter_frame, text="Show", command=self.load_sales).pack(side=tk.LEFT, padx=4)

        # --- Sales table
        columns = ("Invoice No", "Date", "Subtotal", "CGST", "SGST", "Total")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=16)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=110)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Details button
        tk.Button(self, text="View Bill Details", font=("Arial", 11),
                  command=self.show_bill_details, bg="#4682b4", fg="white", width=20).pack(pady=5)

        self.load_sales()

    def load_sales(self):
        month = self.month_var.get().strip()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, date, subtotal, cgst, sgst, total
            FROM sales
            WHERE strftime('%Y-%m', date) = ?
            ORDER BY date DESC
        ''', (month,))
        rows = cursor.fetchall()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in rows:
            self.tree.insert("", tk.END, values=r)
        conn.close()

    def show_bill_details(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a sale record.")
            return
        invoice_id = self.tree.item(selected[0])['values'][0]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT items FROM sales WHERE id=?', (invoice_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            messagebox.showerror("Error", "Sale record not found.")
            return
        items = json.loads(row[0])
        details = "Product\tUnit Price\tQty\tTotal\n"
        details += "-"*40 + "\n"
        for item in items:
            details += f"{item['name']}\t₹{item['unit_price']:.2f}\t{item['quantity']}\t₹{item['total']:.2f}\n"
        messagebox.showinfo("Bill Details", details)

# For standalone test
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    SalesHistoryWindow()
    root.mainloop()
