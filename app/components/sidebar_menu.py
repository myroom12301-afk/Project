from __future__ import annotations

import customtkinter as ctk


class SidebarMenu(ctk.CTkFrame):
    def __init__(
        self,
        master,
        items: list[str],
        on_select,
        icons: dict[str, dict[str, ctk.CTkImage | None]] | None = None,
        user_icon: ctk.CTkImage | None = None,
    ) -> None:
        super().__init__(master, width=250, corner_radius=0, fg_color="#11192B")
        self.items = items
        self.on_select = on_select
        self.icons = icons or {}
        self.user_icon = user_icon
        self.menu_buttons: dict[str, ctk.CTkButton] = {}

        self.grid_rowconfigure(len(items) + 1, weight=1)
        self._build()

    def _build(self) -> None:
        brand = ctk.CTkLabel(
            self,
            text="FINEBANK.IO",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#F6F7FB",
        )
        brand.grid(row=0, column=0, padx=22, pady=(20, 36), sticky="w")

        for index, title in enumerate(self.items, start=1):
            button = ctk.CTkButton(
                self,
                text=title,
                image=self._get_icon(title, active=False),
                compound="left",
                anchor="w",
                height=46,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#16323A",
                text_color="#7F899A",
                font=ctk.CTkFont(family="Segoe UI", size=18),
                border_spacing=8,
                command=lambda name=title: self.on_select(name),
            )
            button.grid(row=index, column=0, padx=18, pady=8, sticky="ew")
            self.menu_buttons[title] = button

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=len(self.items) + 2, column=0, padx=18, pady=22, sticky="ew")

        avatar = ctk.CTkLabel(
            footer,
            text="",
            image=self.user_icon,
            width=36,
            height=36,
            fg_color="transparent",
        )
        avatar.pack(side="left", padx=(0, 12))

        user_block = ctk.CTkFrame(footer, fg_color="transparent")
        user_block.pack(side="left", fill="x", expand=True)

        self.footer_name = ctk.CTkLabel(
            user_block,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color="#F2F4F8",
        )
        self.footer_name.pack(anchor="w")

    def set_active(self, selected: str) -> None:
        for index, title in enumerate(self.items):
            button = self.menu_buttons[title]
            is_active = title == selected
            button.configure(
                image=self._get_icon(title, active=is_active),
                fg_color="#1C584F" if is_active else "transparent",
                text_color="#32E1B5" if is_active else "#7F899A",
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=18,
                    weight="bold" if is_active else "normal",
                ),
            )

    def set_username(self, username: str) -> None:
        self.footer_name.configure(text=username)

    def _get_icon(self, title: str, active: bool) -> ctk.CTkImage | None:
        variants = self.icons.get(title, {})
        return variants.get("active" if active else "inactive")
