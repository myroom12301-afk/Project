import customtkinter as ctk


BG_CARD = "#1E2B40"
BG_SLOT = "#061533"
TEXT_MAIN = "#EEF3FF"
TEXT_SUB = "#8D9AB3"
ACCENT = "#1DE5C8"


def _payment_card(parent: ctk.CTkFrame, app: str, date_text: str, badge_text: str, icon_bg: str) -> None:
    card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=8, height=88)
    card.pack_propagate(False)

    top = ctk.CTkFrame(card, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=(8, 2))

    ctk.CTkLabel(
        top,
        text=app[:2].upper(),
        width=18,
        height=18,
        fg_color=icon_bg,
        corner_radius=5,
        text_color="#FFFFFF",
        font=ctk.CTkFont(size=8, weight="bold"),
    ).pack(side="left")

    title_wrap = ctk.CTkFrame(top, fg_color="transparent")
    title_wrap.pack(side="left", padx=6)
    ctk.CTkLabel(title_wrap, text=app, text_color=TEXT_MAIN, font=ctk.CTkFont(size=9, weight="bold")).pack(anchor="w")
    ctk.CTkLabel(title_wrap, text="Subscription", text_color=TEXT_SUB, font=ctk.CTkFont(size=6)).pack(anchor="w")

    ctk.CTkLabel(top, text=f"◻ {date_text}", text_color=TEXT_SUB, font=ctk.CTkFont(size=7)).pack(side="right", pady=(4, 0))

    ctk.CTkLabel(
        card,
        text=badge_text,
        height=14,
        corner_radius=4,
        fg_color="#134D4B" if "11" in badge_text or "14" in badge_text else "#4A3036",
        text_color=ACCENT if "11" in badge_text or "14" in badge_text else "#FF7B7B",
        font=ctk.CTkFont(size=6, weight="bold"),
    ).pack(anchor="w", padx=10, pady=(16, 8))

    return card


def build(parent: ctk.CTkFrame) -> None:
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_rowconfigure(2, weight=1)

    ctk.CTkLabel(
        parent,
        text="Upcoming & Recurring Bills",
        text_color=TEXT_MAIN,
        font=ctk.CTkFont(size=24, weight="bold"),
    ).grid(row=0, column=0, sticky="w", padx=12, pady=(4, 0))

    ctk.CTkLabel(
        parent,
        text="Total Monthly",
        text_color=TEXT_SUB,
        font=ctk.CTkFont(size=11),
    ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 6))

    ctk.CTkButton(
        parent,
        text="+ Add Bill",
        width=84,
        height=28,
        corner_radius=12,
        fg_color="#1DD9BB",
        hover_color="#16C4A9",
        text_color="#07333B",
        font=ctk.CTkFont(size=10, weight="bold"),
    ).grid(row=1, column=0, sticky="e", padx=12, pady=(0, 6))

    ctk.CTkLabel(
        parent,
        text="Upcoming Payments",
        text_color=TEXT_MAIN,
        font=ctk.CTkFont(size=12, weight="bold"),
    ).grid(row=2, column=0, sticky="w", padx=12, pady=(0, 2))

    payments = ctk.CTkFrame(parent, fg_color="transparent")
    payments.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 8))
    payments.grid_columnconfigure((0, 1, 2), weight=1, uniform="pay")

    cards_data = [
        ("Figma Monthly", "May 15", "Due in 1 day", "#A035FF"),
        ("Adobe creative Cloud", "May 18", "Due in 4 days", "#FF2D2D"),
        ("Spotify Premium", "May 20", "Due in 6 day", "#18C95E"),
        ("Netflix Standard", "May 22", "Due in 8 day", "#FF2D2D"),
        ("GitHub Pro", "May 25", "Due in 11 day", "#48566F"),
        ("Apple iCloud+", "May 28", "Due in 14 day", "#2D86FF"),
    ]

    for i, (app, d, badge, icon_bg) in enumerate(cards_data):
        r = i // 3
        c = i % 3
        card_container = ctk.CTkFrame(payments, fg_color="transparent")
        card_container.grid(row=r, column=c, sticky="ew", padx=5, pady=5)
        card_container.grid_columnconfigure(0, weight=1)
        card = _payment_card(card_container, app, d, badge, icon_bg)
        card.grid(row=0, column=0, sticky="ew")

    ctk.CTkLabel(
        parent,
        text="Recurring Subscriptions",
        text_color=TEXT_MAIN,
        font=ctk.CTkFont(size=12, weight="bold"),
    ).grid(row=4, column=0, sticky="w", padx=12, pady=(2, 4))

    table_wrap = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=8)
    table_wrap.grid(row=5, column=0, sticky="nsew", padx=12, pady=(0, 8))
    table_wrap.grid_columnconfigure(0, weight=1)

    head = ctk.CTkFrame(table_wrap, fg_color="#131D35", corner_radius=0, height=24)
    head.grid(row=0, column=0, sticky="ew")
    head.grid_propagate(False)
    head.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
    headers = ["Name", "Amount", "Frequency", "Next Due", "Last Charge", "Actions"]
    for i, h in enumerate(headers):
        ctk.CTkLabel(head, text=h, text_color=TEXT_SUB, font=ctk.CTkFont(size=8)).grid(
            row=0, column=i, padx=8, pady=7, sticky="w"
        )

    body = ctk.CTkFrame(table_wrap, fg_color="#223B49", corner_radius=0)
    body.grid(row=1, column=0, sticky="nsew")
    for i in range(13):
        ctk.CTkFrame(body, fg_color="#5C6D7B", height=1).pack(fill="x", pady=(14 if i == 0 else 13, 0))

    footer = ctk.CTkFrame(parent, fg_color="transparent")
    footer.grid(row=6, column=0, sticky="ew", padx=12, pady=(0, 10))
    footer.grid_columnconfigure((0, 1, 2), weight=1, uniform="foot")

    summary = [
        ("▣", "Total Bills This Month", "#1CD9BF"),
        ("▣", "Due This Week", "#D7D700"),
        ("▣", "Active Subscriptions", "#1CD9BF"),
    ]
    for i, (icon, label, color) in enumerate(summary):
        box = ctk.CTkFrame(footer, fg_color=BG_CARD, corner_radius=8, height=52)
        box.grid(row=0, column=i, sticky="ew", padx=5)
        box.grid_propagate(False)
        ctk.CTkLabel(box, text=icon, text_color=color, font=ctk.CTkFont(size=10)).pack(side="left", padx=(10, 6), pady=16)
        ctk.CTkLabel(box, text=label, text_color=TEXT_SUB, font=ctk.CTkFont(size=9)).pack(side="left", pady=16)
