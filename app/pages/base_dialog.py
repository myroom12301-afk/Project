import customtkinter as ctk


class BaseDialog(ctk.CTkToplevel):
    def __init__(self, master, width: int, height: int) -> None:
        super().__init__(master)
        self._dlg_w = width
        self._dlg_h = height
        self.title("")
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(fg_color="#0E1726")
        self.lift()
        self.focus_force()
        self.after(50, self._center)
        self.after(50, self.grab_set)
        self.grid_columnconfigure(0, weight=1)

    def _center(self) -> None:
        self.update_idletasks()
        p = self.master.winfo_toplevel()
        x = p.winfo_rootx() + (p.winfo_width() - self._dlg_w) // 2
        y = p.winfo_rooty() + (p.winfo_height() - self._dlg_h) // 2
        self.geometry(f"{self._dlg_w}x{self._dlg_h}+{x}+{y}")
