import customtkinter as ctk

from ..locale import t
from .base_dialog import BaseDialog


class CategoryDialog(BaseDialog):
    def __init__(self, master, cat: dict, on_deleted=None) -> None:
        self._cat = cat
        self._on_deleted = on_deleted
        super().__init__(master, 340, 260)
        self._build()

    def _build(self) -> None:
        name = self._cat["name"]
        desc = (self._cat.get("description") or "").strip()

        ctk.CTkLabel(
            self, text=t("cat_dialog.delete_q", name=name),
            font=ctk.CTkFont("Segoe UI", 18, weight="bold"),
            text_color="#F7F8FC", justify="center",
        ).grid(row=0, column=0, padx=28, pady=(28, 20))

        desc_frame = ctk.CTkFrame(self, fg_color="#131D2E", corner_radius=10)
        desc_frame.grid(row=1, column=0, padx=28, pady=(0, 24), sticky="ew")
        desc_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(desc_frame, text=t("cat_dialog.description"),
                     font=ctk.CTkFont("Segoe UI", 12), text_color="#5A6A7E",
                     ).grid(row=0, column=0, padx=14, pady=(10, 2), sticky="w")

        ctk.CTkLabel(
            desc_frame,
            text=desc if desc else t("cat_dialog.no_desc"),
            font=ctk.CTkFont("Segoe UI", 14),
            text_color="#C8CDD8" if desc else "#5A6A7E",
            wraplength=270, justify="left",
        ).grid(row=1, column=0, padx=14, pady=(0, 10), sticky="w")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, padx=28, pady=(0, 24), sticky="ew")
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_row, text=t("cat_dialog.cancel"), height=44, corner_radius=8,
                      fg_color="#1E2A3A", hover_color="#263345", text_color="#8B95A5",
                      font=ctk.CTkFont("Segoe UI", 14), command=self.destroy,
                      ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(btn_row, text=t("cat_dialog.delete"), height=44, corner_radius=8,
                      fg_color="#8B1A1A", hover_color="#A93226", text_color="#FFFFFF",
                      font=ctk.CTkFont("Segoe UI", 14, weight="bold"), command=self._on_delete,
                      ).grid(row=0, column=1, sticky="ew")

    def _on_delete(self) -> None:
        if self._on_deleted:
            self._on_deleted(self._cat["id"])
        self.destroy()
