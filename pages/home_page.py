import customtkinter as ctk

from pages import node_2_61, node_2_63, node_2_64, node_2_65, node_2_66


class HomePage(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Desktop - 1")
        self.geometry("1366x768")
        self.minsize(1280, 720)
        self.configure(fg_color="#020d24")
        self.after(100, self._maximize_window)

        self.page_builders = {
            "overview": node_2_61.build,
            "balances": node_2_63.build,
            "transactions": node_2_64.build,
            "bills": node_2_65.build,
            "expenses": node_2_66.build,
        }
        self.page_titles = {
            "overview": "Overview",
            "balances": "Balances",
            "transactions": "Transactions",
            "bills": "Bills",
            "expenses": "Expenses",
        }
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        self.active_page = "overview"

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()
        self.show_page("overview")

    def _maximize_window(self) -> None:
        try:
            self.state("zoomed")
        except Exception:
            try:
                self.attributes("-zoomed", True)
            except Exception:
                pass

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color="#081432")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="FINEBANK.IO",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color="#F2F7FF",
        ).pack(anchor="w", padx=10, pady=(8, 16))

        nav = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav.pack(fill="x", padx=8)

        items = [
            ("overview", "Overview"),
            ("balances", "Balances"),
            ("transactions", "Transactions"),
            ("bills", "Bills"),
            ("expenses", "Expenses"),
        ]

        for key, label in items:
            btn = ctk.CTkButton(
                nav,
                text=label,
                height=42,
                corner_radius=8,
                anchor="w",
                fg_color="transparent",
                hover_color="#10244E",
                text_color="#A2AFC4",
                font=ctk.CTkFont(size=28),
                command=lambda page=key: self.show_page(page),
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[key] = btn

        bottom = ctk.CTkFrame(self.sidebar, fg_color="#091534", corner_radius=0)
        bottom.pack(side="bottom", fill="x")
        ctk.CTkFrame(bottom, fg_color="#7D879D", height=1).pack(fill="x")

        user_row = ctk.CTkFrame(bottom, fg_color="transparent", height=50)
        user_row.pack(fill="x", padx=10, pady=8)
        user_row.pack_propagate(False)

        ctk.CTkLabel(
            user_row,
            text="◉",
            width=28,
            height=28,
            fg_color="#10E3C2",
            corner_radius=14,
            text_color="#091534",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left", padx=(4, 8), pady=6)

        ctk.CTkLabel(
            user_row,
            text="Tanzir Rahman",
            text_color="#DCE5F5",
            font=ctk.CTkFont(size=22),
        ).pack(side="left", pady=6)

    def _build_main_area(self) -> None:
        self.area = ctk.CTkFrame(self, fg_color="#030F2B", corner_radius=0)
        self.area.grid(row=0, column=1, sticky="nsew")
        self.area.grid_columnconfigure(0, weight=1)
        self.area.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(self.area, fg_color="transparent", height=74)
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 8))
        top.grid_propagate(False)
        top.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(top, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        self.header_title = ctk.CTkLabel(
            left,
            text="Hello Tanzir",
            text_color="#F2F7FF",
            font=ctk.CTkFont(size=36),
        )
        self.header_title.pack(anchor="w", pady=(0, 0))

        ctk.CTkLabel(
            left,
            text="May 19, 2023",
            text_color="#8B98B4",
            font=ctk.CTkFont(size=22),
        ).pack(anchor="w")

        right = ctk.CTkFrame(top, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        ctk.CTkEntry(
            right,
            width=260,
            height=36,
            corner_radius=8,
            fg_color="#16233F",
            border_width=0,
            text_color="#CFD9EA",
            placeholder_text="Search transaction....",
            placeholder_text_color="#8B98B4",
            font=ctk.CTkFont(size=20),
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            right,
            text="🔔",
            width=34,
            height=34,
            corner_radius=8,
            fg_color="#16233F",
            text_color="#8B98B4",
            font=ctk.CTkFont(size=20),
        ).pack(side="left")

        ctk.CTkFrame(self.area, fg_color="#73809D", height=1).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        self.content = ctk.CTkFrame(self.area, fg_color="transparent")
        self.content.grid(row=2, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def show_page(self, key: str) -> None:
        if key not in self.page_builders:
            return

        self.active_page = key
        self.header_title.configure(text=f"Hello Tanzir  |  {self.page_titles[key]}")

        for page_key, btn in self.nav_buttons.items():
            if page_key == key:
                btn.configure(fg_color="#0B3A4A", text_color="#15E4C7")
            else:
                btn.configure(fg_color="transparent", text_color="#A2AFC4")

        for child in self.content.winfo_children():
            child.destroy()

        page_root = ctk.CTkFrame(self.content, fg_color="transparent")
        page_root.grid(row=0, column=0, sticky="nsew")
        self.page_builders[key](page_root)
