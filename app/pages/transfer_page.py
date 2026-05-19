import json
import threading
import tkinter as tk
import urllib.request

import customtkinter as ctk

from ..locale import t
from .base_dialog import BaseDialog
from .base_page import BasePage

CURRENCIES = [
    "USD", "EUR", "RUB", "KGS", "CNY", "TRY", "GBP",
    "JPY", "CHF", "CAD", "AUD", "KZT", "BYN", "UAH",
]


def _api_fetch(base: str) -> dict[str, float]:
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        with urllib.request.urlopen(url, timeout=6) as resp:
            data = json.loads(resp.read())
            return data.get("rates", {})
    except Exception:
        return {}


class AddRateDialog(BaseDialog):
    def __init__(self, master, base_currency: str, existing: list[str], on_add) -> None:
        self._base     = base_currency
        self._existing = existing
        self._on_add   = on_add
        super().__init__(master, 300, 195)
        self._build()

    def _build(self) -> None:
        font  = ctk.CTkFont(family="Segoe UI", size=14)
        small = ctk.CTkFont(family="Segoe UI", size=12)

        ctk.CTkLabel(
            self, text=t("rates.dialog_title"),
            font=ctk.CTkFont("Segoe UI", 18, "bold"), text_color="#F7F8FC",
        ).pack(pady=(22, 4))

        ctk.CTkLabel(self, text=f"→ {self._base}", font=small, text_color="#7D8798").pack(pady=(0, 14))

        available = [c for c in CURRENCIES if c != self._base and c not in self._existing]
        self.from_var = ctk.StringVar(value=available[0])
        ctk.CTkOptionMenu(
            self, values=available, variable=self.from_var,
            width=200, height=40, corner_radius=8,
            fg_color="#1A2435", button_color="#253347", button_hover_color="#2E3D50",
            text_color="#EDF2FA", font=font,
        ).pack(padx=24)

        ctk.CTkButton(
            self, text=t("rates.dialog_add"),
            height=40, corner_radius=10,
            fg_color="#229D84", hover_color="#1E816D",
            text_color="#ECFFFC", font=font,
            command=self._submit,
        ).pack(fill="x", padx=24, pady=(14, 6))

        ctk.CTkButton(
            self, text=t("common.cancel"),
            height=32, corner_radius=10,
            fg_color="transparent", hover_color="#1A2435",
            text_color="#7D8798", font=small,
            command=self.destroy,
        ).pack(fill="x", padx=24)

    def _submit(self) -> None:
        self._on_add(self.from_var.get())
        self.destroy()


class ConversionTransferDialog(BaseDialog):
    def __init__(self, master, row: object, on_confirm) -> None:
        self._row        = row
        self._on_confirm = on_confirm
        super().__init__(master, 340, 230)
        self._build()

    def _build(self) -> None:
        bold  = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        med   = ctk.CTkFont(family="Segoe UI", size=14)
        small = ctk.CTkFont(family="Segoe UI", size=12)

        ctk.CTkLabel(self, text=t("converter.transfer_title"), font=bold, text_color="#F7F8FC").pack(pady=(22, 12))

        from_str = f"{self._row['from_amount']:,.2f} {self._row['from_currency']}"
        to_str   = f"{self._row['to_amount']:,.2f} {self._row['to_currency']}"
        ctk.CTkLabel(self, text=f"{from_str}  →  {to_str}", font=med, text_color="#29E073").pack(pady=(0, 6))

        ctk.CTkLabel(
            self,
            text=t("converter.transfer_hint", currency=self._row["to_currency"]),
            font=small, text_color="#7D8798", wraplength=280,
        ).pack(pady=(0, 18))

        ctk.CTkButton(
            self, text=t("converter.transfer_btn"),
            height=42, corner_radius=10,
            fg_color="#229D84", hover_color="#1E816D",
            text_color="#ECFFFC", font=med,
            command=self._confirm,
        ).pack(fill="x", padx=28, pady=(0, 8))

        ctk.CTkButton(
            self, text=t("common.cancel"),
            height=34, corner_radius=10,
            fg_color="transparent", hover_color="#1A2435",
            text_color="#7D8798", font=small,
            command=self.destroy,
        ).pack(fill="x", padx=28)

    def _confirm(self) -> None:
        self._on_confirm(self._row)
        self.destroy()


