from __future__ import annotations

import tkinter as tk


class SidebarMenu(tk.Frame):
    def __init__(
        self,
        master,
        items: list[str],
        on_select,
        icons: dict[str, dict[str, object | None]] | None = None,
        user_icon: object | None = None,
    ) -> None:
        super().__init__(master, width=250, bg="#11192B", highlightthickness=0, bd=0)
        self.items = items
        self.on_select = on_select
        self.icons = icons or {}
        self.user_icon = user_icon
        self.menu_rows: dict[str, tk.Frame] = {}
        self.icon_labels: dict[str, tk.Label] = {}
        self.text_labels: dict[str, tk.Label] = {}

        self.grid_propagate(False)
        self._build()

    def _build(self) -> None:
        brand = tk.Label(
            self,
            text="FINEBANK.IO",
            bg="#11192B",
            fg="#F6F7FB",
            font=("Segoe UI", 22, "bold"),
        )
        brand.grid(row=0, column=0, padx=22, pady=(20, 36), sticky="w")

        for index, title in enumerate(self.items, start=1):
            row = tk.Frame(self, bg="#11192B", highlightthickness=0, bd=0, cursor="hand2")
            row.grid(row=index, column=0, padx=18, pady=8, sticky="ew")
            row.grid_columnconfigure(1, weight=1)
            row.bind("<Button-1>", lambda _event, name=title: self.on_select(name))

            icon_label = tk.Label(
                row,
                image=self._get_icon(title, active=False),
                bg="#11192B",
                bd=0,
                highlightthickness=0,
                cursor="hand2",
            )
            icon_label.grid(row=0, column=0, padx=(12, 10), pady=10, sticky="w")
            icon_label.bind("<Button-1>", lambda _event, name=title: self.on_select(name))

            text_label = tk.Label(
                row,
                text=title,
                bg="#11192B",
                fg="#7F899A",
                font=("Segoe UI", 18),
                anchor="w",
                cursor="hand2",
            )
            text_label.grid(row=0, column=1, padx=(0, 12), sticky="ew")
            text_label.bind("<Button-1>", lambda _event, name=title: self.on_select(name))

            self.menu_rows[title] = row
            self.icon_labels[title] = icon_label
            self.text_labels[title] = text_label

        spacer = tk.Frame(self, bg="#11192B", height=1)
        spacer.grid(row=len(self.items) + 1, column=0, sticky="nsew")
        self.grid_rowconfigure(len(self.items) + 1, weight=1)

        footer = tk.Frame(self, bg="#11192B", highlightthickness=0, bd=0)
        footer.grid(row=len(self.items) + 2, column=0, padx=18, pady=22, sticky="ew")

        avatar = tk.Label(
            footer,
            image=self.user_icon,
            bg="#11192B",
            bd=0,
            highlightthickness=0,
        )
        avatar.pack(side="left", padx=(0, 12))

        self.footer_name = tk.Label(
            footer,
            text="",
            bg="#11192B",
            fg="#F2F4F8",
            font=("Segoe UI", 18),
            anchor="w",
        )
        self.footer_name.pack(side="left", fill="x", expand=True)

    def set_active(self, selected: str) -> None:
        for title in self.items:
            is_active = title == selected
            row_bg = "#1C584F" if is_active else "#11192B"
            text_color = "#32E1B5" if is_active else "#7F899A"
            font = ("Segoe UI", 18, "bold") if is_active else ("Segoe UI", 18)

            self.menu_rows[title].configure(bg=row_bg)
            self.icon_labels[title].configure(
                image=self._get_icon(title, active=is_active),
                bg=row_bg,
            )
            self.text_labels[title].configure(
                bg=row_bg,
                fg=text_color,
                font=font,
            )

    def set_username(self, username: str) -> None:
        self.footer_name.configure(text=username)

    def _get_icon(self, title: str, active: bool) -> object | None:
        variants = self.icons.get(title, {})
        return variants.get("active" if active else "inactive")
