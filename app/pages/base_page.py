from __future__ import annotations

import customtkinter as ctk


class BasePage(ctk.CTkFrame):
    def __init__(self, master, controller) -> None:
        super().__init__(master, fg_color="#0B1220", corner_radius=0)
        self.controller = controller

    def on_show(self) -> None:
        return
