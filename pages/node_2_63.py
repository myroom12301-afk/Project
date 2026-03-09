import customtkinter as ctk


def build(parent: ctk.CTkFrame) -> None:
    parent.grid_columnconfigure((0, 1), weight=1)
    parent.grid_rowconfigure(1, weight=1)

    top = ctk.CTkFrame(parent, fg_color="transparent")
    top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(8, 10))
    top.grid_columnconfigure((0, 1, 2, 3), weight=1)

    for i, title in enumerate(["Total Accounts", "Cash", "Bank", "Credit"]):
        card = ctk.CTkFrame(top, fg_color="#1A2B42", corner_radius=10, height=92)
        card.grid(row=0, column=i, sticky="ew", padx=6)
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, text_color="#96A6C2", font=ctk.CTkFont(size=15)).pack(anchor="w", padx=12, pady=(10, 0))
        ctk.CTkLabel(card, text="$", text_color="#FFFFFF", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w", padx=12)

    left = ctk.CTkFrame(parent, fg_color="#1A2B42", corner_radius=10)
    left.grid(row=1, column=0, sticky="nsew", padx=(14, 7), pady=(0, 12))
    ctk.CTkLabel(left, text="All Balances", text_color="#EEF3FF", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=14, pady=(10, 8))
    for i in range(7):
        r = ctk.CTkFrame(left, fg_color="#08163B", corner_radius=8, height=44)
        r.pack(fill="x", padx=12, pady=5)
        r.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(r, text=f"Account {i+1}", text_color="#CFD9EA", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(r, text="$", text_color="#FFFFFF", font=ctk.CTkFont(size=18)).grid(row=0, column=1, padx=10, pady=10, sticky="e")

    right = ctk.CTkFrame(parent, fg_color="#1A2B42", corner_radius=10)
    right.grid(row=1, column=1, sticky="nsew", padx=(7, 14), pady=(0, 12))
    ctk.CTkLabel(right, text="Account Details", text_color="#EEF3FF", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=14, pady=(10, 8))

    box = ctk.CTkFrame(right, fg_color="#08163B", corner_radius=8)
    box.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    ctk.CTkLabel(box, text="Details Preview", text_color="#8A98B1", font=ctk.CTkFont(size=16)).place(relx=0.5, rely=0.5, anchor="center")
