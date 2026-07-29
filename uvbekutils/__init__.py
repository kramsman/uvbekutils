"""uvbekutils — helpers, resolved lazily.

Names are looked up on first use rather than imported here, because Python runs
this file whenever *anything* in the package is touched. Importing eagerly meant
`from uvbekutils.bek_funcs import safe_str` also pulled in `pyautobek`, and with
it PySide6 — which turns a plain terminal script into a macOS GUI app that takes
a dock icon and steals keyboard focus from its own prompts.

Only pyautobek and select_file need Qt; every other submodule is Qt-free. Loading
lazily means Qt arrives only when a dialog is actually used.

Usage is unchanged:

    from uvbekutils import confirm, safe_str      # still works
    from uvbekutils.pyautobek import alert        # still works
"""

import importlib

# public name -> submodule that defines it
_LAZY = {
    # these two import PySide6, so they load Qt when first touched
    "alert":                    "pyautobek",
    "confirm":                  "pyautobek",
    "select_file":              "select_file",

    "list_pick":                "list_pick",
    "sumby_w_totals":           "sumby_w_totals",
    "select_from_list":         "select_from_list",
    "ColSpec":                  "standardize_columns",
    "standardize_columns":      "standardize_columns",

    "safe_str":                 "bek_funcs",
    "scroll_box":               "bek_funcs",
    "is_number":                "bek_funcs",
    "exit_yes":                 "bek_funcs",
    "exit_yes_no":              "bek_funcs",
    "clean_field":              "bek_funcs",
    "autosize_xls_cols":        "bek_funcs",
    "load_workbook_w_filepath": "bek_funcs",
    "wb_path":                  "bek_funcs",
    "wb_name":                  "bek_funcs",
    "setup_loguru":             "bek_funcs",
    "bad_file_exit":            "bek_funcs",
    "bad_path_exit":            "bek_funcs",
    "bad_path_create":          "bek_funcs",
    "calling_func":             "bek_funcs",
    "find_header_row_in_file":  "bek_funcs",
    "read_file_to_df":          "bek_funcs",
    "check_ws_headers":         "bek_funcs",
    "convert_bool":             "bek_funcs",
    "exe_file":                 "bek_funcs",
    "exe_path":                 "bek_funcs",
    "bek_write_excel":          "bek_funcs",
    "bek_excel_titles":         "bek_funcs",
    "conc_addr":                "bek_funcs",
    "conc_addr_desc":           "bek_funcs",
    "conc_addr_remove_desc":    "bek_funcs",
}

__all__ = sorted(_LAZY)


def __getattr__(name):
    """PEP 562 — resolve a public name to its submodule on first access."""
    if name in _LAZY:
        value = getattr(importlib.import_module(f".{_LAZY[name]}", __name__), name)
        globals()[name] = value          # cache so this runs once per name
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return __all__
