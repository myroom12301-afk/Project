import customtkinter as ctk


def build(parent: ctk.CTkFrame) -> None:
    parent.grid_columnconfigure((0, 1, 2), weight=1, uniform="c")
    parent.grid_rowconfigure(2, weight=1)

    cards = ctk.CTkFrame(parent, fg_color="transparent", height=180)
    cards.grid(row=0, column=0, columnspan=3, sticky="ew", padx=14, pady=(6, 10))
    cards.grid_propagate(False)
    cards.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

    left = ctk.CTkFrame(cards, fg_color="#1A2B42", corner_radius=10)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    ctk.CTkLabel(left, text="Total Balance", text_color="#95A5C3", font=ctk.CTkFont(size=20)).pack(anchor="w", padx=14, pady=(12, 2))
    ctk.CTkLabel(left, text="$", text_color="#FFFFFF", font=ctk.CTkFont(size=42, weight="bold")).pack(anchor="w", padx=14)
    ctk.CTkLabel(left, text="All Accounts", text_color="#95A5C3", font=ctk.CTkFont(size=16)).pack(anchor="w", padx=14, pady=(0, 8))

    mid = ctk.CTkFrame(cards, fg_color="#1A2B42", corner_radius=0, border_width=2, border_color="#0A9BFF")
    mid.grid(row=0, column=1, sticky="nsew", padx=8)
    ctk.CTkLabel(mid, text="Goals", text_color="#A3B2CB", font=ctk.CTkFont(size=20)).place(x=14, y=12)
    ctk.CTkLabel(mid, text="◯", text_color="#8495AE", font=ctk.CTkFont(size=60)).place(x=16, y=56)
    ctk.CTkLabel(mid, text="$", text_color="#FFFFFF", font=ctk.CTkFont(size=30)).place(x=122, y=66)

    right = ctk.CTkFrame(cards, fg_color="#1A2B42", corner_radius=10)
    right.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
    ctk.CTkLabel(right, text="Upcoming Bills", text_color="#A3B2CB", font=ctk.CTkFont(size=20, underline=True)).pack(anchor="w", padx=14, pady=(12, 8))
    for _ in range(2):
        r = ctk.CTkFrame(right, fg_color="#08163B", corner_radius=8, height=34)
        r.pack(fill="x", padx=10, pady=6)
        r.pack_propagate(False)
        ctk.CTkLabel(r, text="$", text_color="#FFFFFF", font=ctk.CTkFont(size=22)).pack(side="right", padx=10)

    bottom = ctk.CTkFrame(parent, fg_color="transparent")
    bottom.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=14, pady=(0, 12))
    bottom.grid_columnconfigure((0, 1, 2), weight=1, uniform="b")
    bottom.grid_rowconfigure(0, weight=1)

    recent = ctk.CTkFrame(bottom, fg_color="#1A2B42", corner_radius=10)
    recent.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    h = ctk.CTkFrame(recent, fg_color="transparent")
    h.pack(fill="x", padx=12, pady=(10, 6))
    ctk.CTkLabel(h, text="Recent Transactions", text_color="#EEF3FF", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
    ctk.CTkLabel(h, text="View All", text_color="#00EAD0", font=ctk.CTkFont(size=14)).pack(side="right")

    week = ctk.CTkFrame(bottom, fg_color="#1A2B42", corner_radius=0, border_width=2, border_color="#66718A")
    week.grid(row=0, column=1, sticky="nsew", padx=8)
    ctk.CTkLabel(week, text="Weekly Comparison", text_color="#EEF3FF", font=ctk.CTkFont(size=20, weight="bold")).place(x=14, y=10)
    ctk.CTkFrame(week, fg_color="#7A869D", width=2, height=140).place(x=24, y=54)
    ctk.CTkFrame(week, fg_color="#7A869D", width=170, height=2).place(x=24, y=194)
    ctk.CTkLabel(week, text="■ This Week", text_color="#00E2C5", font=ctk.CTkFont(size=13)).place(x=20, y=212)
    ctk.CTkLabel(week, text="■ Last Week", text_color="#8A97AE", font=ctk.CTkFont(size=13)).place(x=114, y=212)

    exp = ctk.CTkFrame(bottom, fg_color="#1A2B42", corner_radius=10)
    exp.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
    ctk.CTkLabel(exp, text="Expenses Breakdown", text_color="#EEF3FF", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=14, pady=(10, 8))
    for _ in range(6):
        r = ctk.CTkFrame(exp, fg_color="#08163B", corner_radius=8, height=34)
        r.pack(fill="x", padx=10, pady=5)
        r.pack_propagate(False)
        ctk.CTkLabel(r, text="$", text_color="#FFFFFF", font=ctk.CTkFont(size=20)).pack(side="right", padx=10)
