import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import json
from datetime import datetime
from fpdf import FPDF
from num2words import num2words

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.db_utils import get_connection

class BillingWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Billing")
        self.geometry("900x650")
        self.configure(bg="#f5f5f5")

        # Header
        title = tk.Label(self, text="Create Bill", font=("Arial", 22, "bold"), bg="#f5f5f5")
        title.pack(pady=10)

        # --- Customer Details Frame
        cust_frame = tk.Frame(self, bg="#f5f5f5")
        cust_frame.pack(pady=4)
        tk.Label(cust_frame, text="Customer Name:", font=("Arial", 11), bg="#f5f5f5").grid(row=0, column=0, padx=3)
        self.cust_name_var = tk.StringVar()
        tk.Entry(cust_frame, textvariable=self.cust_name_var, width=25).grid(row=0, column=1, padx=3)
        tk.Label(cust_frame, text="Address:", font=("Arial", 11), bg="#f5f5f5").grid(row=0, column=2, padx=3)
        self.cust_addr_var = tk.StringVar()
        tk.Entry(cust_frame, textvariable=self.cust_addr_var, width=30).grid(row=0, column=3, padx=3)

        # --- Frame for product selection
        selection_frame = tk.Frame(self, bg="#f5f5f5")
        selection_frame.pack(pady=8)

        tk.Label(selection_frame, text="Product:", font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=0, padx=3)
        self.product_var = tk.StringVar()
        self.product_dropdown = ttk.Combobox(selection_frame, textvariable=self.product_var, width=32, state='readonly')
        self.product_dropdown.grid(row=0, column=1, padx=3)

        tk.Label(selection_frame, text="Quantity:", font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=2, padx=3)
        self.qty_var = tk.StringVar()
        tk.Entry(selection_frame, textvariable=self.qty_var, width=10).grid(row=0, column=3, padx=3)

        tk.Button(selection_frame, text="Add to Bill", command=self.add_to_bill, bg="#2e8b57", fg="white", font=("Arial", 11, "bold"), width=15).grid(row=0, column=4, padx=8)

        # --- Table for bill items
        self.bill_tree = ttk.Treeview(self, columns=("Name", "Unit Price", "Quantity", "Total"), show="headings", height=10)
        for col in ("Name", "Unit Price", "Quantity", "Total"):
            self.bill_tree.heading(col, text=col)
            self.bill_tree.column(col, anchor="center", width=160)
        self.bill_tree.pack(pady=14)

        # --- Subtotal, Tax, and Total display
        total_frame = tk.Frame(self, bg="#f5f5f5")
        total_frame.pack(anchor="e", pady=6, padx=40)

        self.subtotal_var = tk.StringVar(value="0.00")
        self.cgst_var = tk.StringVar(value="0.00")
        self.sgst_var = tk.StringVar(value="0.00")
        self.total_var = tk.StringVar(value="0.00")

        tk.Label(total_frame, text="Subtotal: Rs.", font=("Arial", 12, "bold"), bg="#f5f5f5").grid(row=0, column=0)
        tk.Label(total_frame, textvariable=self.subtotal_var, font=("Arial", 12, "bold"), bg="#f5f5f5").grid(row=0, column=1)
        tk.Label(total_frame, text="  CGST (9%): Rs.", font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=2)
        tk.Label(total_frame, textvariable=self.cgst_var, font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=3)
        tk.Label(total_frame, text="  SGST (9%): Rs.", font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=4)
        tk.Label(total_frame, textvariable=self.sgst_var, font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=5)
        tk.Label(total_frame, text="  Total: Rs.", font=("Arial", 13, "bold"), bg="#f5f5f5").grid(row=0, column=6)
        tk.Label(total_frame, textvariable=self.total_var, font=("Arial", 13, "bold"), bg="#f5f5f5").grid(row=0, column=7)

        # --- Complete Sale Button
        tk.Button(self, text="Complete Sale & Generate Bill", font=("Arial", 12, "bold"),
                  bg="#4682b4", fg="white", command=self.complete_sale, width=26).pack(pady=10)

        # --- Sales History Button
        tk.Button(self, text="View Sales History", font=("Arial", 11),
                  bg="#b0c4de", fg="black", command=self.open_sales_history, width=20).pack(pady=2)

        # Internal cart list
        self.cart = []  # Each item: (product_id, name, unit_price, quantity, total)
        self.load_products()

    def load_products(self):
        # Fetch products from DB and set in dropdown
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, quantity FROM products WHERE quantity > 0")
        self.products = cursor.fetchall()
        conn.close()
        self.product_dropdown['values'] = [f"{row[1]} (Rs.{row[2]})" for row in self.products]

    def add_to_bill(self):
        if not self.product_var.get():
            messagebox.showerror("Error", "Select a product.")
            return
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive integer.")
            return

        selected_index = self.product_dropdown.current()
        product = self.products[selected_index]
        product_id, name, price, available_qty = product

        if qty > available_qty:
            messagebox.showerror("Error", f"Only {available_qty} units available.")
            return

        for idx, item in enumerate(self.cart):
            if item[0] == product_id:
                new_qty = item[3] + qty
                if new_qty > available_qty:
                    messagebox.showerror("Error", f"Total quantity exceeds stock ({available_qty}).")
                    return
                new_total = price * new_qty
                self.cart[idx] = (product_id, name, price, new_qty, new_total)
                break
        else:
            total = price * qty
            self.cart.append((product_id, name, price, qty, total))

        self.refresh_bill_table()
        self.qty_var.set("")

    def refresh_bill_table(self):
        for row in self.bill_tree.get_children():
            self.bill_tree.delete(row)
        subtotal = 0.0
        for item in self.cart:
            _, name, price, qty, total = item
            self.bill_tree.insert("", tk.END, values=(name, f"{price:.2f}", qty, f"{total:.2f}"))
            subtotal += total
        cgst = round(subtotal * 0.09, 2)
        sgst = round(subtotal * 0.09, 2)
        total = round(subtotal + cgst + sgst, 2)
        self.subtotal_var.set(f"{subtotal:.2f}")
        self.cgst_var.set(f"{cgst:.2f}")
        self.sgst_var.set(f"{sgst:.2f}")
        self.total_var.set(f"{total:.2f}")

    def complete_sale(self):
        if not self.cart:
            messagebox.showerror("Error", "Cart is empty.")
            return

        # Tax calculations
        subtotal = sum(item[4] for item in self.cart)
        cgst = round(subtotal * 0.09, 2)
        sgst = round(subtotal * 0.09, 2)
        total = round(subtotal + cgst + sgst, 2)

        # Save to sales table
        conn = get_connection()
        cursor = conn.cursor()

        items_data = [
            {
                'product_id': item[0],
                'name': item[1],
                'unit_price': item[2],
                'quantity': item[3],
                'total': item[4]
            } for item in self.cart
        ]
        items_json = json.dumps(items_data)
        sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO sales (date, items, subtotal, cgst, sgst, total)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sale_date, items_json, subtotal, cgst, sgst, total))
        sale_id = cursor.lastrowid

        # Update product quantities
        for item in self.cart:
            product_id, _, _, qty, _ = item
            cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (qty, product_id))
        conn.commit()
        conn.close()

        # Export PDF Invoice
        self.export_invoice_pdf(
            sale_id, items_data, subtotal, cgst, sgst, total, sale_date,
            company_name="InventaBill Pvt Ltd",
            company_msg="Your Trusted Billing Partner",
            customer_name=self.cust_name_var.get(),
            customer_address=self.cust_addr_var.get(),
            terms="Goods once sold will not be taken back or exchanged."
        )

        messagebox.showinfo("Success", f"Sale completed!\nInvoice Total: Rs.{total:.2f}")
        self.cart = []
        self.refresh_bill_table()
        self.load_products()
        self.product_var.set("")
        self.qty_var.set("")
        self.cust_name_var.set("")
        self.cust_addr_var.set("")

    def export_invoice_pdf(self, sale_id, items, subtotal, cgst, sgst, total, date,
                          company_name, company_msg, customer_name, customer_address, terms):
        pdf = FPDF()
        pdf.add_page()

        # Header bar
        pdf.set_fill_color(32, 98, 165)
        pdf.rect(0, 0, 210, 20, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 16)
        pdf.set_xy(10, 8)
        pdf.cell(120, 10, company_name, ln=0, align="L")
        pdf.set_font("Arial", "", 10)
        pdf.set_xy(10, 14)
        pdf.cell(120, 6, company_msg, ln=0, align="L")
        # Invoice header
        pdf.set_font("Arial", "B", 13)
        pdf.set_xy(140, 10)
        pdf.cell(0, 6, "INVOICE", ln=1, align="L")
        pdf.set_font("Arial", "", 11)
        pdf.set_xy(140, 16)
        pdf.cell(0, 6, f"Invoice No: {sale_id}", ln=1, align="L")
        pdf.set_xy(140, 22)
        pdf.cell(0, 6, f"Invoice Date: {date[:10]}", ln=1, align="L")

        pdf.set_text_color(0, 0, 0)
        # Customer Details
        pdf.set_xy(10, 30)
        pdf.set_font("Arial", "", 11)
        pdf.cell(30, 8, "Name:")
        pdf.cell(0, 8, customer_name, ln=1)
        pdf.set_xy(10, 38)
        pdf.cell(30, 8, "Address:")
        pdf.cell(0, 8, customer_address, ln=1)

        # Table headers
        pdf.set_xy(10, 50)
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(224, 235, 255)
        pdf.cell(15, 8, "S.No.", 1, 0, 'C', 1)
        pdf.cell(70, 8, "Description", 1, 0, 'C', 1)
        pdf.cell(25, 8, "Qty", 1, 0, 'C', 1)
        pdf.cell(30, 8, "Rate", 1, 0, 'C', 1)
        pdf.cell(30, 8, "Amount", 1, 1, 'C', 1)

        # Table body
        pdf.set_font("Arial", "", 11)
        sn = 1
        for item in items:
            pdf.cell(15, 8, str(sn), 1, 0, 'C')
            pdf.cell(70, 8, str(item['name']), 1, 0, 'L')
            pdf.cell(25, 8, str(item['quantity']), 1, 0, 'C')
            pdf.cell(30, 8, "Rs.{:.2f}".format(item['unit_price']), 1, 0, 'R')
            pdf.cell(30, 8, "Rs.{:.2f}".format(item['total']), 1, 1, 'R')
            sn += 1

        # Totals, Taxes
        pdf.set_font("Arial", "B", 11)
        pdf.cell(140, 8, "Subtotal", 1, 0, 'R')
        pdf.cell(30, 8, "Rs.{:.2f}".format(subtotal), 1, 1, 'R')
        pdf.set_font("Arial", "", 11)
        pdf.cell(140, 8, "CGST (9%)", 1, 0, 'R')
        pdf.cell(30, 8, "Rs.{:.2f}".format(cgst), 1, 1, 'R')
        pdf.cell(140, 8, "SGST (9%)", 1, 0, 'R')
        pdf.cell(30, 8, "Rs.{:.2f}".format(sgst), 1, 1, 'R')
        pdf.set_font("Arial", "B", 11)
        pdf.cell(140, 8, "Total", 1, 0, 'R')
        pdf.cell(30, 8, "Rs.{:.2f}".format(total), 1, 1, 'R')

        # Rupees in words
        pdf.set_xy(10, pdf.get_y() + 3)
        pdf.set_font("Arial", "I", 10)
        try:
            words = num2words(int(total), to='cardinal', lang='en_IN').capitalize() + " only"
        except:
            words = "Amount in words not available"
        pdf.cell(0, 7, f"Rupees in words: {words}", ln=1)

        # Terms and conditions
        pdf.set_xy(10, pdf.get_y() + 2)
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 7, f"Terms & Conditions: {terms}", ln=1)

        # Signature line at the bottom
        pdf.set_xy(160, 270)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, "Signature", ln=1, align="R")

        # Footer bar
        pdf.set_fill_color(32, 98, 165)
        pdf.rect(0, 287, 210, 10, 'F')

        pdf.output(f"Invoice_{sale_id}.pdf")
        messagebox.showinfo("Invoice Saved", f"PDF Invoice saved as Invoice_{sale_id}.pdf")

    def open_sales_history(self):
        try:
            from ui.sales_history_window import SalesHistoryWindow
            SalesHistoryWindow(self)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Sales History window.\n{e}")

# For testing standalone
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    BillingWindow()
    root.mainloop()
