from __future__ import annotations

import customtkinter as ctk

from ..locale import t
from .base_page import BasePage

EXPENSE = 0
INCOME = 1


class CategoriesPage(BasePage):
    def __init__(self, master, controller) -> None:
        super().__init__(master, controller)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._expense_list: ctk.CTkScrollableFrame | None = None
        self._income_list: ctk.CTkScrollableFrame | None = None

        self._build_form_panel()
        self._build_categories_panel()

    def _build_form_panel(self) -> None:
        panel = ctk.CTkFrame(self, fg_color="#151F2E", corner_radius=18, width=290)
        panel.grid(row=0, column=0, padx=(24, 12), pady=24, sticky="nsew")
        panel.grid_propagate(False)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(9, weight=1)

        ctk.CTkLabel(panel, text=t("cats.add_title"),
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                     text_color="#F7F8FC", justify="left",
                     ).grid(row=0, column=0, padx=20, pady=(22, 20), sticky="w")

        ctk.CTkLabel(panel, text=t("cats.name"),
                     font=ctk.CTkFont("Segoe UI", 14), text_color="#9BAABF",
                     ).grid(row=1, column=0, padx=20, pady=(0, 6), sticky="w")

        name_wrap = ctk.CTkFrame(panel, fg_color="#1C2A3D", corner_radius=10, height=44)
        name_wrap.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="ew")
        name_wrap.grid_propagate(False)
        name_wrap.grid_columnconfigure(1, weight=1)
        name_wrap.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(name_wrap, text="✉", fg_color="transparent",
                     text_color="#5A6A7E", font=ctk.CTkFont("Segoe UI", 18),
                     ).grid(row=0, column=0, padx=(12, 4))

        self._name_entry = ctk.CTkEntry(
            name_wrap, placeholder_text=t("cats.name_hint"),
            fg_color="transparent", border_width=0,
            text_color="#F7F8FC", placeholder_text_color="#5A6A7E",
        )
        self._name_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(panel, text=t("cats.type"),
                     font=ctk.CTkFont("Segoe UI", 14), text_color="#9BAABF",
                     ).grid(row=3, column=0, padx=20, pady=(0, 6), sticky="w")

        type_wrap = ctk.CTkFrame(panel, fg_color="#1C2A3D", corner_radius=10, height=44)
        type_wrap.grid(row=4, column=0, padx=20, pady=(0, 16), sticky="ew")
        type_wrap.grid_propagate(False)
        type_wrap.grid_columnconfigure(1, weight=1)
        type_wrap.grid_rowconfigure(0, weight=1)

        expense_label = t("common.expense")
        income_label  = t("common.income")
        self._type_icons = {
            expense_label: self.controller._load_icon("Vector (1).svg", size=(22, 22), color="#5A6A7E"),
            income_label:  self.controller._load_icon("fi-1.svg",        size=(22, 22), color="#5A6A7E"),
        }
        self._type_icon_label = ctk.CTkLabel(
            type_wrap, image=self._type_icons[expense_label], text="", fg_color="transparent")
        self._type_icon_label.grid(row=0, column=0, padx=(10, 4))

        self._type_var = ctk.StringVar(value=expense_label)
        ctk.CTkOptionMenu(
            type_wrap, values=[expense_label, income_label],
            variable=self._type_var, command=self._on_type_icon_changed,
            height=36, corner_radius=8,
            fg_color="#1C2A3D", button_color="#1C584F", button_hover_color="#1A4F47",
            text_color="#F7F8FC", dropdown_fg_color="#1C2A3D",
            dropdown_text_color="#F7F8FC", dropdown_hover_color="#22344E",
        ).grid(row=0, column=1, sticky="ew", padx=(0, 4), pady=4)

        ctk.CTkLabel(panel, text=t("cats.desc_opt"),
                     font=ctk.CTkFont("Segoe UI", 14), text_color="#9BAABF",
                     ).grid(row=5, column=0, padx=20, pady=(0, 6), sticky="w")

        self._desc_textbox = ctk.CTkTextbox(
            panel, height=80, corner_radius=10,
            fg_color="#1C2A3D", border_width=0, text_color="#F7F8FC",
            scrollbar_button_color="#2A3A50", scrollbar_button_hover_color="#3A4A60",
        )
        self._desc_textbox.grid(row=6, column=0, padx=20, pady=(0, 4), sticky="ew")
        self._desc_textbox.bind("<KeyRelease>", self._on_desc_change)

        self._desc_counter = ctk.CTkLabel(panel, text="0/30",
                                          font=ctk.CTkFont("Segoe UI", 12), text_color="#5A6A7E")
        self._desc_counter.grid(row=7, column=0, padx=20, pady=(0, 4), sticky="e")

        ctk.CTkButton(
            panel, text=t("cats.add_btn"),
            height=48, corner_radius=12,
            fg_color="#1C584F", hover_color="#1A4F47",
            text_color="#32E1B5", font=ctk.CTkFont("Segoe UI", 15, weight="bold"),
            command=self._on_add_from_form,
        ).grid(row=8, column=0, padx=20, pady=(0, 16), sticky="ew")

    def _build_categories_panel(self) -> None:
        panel = ctk.CTkFrame(self, fg_color="#151F2E", corner_radius=18)
        panel.grid(row=0, column=1, padx=(12, 24), pady=24, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_columnconfigure(1, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(panel, text=t("cats.title"),
                     font=ctk.CTkFont("Segoe UI", 22, weight="bold"), text_color="#F7F8FC",
                     ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 14), sticky="w")

        self._expense_list = self._build_column(panel, t("common.expense"), EXPENSE, col=0)
        self._income_list  = self._build_column(panel, t("common.income"),  INCOME, col=1)

    def _build_column(self, parent, title: str, tx_type: int, col: int) -> ctk.CTkScrollableFrame:
        pad_l = 16 if col == 0 else 8
        pad_r = 8  if col == 0 else 16

        container = ctk.CTkFrame(parent, fg_color="#1A2538", corner_radius=14)
        container.grid(row=1, column=col, padx=(pad_l, pad_r), pady=(0, 16), sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        ctk.CTkButton(
            container, text=title, height=40, corner_radius=10,
            fg_color="#1C584F", hover_color="#1C584F",
            text_color="#32E1B5", font=ctk.CTkFont("Segoe UI", 16, weight="bold"), cursor="arrow",
        ).grid(row=0, column=0, padx=12, pady=(12, 10), sticky="ew")

        scroll = ctk.CTkScrollableFrame(
            container, fg_color="transparent",
            scrollbar_button_color="#2A3A50", scrollbar_button_hover_color="#3A4A60",
        )
        scroll.grid(row=1, column=0, padx=4, pady=(0, 12), sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        return scroll

    def _render_categories(self) -> None:
        user_id = self.controller.user["id"]
        repo    = self.controller.repo

        for tx_type, scroll in [(EXPENSE, self._expense_list), (INCOME, self._income_list)]:
            for widget in scroll.winfo_children():
                widget.destroy()

            categories = repo.get_categories(user_id, tx_type)
            defaults = [c for c in categories if c["is_default"]]
            added    = [c for c in categories if not c["is_default"]]

            row = 0
            if defaults:
                self._section_label(scroll, t("cats.default_section"), row)
                row += 1
                for cat in defaults:
                    self._category_button(scroll, cat, row); row += 1

            if added:
                self._section_label(scroll, t("cats.added_section"), row, top_pad=12)
                row += 1
                for cat in added:
                    self._category_button(scroll, cat, row); row += 1

    def _section_label(self, parent, text: str, row: int, top_pad: int = 8) -> None:
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont("Segoe UI", 13), text_color="#7F899A",
                     ).grid(row=row, column=0, padx=12, pady=(top_pad, 4), sticky="w")

    def _category_button(self, parent, cat, row: int) -> None:
        ctk.CTkButton(
            parent, text=f"● {cat['name']}", anchor="w",
            height=36, corner_radius=8,
            fg_color="transparent", hover_color="#22344E",
            text_color="#C8D4E3", font=ctk.CTkFont("Segoe UI", 14),
            command=lambda c=cat: self._on_category_click(c),
        ).grid(row=row, column=0, padx=8, pady=2, sticky="ew")

    def _on_category_click(self, cat) -> None:
        from .category_dialog import CategoryDialog
        CategoryDialog(self, cat=dict(cat), on_deleted=self._on_category_deleted)

    def _on_category_deleted(self, category_id: int) -> None:
        self.controller.repo.delete_category(category_id)
        self._render_categories()

    def _on_type_icon_changed(self, value: str) -> None:
        self._type_icon_label.configure(image=self._type_icons.get(value))

    def _on_desc_change(self, _event=None) -> None:
        text  = self._desc_textbox.get("1.0", "end-1c")
        count = len(text)
        over  = count > 30
        self._desc_counter.configure(text=f"{count}/30",
                                     text_color="#E05555" if over else "#5A6A7E")
        self._desc_textbox.configure(border_color="#E05555" if over else "#2A3A50")

    def _on_add_from_form(self) -> None:
        name = self._name_entry.get().strip()
        if not name:
            self._name_entry.configure(border_color="#E05555")
            self.after(1200, lambda: self._name_entry.configure(border_color="#2A3A50"))
            return

        desc = self._desc_textbox.get("1.0", "end-1c").strip()
        if len(desc) > 30:
            self._desc_textbox.configure(border_color="#E05555")
            return

        val = self._type_var.get()
        tx_type = EXPENSE if val == t("common.expense") else INCOME
        self.controller.repo.add_category(self.controller.user["id"], name, tx_type, desc)
        self._name_entry.delete(0, "end")
        self._desc_textbox.delete("1.0", "end")
        self._desc_counter.configure(text="0/30", text_color="#5A6A7E")
        self._desc_textbox.configure(border_color="#2A3A50")
        self._render_categories()

    def on_show(self) -> None:
        self._render_categories()