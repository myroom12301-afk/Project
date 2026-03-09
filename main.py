import argparse
import customtkinter as ctk

from pages.home_page import HomePage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Personal Money UI launcher")
    parser.add_argument(
        "page",
        nargs="?",
        default="home",
        choices=["home"],
        help="Page name to run",
    )
    return parser


def main() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    args = build_parser().parse_args()

    if args.page == "home":
        app = HomePage()
        app.mainloop()


if __name__ == "__main__":
    main()
