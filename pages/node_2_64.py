import customtkinter as ctk


def build(parent: ctk.CTkFrame) -> None:
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_rowconfigure(1, weight=1)

    filters = ctk.CTkFrame(parent, fg_color="#1A2B42", corner_radius=10, height=64)
    filters.grid(row=0, column=0, sticky="ew", padx=14, pady=(8, 10))
    filters.grid_propagate(False)
    for i, t in enumerate(["All", "Income", "Expense", "Transfer", "Date"]):
        ctk.CTkButton(
            filters,
            text=t,
            width=96,
            height=36,
            corner_radius=8,
            fg_color="#08163B",
            hover_color="#10204A",
            text_color="#D4DDF0",
            font=ctk.CTkFont(size=13),
        ).pack(side="left", padx=8, pady=14)

    table = ctk.CTkFrame(parent, fg_color="#1A2B42", corner_radius=10)
    table.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 12))

    head = ctk.CTkFrame(table, fg_color="#08163B", corner_radius=8, height=42)
    head.pack(fill="x", padx=10, pady=(10, 6))
    head.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
    for i, col in enumerate(["Date", "Account", "Category", "Note", "Amount"]):
        ctk.CTkLabel(head, text=col, text_color="#8FA0BE", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=i, padx=8, pady=10, sticky="w"
        )

    for _ in range(11):
        row = ctk.CTkFrame(table, fg_color="#08163B", corner_radius=8, height=38)
        row.pack(fill="x", padx=10, pady=4)
        row.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        vals = ["00/00/0000", "Account", "Category", "Transaction text", "$"]
        for i, val in enumerate(vals):
            ctk.CTkLabel(row, text=val, text_color="#D0DBEF", font=ctk.CTkFont(size=12)).grid(
                row=0, column=i, padx=8, pady=8, sticky="e" if i == 4 else "w"
            )
