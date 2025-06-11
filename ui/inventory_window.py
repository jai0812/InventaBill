import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Ensure imports work if running from main.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.db_utils import get_connection, add_product  # We'll use add_product from earlier

class InventoryWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Inventory Management")
        self.geometry("600x400")

        # Table for showing products
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Category", "Price", "Quantity"), show="headings")
        for col in ("ID", "Name", "Category", "Price", "Quantity"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Entry fields for new product
        entry_frame = tk.Frame(self)
        entry_frame.pack(pady=5)
        tk.Label(entry_frame, text="Name").grid(row=0, column=0)
        tk.Label(entry_frame, text="Category").grid(row=0, column=1)
        tk.Label(entry_frame, text="Price").grid(row=0, column=2)
        tk.Label(entry_frame, text="Quantity").grid(row=0, column=3)

        self.name_var = tk.StringVar()
        self.cat_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.qty_var = tk.StringVar()

        tk.Entry(entry_frame, textvariable=self.name_var, width=15).grid(row=1, column=0)
        tk.Entry(entry_frame, textvariable=self.cat_var, width=15).grid(row=1, column=1)
        tk.Entry(entry_frame, textvariable=self.price_var, width=10).grid(row=1, column=2)
        tk.Entry(entry_frame, textvariable=self.qty_var, width=10).grid(row=1, column=3)
        tk.Button(entry_frame, text="Add Product", command=self.add_product).grid(row=1, column=4, padx=5)
        tk.Button(entry_frame, text="Delete Selected", command=self.delete_selected).grid(row=1, column=5, padx=5)
        tk.Button(entry_frame, text="Edit Selected", command=self.edit_selected).grid(row=1, column=6, padx=5)

        self.refresh_table()

    def refresh_table(self):
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Fetch all products from DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def add_product(self):
        name = self.name_var.get().strip()
        category = self.cat_var.get().strip()
        try:
            price = float(self.price_var.get())
            quantity = int(self.qty_var.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Price must be a number and quantity an integer.")
            return
        if not name or not category:
            messagebox.showerror("Missing info", "Please fill all fields.")
            return
        add_product(name, category, price, quantity)
        self.refresh_table()
        self.name_var.set("")
        self.cat_var.set("")
        self.price_var.set("")
        self.qty_var.set("")
        messagebox.showinfo("Success", f"Product '{name}' added.")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a product to delete.")
            return
        confirm = messagebox.askyesno("Delete", "Are you sure you want to delete the selected product?")
        if not confirm:
            return
        # Assumes 'ID' is in the first column
        item = self.tree.item(selected[0])
        product_id = item['values'][0]

        # Delete from database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        self.refresh_table()
        messagebox.showinfo("Deleted", "Product deleted successfully!")


    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a product to edit.")
            return

        item = self.tree.item(selected[0])
        product_id, name, category, price, quantity = item['values']

        # Pre-fill the entry fields
        self.name_var.set(name)
        self.cat_var.set(category)
        self.price_var.set(str(price))
        self.qty_var.set(str(quantity))

        # Change the "Add Product" button to "Update"
        def update_product():
            new_name = self.name_var.get().strip()
            new_category = self.cat_var.get().strip()
            try:
                new_price = float(self.price_var.get())
                new_quantity = int(self.qty_var.get())
            except ValueError:
                messagebox.showerror("Invalid input", "Price must be a number and quantity an integer.")
                return

            if not new_name or not new_category:
                messagebox.showerror("Missing info", "Please fill all fields.")
                return

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products
                SET name = ?, category = ?, price = ?, quantity = ?
                WHERE id = ?
            """, (new_name, new_category, new_price, new_quantity, product_id))
            conn.commit()
            conn.close()
            self.refresh_table()
            self.name_var.set("")
            self.cat_var.set("")
            self.price_var.set("")
            self.qty_var.set("")
            messagebox.showinfo("Success", "Product updated successfully!")
            # Restore add_product button
            add_btn.config(text="Add Product", command=self.add_product)

        # Change button to "Update"
        add_btn = entry_frame.grid_slaves(row=1, column=4)[0]
        add_btn.config(text="Update", command=update_product)




# Optional: For testing this window directly
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window
    inv = InventoryWindow()
    inv.mainloop()