class TransferPage(BasePage):
    def __init__(self, master, controller) -> None:
        super().__init__(master, controller)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.small_font = ctk.CTkFont(family="Segoe UI", size=13)
        self.body_font  = ctk.CTkFont(family="Segoe UI", size=15)
        self.title_font = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")

        self._live_rates: dict[str, dict[str, float]] = {}
        self._add_dialog:      AddRateDialog | None = None
        self._transfer_dialog: ConversionTransferDialog | None = None

        self._build_top_section()
        self._build_history_section()

    @property
    def repo(self):
        return self.controller.repo

    @property
    def user(self):
        return self.controller.user

    @property
    def _base_code(self) -> str:
        try:
            return self.user["currency"] or "USD"
        except Exception:
            return "USD"

    def on_show(self) -> None:
        self._refresh_rates_display()
        self._refresh_history()
        self._fetch_rates_async()

    # ── top: converter + rates ────────────────────────────────────────────────

    def _build_top_section(self) -> None:
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=22, pady=(20, 10))
        top.grid_columnconfigure(0, weight=3)
        top.grid_columnconfigure(1, weight=2)

        self._build_converter_card(top)
        self._build_rates_card(top)

    def _build_converter_card(self, parent) -> None:
        card = ctk.CTkFrame(parent, corner_radius=18, fg_color="#202B3C")
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=t("converter.title"), font=self.title_font, text_color="#F7F8FC",
                     ).grid(row=0, column=0, sticky="w", padx=22, pady=(22, 16))

        ctk.CTkLabel(card, text=t("converter.from_lbl"), font=self.small_font, text_color="#7D8798").grid(row=1, column=0, sticky="w", padx=22)

        from_row = ctk.CTkFrame(card, fg_color="transparent")
        from_row.grid(row=2, column=0, sticky="ew", padx=22, pady=(6, 4))
        from_row.grid_columnconfigure(1, weight=1)

        self.from_var = ctk.StringVar(value="USD")
        self.from_menu = ctk.CTkOptionMenu(
            from_row, values=["USD"], variable=self.from_var,
            width=120, height=48, corner_radius=10,
            fg_color="#1A2435", button_color="#253347", button_hover_color="#2E3D50",
            text_color="#EDF2FA", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            command=self._on_currency_changed,
        )
        self.from_menu.grid(row=0, column=0, padx=(0, 10))

        self.amount_entry = ctk.CTkEntry(
            from_row, height=48, corner_radius=10,
            fg_color="#1A2435", border_color="#2E3D50", border_width=1,
            text_color="#EDF2FA", font=ctk.CTkFont(family="Segoe UI", size=18), justify="right",
        )
        self.amount_entry.grid(row=0, column=1, sticky="ew")
        self.amount_entry.insert(0, "100.00")
        self.amount_entry.bind("<KeyRelease>", self._on_amount_changed)

        swap_row = ctk.CTkFrame(card, fg_color="transparent")
        swap_row.grid(row=3, column=0, sticky="ew", padx=22, pady=6)
        swap_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(swap_row, text="↓↑", font=ctk.CTkFont(family="Segoe UI", size=18),
                     text_color="#8BAAD4").grid(row=0, column=0)

        ctk.CTkLabel(card, text=t("converter.to_lbl"), font=self.small_font, text_color="#7D8798").grid(row=4, column=0, sticky="w", padx=22)

        to_row = ctk.CTkFrame(card, fg_color="transparent")
        to_row.grid(row=5, column=0, sticky="ew", padx=22, pady=(6, 4))
        to_row.grid_columnconfigure(1, weight=1)

        self.to_currency_lbl = ctk.CTkLabel(
            to_row, text=self._base_code,
            width=120, height=48, corner_radius=10,
            fg_color="#1A2435", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#EDF2FA",
        )
        self.to_currency_lbl.grid(row=0, column=0, padx=(0, 10))

        self.result_lbl = ctk.CTkLabel(
            to_row, text="0.00", height=48, corner_radius=10,
            fg_color="#1A2435", font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color="#EDF2FA", anchor="e",
        )
        self.result_lbl.grid(row=0, column=1, sticky="ew")

        self.rate_info_lbl = ctk.CTkLabel(card, text="", font=self.small_font, text_color="#6B7A8E")
        self.rate_info_lbl.grid(row=6, column=0, pady=(8, 10))

        ctk.CTkButton(
            card, text=t("converter.convert_btn"),
            height=48, corner_radius=12,
            fg_color="#229D84", hover_color="#1E816D",
            text_color="#ECFFFC", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            command=self._on_convert,
        ).grid(row=7, column=0, sticky="ew", padx=22, pady=(0, 22))

    def _build_rates_card(self, parent) -> None:
        card = ctk.CTkFrame(parent, corner_radius=18, fg_color="#202B3C")
        card.grid(row=0, column=1, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(card, text=t("rates.title"), font=self.title_font, text_color="#F7F8FC").grid(row=0, column=0, sticky="w", padx=22, pady=(22, 8))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 4))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text=t("rates.col_currency"), font=self.small_font, text_color="#7D8798").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(hdr, text=t("rates.col_rate"),     font=self.small_font, text_color="#7D8798").grid(row=0, column=1, sticky="e")
        ctk.CTkFrame(card, height=1, fg_color="#2E3D50").grid(row=1, column=0, sticky="sew", padx=14)

        self.rates_frame = ctk.CTkScrollableFrame(card, fg_color="transparent", corner_radius=0)
        self.rates_frame.grid(row=2, column=0, sticky="nsew", padx=4, pady=(4, 0))
        self.rates_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            card, text=t("rates.add_btn"),
            height=38, corner_radius=10,
            fg_color="transparent", border_width=1, border_color="#2E8B6E",
            text_color="#29E073", hover_color="#1A3028",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            command=self._on_add_rate,
        ).grid(row=3, column=0, sticky="ew", padx=18, pady=14)

    def _refresh_rates_display(self) -> None:
        for child in self.rates_frame.winfo_children():
            child.destroy()

        base = self._base_code
        try:
            pairs = self.repo.get_exchange_rates(self.user["id"])
        except Exception:
            return

        for i, row in enumerate(pairs):
            live = self._live_rates.get(row["from_currency"], {})
            rate = live.get(base, row["rate"])

            r = ctk.CTkFrame(self.rates_frame, fg_color="transparent", corner_radius=0)
            r.grid(row=i, column=0, sticky="ew")
            r.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(r, text=f"{row['from_currency']} → {base}", font=self.body_font, text_color="#D8DEE8").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))
            ctk.CTkLabel(r, text=f"{rate:.2f}", font=self.body_font, text_color="#C8D0DC").grid(row=0, column=1, sticky="e", padx=10, pady=(8, 0))

            sep = tk.Frame(r, bg="#FFFFFF", height=1)
            sep.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=(8, 0))

        current = [row["from_currency"] for row in pairs]
        if current:
            self.from_menu.configure(values=current)
            if self.from_var.get() not in current:
                self.from_var.set(current[0])

        self.to_currency_lbl.configure(text=base)
        self._recalculate_result()

    def _fetch_rates_async(self) -> None:
        try:
            pairs = self.repo.get_exchange_rates(self.user["id"])
        except Exception:
            return

        base  = self._base_code
        froms = list({p["from_currency"] for p in pairs})

        def worker():
            for from_c in froms:
                fetched = _api_fetch(from_c)
                if not fetched:
                    continue
                self._live_rates[from_c] = fetched
                rate_to_base = fetched.get(base)
                if rate_to_base is None:
                    continue
                for pair in pairs:
                    if pair["from_currency"] == from_c:
                        try:
                            self.repo.update_exchange_rate(pair["id"], rate_to_base)
                        except Exception:
                            pass
            try:
                self.after(0, self._refresh_rates_display)
                self.after(0, self._recalculate_result)
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _build_history_section(self) -> None:
        card = ctk.CTkFrame(self, corner_radius=18, fg_color="#202B3C")
        card.grid(row=1, column=0, sticky="nsew", padx=22, pady=(0, 20))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            card, text=t("converter.history_title"),
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color="#F7F8FC",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 10))

        table_wrap = ctk.CTkFrame(card, fg_color="transparent")
        table_wrap.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(table_wrap, fg_color="#162034", corner_radius=8)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(0, weight=0, minsize=150)
        hdr.grid_columnconfigure(1, weight=1, minsize=220)
        hdr.grid_columnconfigure(2, weight=1, minsize=220)
        hdr.grid_columnconfigure(3, weight=0, minsize=130)

        for col, key, anchor in (
            (0, "converter.col_date", "w"),
            (1, "converter.col_from", "w"),
            (2, "converter.col_to",   "w"),
            (3, "converter.col_rate", "e"),
        ):
            ctk.CTkLabel(hdr, text=t(key), font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#8A93A3", anchor=anchor).grid(row=0, column=col, sticky="ew", padx=14, pady=9)

        body_scroll = ctk.CTkScrollableFrame(
            table_wrap, fg_color="transparent", corner_radius=0,
            scrollbar_button_color="#2A3A50", scrollbar_button_hover_color="#3A4A60",
        )
        body_scroll.grid(row=1, column=0, sticky="nsew", pady=(2, 0))
        body_scroll.grid_columnconfigure(0, weight=1)

        self.history_rows = ctk.CTkFrame(body_scroll, fg_color="transparent")
        self.history_rows.grid(row=0, column=0, sticky="ew")
        self.history_rows.grid_columnconfigure(0, weight=1)

    def _refresh_history(self) -> None:
        for w in self.history_rows.winfo_children():
            w.destroy()

        try:
            rows = self.repo.get_conversion_history(self.user["id"])
        except Exception:
            return

        if not rows:
            empty = ctk.CTkFrame(self.history_rows, fg_color="#263241", corner_radius=0, height=54)
            empty.grid(row=0, column=0, sticky="ew")
            empty.grid_propagate(False)
            ctk.CTkLabel(empty, text=t("txlist.no_transactions"), font=ctk.CTkFont(family="Segoe UI", size=14), text_color="#7F899A").place(relx=0.5, rely=0.5, anchor="center")
            return

        for i, row in enumerate(rows):
            date_str = row["created_at"][2:10].replace("-", ".") if row["created_at"] else ""
            from_str = f"{row['from_amount']:,.0f} {row['from_currency']}"
            to_str   = f"{row['to_amount']:,.0f} {row['to_currency']}"
            rate_str = f"{row['rate']:.2f}"

            rf = ctk.CTkFrame(self.history_rows, fg_color="#263241", corner_radius=0, height=36, cursor="hand2")
            rf.grid(row=i, column=0, sticky="ew", pady=(0, 2))
            rf.grid_propagate(False)
            rf.grid_columnconfigure(0, weight=0, minsize=150)
            rf.grid_columnconfigure(1, weight=1, minsize=220)
            rf.grid_columnconfigure(2, weight=1, minsize=220)
            rf.grid_columnconfigure(3, weight=0, minsize=130)

            lbl_date = ctk.CTkLabel(rf, text=date_str, font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#F4F6FA", anchor="w", cursor="hand2")
            lbl_from = ctk.CTkLabel(rf, text=from_str, font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#9AA5B5", anchor="w", cursor="hand2")
            lbl_to   = ctk.CTkLabel(rf, text=to_str,   font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#9AA5B5", anchor="w", cursor="hand2")
            lbl_rate = ctk.CTkLabel(rf, text=rate_str, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#C8D0DC", anchor="e", cursor="hand2")

            lbl_date.grid(row=0, column=0, sticky="ew", padx=14, pady=7)
            lbl_from.grid(row=0, column=1, sticky="ew", padx=14, pady=7)
            lbl_to  .grid(row=0, column=2, sticky="ew", padx=14, pady=7)
            lbl_rate.grid(row=0, column=3, sticky="ew", padx=14, pady=7)

            for widget in (rf, lbl_date, lbl_from, lbl_to, lbl_rate):
                widget.bind("<Button-1>", lambda _, r=row: self._on_history_click(r))
                widget.bind("<Enter>",    lambda _, f=rf: f.configure(fg_color="#2E3D52"))
                widget.bind("<Leave>",    lambda _, f=rf: f.configure(fg_color="#263241"))

    # ── converter logic ───────────────────────────────────────────────────────

    def _get_rate(self, from_c: str, to_c: str) -> float | None:
        rate = self._live_rates.get(from_c, {}).get(to_c)
        if rate is None:
            try:
                db_pairs = self.repo.get_exchange_rates(self.user["id"])
                row = next((r for r in db_pairs if r["from_currency"] == from_c), None)
                rate = row["rate"] if row else None
            except Exception:
                rate = None
        return rate

    def _recalculate_result(self) -> None:
        try:
            amount = float(self.amount_entry.get().replace(",", "").replace(" ", ""))
        except ValueError:
            self.result_lbl.configure(text="—")
            self.rate_info_lbl.configure(text="")
            return

        from_c = self.from_var.get()
        to_c   = self._base_code
        rate   = self._get_rate(from_c, to_c)

        if rate is not None:
            self.result_lbl.configure(text=f"{amount * rate:,.2f}")
            self.rate_info_lbl.configure(text=f"1 {from_c} = {rate:.4f} {to_c}")
        else:
            self.result_lbl.configure(text="—")
            self.rate_info_lbl.configure(text=t("converter.no_rate"))

    def _on_currency_changed(self, _value: str = "") -> None:
        self._recalculate_result()

    def _on_amount_changed(self, _event=None) -> None:
        self._recalculate_result()

    def _on_convert(self) -> None:
        try:
            amount = float(self.amount_entry.get().replace(",", "").replace(" ", ""))
        except ValueError:
            return

        from_c = self.from_var.get()
        to_c   = self._base_code
        rate   = self._get_rate(from_c, to_c)

        if rate is None:
            return

        try:
            self.repo.save_conversion(self.user["id"], amount, from_c, amount * rate, to_c, rate)
        except Exception:
            return
        self._refresh_history()

    def _on_add_rate(self) -> None:
        if self._add_dialog is not None and self._add_dialog.winfo_exists():
            self._add_dialog.focus_force()
            return
        try:
            existing = self.repo.get_exchange_rates(self.user["id"])
            existing_codes = [r["from_currency"] for r in existing]
        except Exception:
            existing_codes = []
        self._add_dialog = AddRateDialog(self, self._base_code, existing_codes, self._on_rate_added)

    def _on_rate_added(self, from_c: str) -> None:
        base = self._base_code
        try:
            existing = self.repo.get_exchange_rates(self.user["id"])
            if any(r["from_currency"] == from_c for r in existing):
                return
            if len(existing) >= 5:
                self.repo.delete_exchange_rate(existing[0]["id"])
            self.repo.add_exchange_rate(self.user["id"], from_c, base, 0.0)
        except Exception:
            return

        self._refresh_rates_display()

        def fetch_new():
            fetched = _api_fetch(from_c)
            if fetched and base in fetched:
                self._live_rates.setdefault(from_c, {}).update(fetched)
                try:
                    pairs = self.repo.get_exchange_rates(self.user["id"])
                    pair  = next((p for p in pairs if p["from_currency"] == from_c), None)
                    if pair:
                        self.repo.update_exchange_rate(pair["id"], fetched[base])
                except Exception:
                    pass
            try:
                self.after(0, self._refresh_rates_display)
            except Exception:
                pass

        threading.Thread(target=fetch_new, daemon=True).start()

    def _on_history_click(self, row: object) -> None:
        if self._transfer_dialog is not None and self._transfer_dialog.winfo_exists():
            self._transfer_dialog.focus_force()
            return
        self._transfer_dialog = ConversionTransferDialog(self, row, self._on_transfer_confirmed)

    def _on_transfer_confirmed(self, row: object) -> None:
        try:
            cat_id = self.repo.get_or_create_system_category(
                self.user["id"], t("converter.category_name"), 1
            )
            desc = f"{row['from_currency']} → {row['to_currency']}"
            self.repo.save_transaction(
                self.user["id"], None, cat_id, 1,
                float(row["to_amount"]), desc,
            )
        except Exception:
            pass
