from __future__ import annotations

# code -> {name, symbol}
CURRENCIES: dict[str, dict[str, str]] = {
    "USD": {"name": "US Dollar",          "symbol": "$"},
    "EUR": {"name": "Euro",               "symbol": "€"},
    "GBP": {"name": "British Pound",      "symbol": "£"},
    "JPY": {"name": "Japanese Yen",       "symbol": "¥"},
    "CNY": {"name": "Chinese Yuan",       "symbol": "¥"},
    "CHF": {"name": "Swiss Franc",        "symbol": "Fr"},
    "CAD": {"name": "Canadian Dollar",    "symbol": "CA$"},
    "AUD": {"name": "Australian Dollar",  "symbol": "A$"},
    "NZD": {"name": "New Zealand Dollar", "symbol": "NZ$"},
    "SEK": {"name": "Swedish Krona",      "symbol": "kr"},
    "NOK": {"name": "Norwegian Krone",    "symbol": "kr"},
    "DKK": {"name": "Danish Krone",       "symbol": "kr"},
    "PLN": {"name": "Polish Zloty",       "symbol": "zł"},
    "CZK": {"name": "Czech Koruna",       "symbol": "Kč"},
    "HUF": {"name": "Hungarian Forint",   "symbol": "Ft"},
    "RON": {"name": "Romanian Leu",       "symbol": "lei"},
    "BGN": {"name": "Bulgarian Lev",      "symbol": "лв"},
    "RUB": {"name": "Russian Ruble",      "symbol": "₽"},
    "UAH": {"name": "Ukrainian Hryvnia",  "symbol": "₴"},
    "BYN": {"name": "Belarusian Ruble",   "symbol": "Br"},
    "KZT": {"name": "Kazakh Tenge",       "symbol": "₸"},
    "KGS": {"name": "Kyrgyz Som",         "symbol": "с"},
    "UZS": {"name": "Uzbek Sum",          "symbol": "сум"},
    "TJS": {"name": "Tajik Somoni",       "symbol": "SM"},
    "TMT": {"name": "Turkmen Manat",      "symbol": "T"},
    "AZN": {"name": "Azerbaijani Manat",  "symbol": "₼"},
    "GEL": {"name": "Georgian Lari",      "symbol": "₾"},
    "AMD": {"name": "Armenian Dram",      "symbol": "֏"},
    "MDL": {"name": "Moldovan Leu",       "symbol": "L"},
    "TRY": {"name": "Turkish Lira",       "symbol": "₺"},
    "INR": {"name": "Indian Rupee",       "symbol": "₹"},
    "PKR": {"name": "Pakistani Rupee",    "symbol": "₨"},
    "BDT": {"name": "Bangladeshi Taka",   "symbol": "৳"},
    "NPR": {"name": "Nepalese Rupee",     "symbol": "₨"},
    "LKR": {"name": "Sri Lankan Rupee",   "symbol": "₨"},
    "MYR": {"name": "Malaysian Ringgit",  "symbol": "RM"},
    "SGD": {"name": "Singapore Dollar",   "symbol": "S$"},
    "IDR": {"name": "Indonesian Rupiah",  "symbol": "Rp"},
    "THB": {"name": "Thai Baht",          "symbol": "฿"},
    "PHP": {"name": "Philippine Peso",    "symbol": "₱"},
    "VND": {"name": "Vietnamese Dong",    "symbol": "₫"},
    "KRW": {"name": "South Korean Won",   "symbol": "₩"},
    "HKD": {"name": "Hong Kong Dollar",   "symbol": "HK$"},
    "TWD": {"name": "Taiwan Dollar",      "symbol": "NT$"},
    "MXN": {"name": "Mexican Peso",       "symbol": "MX$"},
    "BRL": {"name": "Brazilian Real",     "symbol": "R$"},
    "ARS": {"name": "Argentine Peso",     "symbol": "AR$"},
    "CLP": {"name": "Chilean Peso",       "symbol": "CL$"},
    "COP": {"name": "Colombian Peso",     "symbol": "CO$"},
    "PEN": {"name": "Peruvian Sol",       "symbol": "S/"},
    "ZAR": {"name": "South African Rand", "symbol": "R"},
    "NGN": {"name": "Nigerian Naira",     "symbol": "₦"},
    "EGP": {"name": "Egyptian Pound",     "symbol": "£"},
    "MAD": {"name": "Moroccan Dirham",    "symbol": "MAD"},
    "SAR": {"name": "Saudi Riyal",        "symbol": "SR"},
    "AED": {"name": "UAE Dirham",         "symbol": "AED"},
    "QAR": {"name": "Qatari Riyal",       "symbol": "QR"},
    "KWD": {"name": "Kuwaiti Dinar",      "symbol": "KD"},
    "BHD": {"name": "Bahraini Dinar",     "symbol": "BD"},
    "ILS": {"name": "Israeli Shekel",     "symbol": "₪"},
}

_DEFAULT_CODE = "USD"


def get_symbol(code: str) -> str:
    return CURRENCIES.get(code, {}).get("symbol", code)


def get_all() -> list[tuple[str, str, str]]:
    """Returns list of (code, name, symbol) sorted by code."""
    return [(code, info["name"], info["symbol"]) for code, info in sorted(CURRENCIES.items())]