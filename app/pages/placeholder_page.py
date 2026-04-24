from __future__ import annotations

import customtkinter as ctk

from .base_page import BasePage


class PlaceholderPage(BasePage):
    def __init__(self, master, controller, title: str, description: str) -> None:
        super().__init__(master, controller)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(self, corner_radius=24, fg_color="#202B3C")
        card.grid(row=0, column=0, padx=32, pady=32, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color="#F7F8FC",
        ).pack(anchor="w", padx=28, pady=(28, 12))

        ctk.CTkLabel(
            card,
            text=description,
            justify="left",
            wraplength=720,
            font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color="#B7C0CE",
        ).pack(anchor="w", padx=28, pady=(0, 28))
