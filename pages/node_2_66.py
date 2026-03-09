import customtkinter as ctk


_CARD = "#1D2B40"
_SLOT = "#0A1738"
_TEXT = "#EEF3FF"
_MUTED = "#97A5BE"
_ACCENT = "#16C7A8"
_BAR_GRAY = "#3A4961"


def _mini_bars(container: ctk.CTkFrame) -> None:
    chart = ctk.CTkFrame(container, fg_color="transparent")
    chart.pack(fill="both", expand=True, padx=16, pady=(4, 10))

    canvas = ctk.CTkFrame(chart, fg_color="#1D2B40")
    canvas.pack(fill="both", expand=True)

    ctk.CTkFrame(canvas, fg_color="#6E7B93", width=1, height=96).place(x=14, y=18)
    ctk.CTkFrame(canvas, fg_color="#6E7B93", width=330, height=1).place(x=14, y=114)

    vals = [65, 82, 96, 82, 98, 102]
    names = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
    x = 26
    for i, h in enumerate(vals):
        ctk.CTkFrame(canvas, fg_color=_ACCENT, width=26, height=h, corner_radius=3).place(x=x, y=114 - h)
        ctk.CTkLabel(canvas, text=names[i], text_color="#6F809C", font=ctk.CTkFont(size=7)).place(x=x + 4, y=116)
        x += 35


def _compare_bars(container: ctk.CTkFrame) -> None:
    chart = ctk.CTkFrame(container, fg_color="transparent")
    chart.pack(fill="both", expand=True, padx=16, pady=(4, 10))

    canvas = ctk.CTkFrame(chart, fg_color="#1D2B40")
    canvas.pack(fill="both", expand=True)

    ctk.CTkFrame(canvas, fg_color="#6E7B93", width=1, height=96).place(x=14, y=18)
    ctk.CTkFrame(canvas, fg_color="#6E7B93", width=380, height=1).place(x=14, y=114)

    labels = ["Housing", "Food", "Shopping", "Entertainment", "Transport"]
    this_m = [108, 76, 78, 48, 35]
    last_m = [96, 84, 82, 40, 35]

    x = 24
    for i in range(5):
        ctk.CTkFrame(canvas, fg_color=_ACCENT, width=22, height=this_m[i], corner_radius=3).place(x=x, y=114 - this_m[i])
        ctk.CTkFrame(canvas, fg_color=_BAR_GRAY, width=22, height=last_m[i], corner_radius=3).place(x=x + 26, y=114 - last_m[i])
        ctk.CTkLabel(canvas, text=labels[i], text_color="#6F809C", font=ctk.CTkFont(size=6)).place(x=x - 1, y=116)
        x += 70

    ctk.CTkLabel(canvas, text="■ This Month", text_color=_ACCENT, font=ctk.CTkFont(size=8)).place(x=130, y=126)
    ctk.CTkLabel(canvas, text="■ Last Month", text_color="#8A97AE", font=ctk.CTkFont(size=8)).place(x=206, y=126)


def build(parent: ctk.CTkFrame) -> None:
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_rowconfigure(2, weight=1)

    ctk.CTkLabel(parent, text="Expenses", text_color=_TEXT, font=ctk.CTkFont(size=20, weight="bold")).grid(
        row=0, column=0, sticky="w", padx=16, pady=(4, 0)
    )
    ctk.CTkLabel(parent, text="Total This Month", text_color=_MUTED, font=ctk.CTkFont(size=12)).grid(
        row=1, column=0, sticky="w", padx=16, pady=(0, 8)
    )

    top = ctk.CTkFrame(parent, fg_color=_CARD, corner_radius=14)
    top.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
    top.grid_columnconfigure(1, weight=1)

    left = ctk.CTkFrame(top, fg_color="transparent", width=280)
    left.grid(row=0, column=0, sticky="nsw", padx=(16, 6), pady=14)
    left.grid_propagate(False)
    ctk.CTkLabel(left, text="Expenses by Category", text_color=_TEXT, font=ctk.CTkFont(size=28)).pack(anchor="w")
    ctk.CTkLabel(left, text="Total", text_color=_MUTED, font=ctk.CTkFont(size=24)).pack(side="bottom", pady=10)

    right = ctk.CTkFrame(top, fg_color="#13233E", corner_radius=2, border_width=2, border_color="#11A8FF")
    right.grid(row=0, column=1, sticky="nsew", padx=(6, 16), pady=12)
    right.grid_columnconfigure((0, 1), weight=1)

    for r in range(4):
        for c in range(2):
            slot = ctk.CTkFrame(right, fg_color=_SLOT, corner_radius=12, height=52)
            slot.grid(row=r, column=c, sticky="ew", padx=10, pady=8)

    bottom = ctk.CTkFrame(parent, fg_color="transparent")
    bottom.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 12))
    bottom.grid_columnconfigure((0, 1), weight=1, uniform="exp")
    bottom.grid_rowconfigure(0, weight=1)

    monthly = ctk.CTkFrame(bottom, fg_color=_CARD, corner_radius=22)
    monthly.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    ctk.CTkLabel(monthly, text="Monthly Trend", text_color=_TEXT, font=ctk.CTkFont(size=30)).pack(anchor="w", padx=20, pady=(14, 2))
    _mini_bars(monthly)

    compare = ctk.CTkFrame(bottom, fg_color=_CARD, corner_radius=22)
    compare.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
    ctk.CTkLabel(compare, text="This Month vs Last Month", text_color=_TEXT, font=ctk.CTkFont(size=30)).pack(
        anchor="w", padx=20, pady=(14, 2)
    )
    _compare_bars(compare)
