from __future__ import annotations

import customtkinter as ctk

from ..locale import t

EXPENSE = 0
INCOME = 1

_ENTRY_STYLE = dict(
    height=44, corner_radius=8,
    fg_color="#131D2E", border_color="#22D7AF", border_width=2,
    text_color="#F7F8FC", placeholder_text_color="#5A6A7E",
)
_MENU_STYLE = dict(
    height=44, corner_radius=6,
    fg_color="#131D2E",
    button_color="#22D7AF", button_hover_color="#1BB99A",
    text_color="#F7F8FC",
    dropdown_fg_color="#1C2A3D", dropdown_text_color="#F7F8FC",
    dropdown_hover_color="#22344E",
)


def _bordered_menu(parent, row: int, **menu_kwargs) -> ctk.CTkOptionMenu:
    wrap = ctk.CTkFrame(parent, fg_color="#22D7AF", corner_radius=8)
    wrap.grid(row=row, column=0, padx=24, pady=(0, 14), sticky="ew")
    wrap.grid_columnconfigure(0, weight=1)
    menu = ctk.CTkOptionMenu(wrap, **menu_kwargs, **_MENU_STYLE)
    menu.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
    return menu


class TransactionDialog(ctk.CTkToplevel):
    def __init__(self, master, controller, on_saved=None) -> None:
        super().__init__(master)
        self.controller = controller
        self.on_saved = on_saved

        self.title("")
        self.geometry("380x460")
        self.resizable(False, False)
        self.configure(fg_color="#0E1726")
        self.lift()
        self.focus_force()
        self.after(50, self._center)
        self.after(50, self.grab_set)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _center(self) -> None:
        self.update_idletasks()
        p = self.master.winfo_toplevel()
        w, h = 380, 460
        self.geometry(f"{w}x{h}+{p.winfo_rootx() + (p.winfo_width() - w) // 2}+{p.winfo_rooty() + (p.winfo_height() - h) // 2}")

    def _label(self, row: int, text: str) -> None:
        ctk.CTkLabel(self, text=text,
                     font=ctk.CTkFont("Segoe UI", 13), text_color="#8B95A5",
                     ).grid(row=row, column=0, padx=24, pady=(0, 6), sticky="w")

    def _build(self) -> None:
        expense_label = t("common.expense")
        income_label  = t("common.income")

        ctk.CTkLabel(self, text=t("txn.new"),
                     font=ctk.CTkFont("Segoe UI", 18, weight="bold"), text_color="#C8CDD8",
                     ).grid(row=0, column=0, padx=24, pady=(24, 16), sticky="w")

        self._type_var = ctk.StringVar(value=expense_label)
        self._type_menu = _bordered_menu(self, row=1,
                                         variable=self._type_var,
                                         values=[expense_label, income_label],
                                         command=self._on_type_changed)

        self._label(2, t("txn.category"))
        initial_cats = self.controller.repo.get_categories(self.controller.user["id"], EXPENSE)
        initial_names = [c["name"] for c in initial_cats] or ["—"]
        self._category_var = ctk.StringVar(value=initial_names[0])
        self._category_menu = _bordered_menu(self, row=3,
                                              variable=self._category_var,
                                              values=initial_names)

        self._label(4, t("txn.amount"))
        sym = self.controller.currency_symbol
        self._amount_entry = ctk.CTkEntry(self, placeholder_text=sym, **_ENTRY_STYLE)
        self._amount_entry.grid(row=5, column=0, padx=24, pady=(0, 14), sticky="ew")

        self._label(6, t("txn.desc"))
        self._desc_entry = ctk.CTkEntry(self, placeholder_text=t("txn.desc_hint"), **_ENTRY_STYLE)
        self._desc_entry.grid(row=7, column=0, padx=24, pady=(0, 24), sticky="ew")
        self._desc_entry.bind("<KeyRelease>", self._limit_description)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=8, column=0, padx=24, pady=(0, 24), sticky="ew")
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_row, text=t("txn.cancel"), height=44, corner_radius=8,
                      fg_color="#1E2A3A", hover_color="#263345", text_color="#8B95A5",
                      font=ctk.CTkFont("Segoe UI", 14), command=self.destroy,
                      ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(btn_row, text=t("txn.add"), height=44, corner_radius=8,
                      fg_color="#1C584F", hover_color="#1A4F47", text_color="#32E1B5",
                      font=ctk.CTkFont("Segoe UI", 14, weight="bold"), command=self._on_submit,
                      ).grid(row=0, column=1, sticky="ew")

    def _on_type_changed(self, _value: str = "") -> None:
        val = self._type_var.get()
        tx_type = EXPENSE if val == t("common.expense") else INCOME
        cats  = self.controller.repo.get_categories(self.controller.user["id"], tx_type)
        names = [c["name"] for c in cats] or ["—"]
        self._category_menu.configure(values=names)
        self._category_var.set(names[0])

    def _limit_description(self, _event=None) -> None:
        if len(self._desc_entry.get()) > 20:
            self._desc_entry.delete(20, "end")

    def _on_submit(self) -> None:
        try:
            amount = float(self._amount_entry.get().strip().lstrip(self.controller.currency_symbol))
            if amount <= 0:
                raise ValueError
        except ValueError:
            self._amount_entry.configure(border_color="#E05555")
            self.after(1200, lambda: self._amount_entry.configure(border_color="#22D7AF"))
            return

        val     = self._type_var.get()
        tx_type = EXPENSE if val == t("common.expense") else INCOME
        cats    = self.controller.repo.get_categories(self.controller.user["id"], tx_type)
        cat_id  = next((c["id"] for c in cats if c["name"] == self._category_var.get()), None)
        if cat_id is None:
            return

        self.controller.repo.save_transaction(
            user_id=self.controller.user["id"],
            transaction_id=None,
            category_id=cat_id,
            tx_type=tx_type,
            amount=amount,
            description=self._desc_entry.get().strip(),
        )
        if self.on_saved:
            self.on_saved()
        self.destroy()