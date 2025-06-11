import tkinter as tk
from tkinter import messagebox
from ui.inventory_window import InventoryWindow  # Import your inventory window
from ui.billing_window import BillingWindow


class InventaBillApp:
    def __init__(self, root):
        self.root = root
        self.root.title("InventaBill - Billing & Inventory System")
        self.root.geometry("600x400")

        # Title label
        title = tk.Label(root, text="InventaBill", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        # Buttons for navigation
        inventory_btn = tk.Button(
            root,
            text="Inventory Management",
            font=("Arial", 14),
            width=25,
            command=self.open_inventory
        )
        inventory_btn.pack(pady=10)

        billing_btn = tk.Button(
            root,
            text="Billing",
            font=("Arial", 14),
            width=25,
            command=self.open_billing
        )
        billing_btn.pack(pady=10)

        exit_btn = tk.Button(
            root,
            text="Exit",
            font=("Arial", 14),
            width=25,
            command=self.exit_app
        )
        exit_btn.pack(pady=10)

    def open_inventory(self):
        InventoryWindow(self.root)

    def open_billing(self):
        messagebox.showinfo("Billing", "Billing Module will be added soon!")

    def exit_app(self):
        self.root.destroy()
    
    def open_billing(self):
        BillingWindow(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = InventaBillApp(root)
    root.mainloop()
