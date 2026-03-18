from dataclasses import dataclass
from typing import Literal

import pandas as pd
from .bek_funcs import exit_yes


@dataclass
class ColSpec:
    col_name: str
    new_col_name: str | None = None
    remove_col: bool = False

    def __post_init__(self):
        self.col_name = self.col_name.strip()


def standardize_columns(
        df: pd.DataFrame,
        col_list: list[ColSpec],
        col_check: Literal["exact", "subset"] | None = None,
        change_case: Literal['upper', 'lower'] | None = None,
        popup: bool = False,
) -> pd.DataFrame:
    """Renames, case-converts, and/or drops DataFrame columns from a spec list.

    Args:
        df (pd.DataFrame): Input DataFrame.
        col_list (list[ColSpec]): Column specifications. Each ``ColSpec`` has:

            * **col_name** *(str, required)* —
              Column name as it appears in ``df``.
            * **new_col_name** *(str | None, optional)* —
              Rename target. ``None`` or ``''`` keeps the original name.
            * **remove_col** *(bool, optional, default* ``False`` *)* —
              ``True`` drops the column; rename is skipped.

            All column name matching is case-insensitive.
        col_check (str | None, optional): Column presence validation applied
            before any changes. Allowed values:

            * ``'exact'``  — df columns must match list exactly; no extras
              on either side
            * ``'subset'`` — every column in the list must be present in df;
              extra df columns are allowed
            * ``None``     — no validation (default)

        change_case (str | None, optional): Case conversion applied to column
            names in all non-removed columns. Allowed values:

            * ``'upper'`` — rename columns to uppercase
            * ``'lower'`` — rename columns to lowercase
            * ``None``    — no conversion (default)

        popup (bool, optional): Controls error presentation when a
            ``col_check`` constraint is violated. Defaults to ``False``.

            * ``True``  — shows a GUI popup (via ``exit_yes``) describing the
              mismatch, then raises an exception.
            * ``False`` — raises ``ValueError`` directly with no popup.

    Returns:
        pd.DataFrame: New DataFrame with columns standardized per the spec.
            The original ``df`` is not modified.

    Raises:
        ValueError: If ``col_check`` constraints are violated and ``popup=False``.
        Exception: If ``col_check`` constraints are violated and ``popup=True``
            (raised by ``exit_yes`` after showing a GUI popup).
    """
    # Case-insensitive map: lowercase col name → actual col name in df
    df_col_map = {col.strip().lower(): col for col in df.columns}

    requested_lower = {item.col_name.lower() for item in col_list}
    df_lower = set(df_col_map.keys())

    def _fail(msg: str) -> None:
        if popup:
            exit_yes(msg, raise_err=True)
        raise ValueError(msg)

    if col_check == "exact":
        if df_lower != requested_lower:
            _fail(
                f"col_check='exact' failed in standardize_columns.\n\n"
                f"  Expected columns: {sorted(requested_lower)}\n\n"
                f"  Actual columns:   {sorted(df_lower)}\n\n"
                f"  Extra in df:   {sorted(df_lower - requested_lower)}\n"
                f"  Missing:       {sorted(requested_lower - df_lower)}"
            )
    elif col_check == "subset":
        missing = requested_lower - df_lower
        if missing:
            _fail(
                f"col_check='subset' failed in standardize_columns.\n\n"
                f"  Expected columns: {sorted(requested_lower)}\n\n"
                f"  Actual columns:   {sorted(df_lower)}\n\n"
                f"  Missing: {sorted(missing)}"
            )

    df = df.copy()
    rename_map = {}
    cols_to_drop = []

    for item in col_list:
        actual = df_col_map.get(item.col_name.lower())
        if actual is None:
            continue  # not in df; col_check would have raised if that matters

        if item.remove_col:
            cols_to_drop.append(actual)
            continue

        target = item.new_col_name if item.new_col_name else actual
        if change_case == 'upper':
            target = target.upper()
        elif change_case == 'lower':
            target = target.lower()
        if target != actual:
            rename_map[actual] = target

    # Apply change_case to all df columns not already handled by the spec
    if change_case:
        spec_actuals = set(cols_to_drop) | set(rename_map.keys())
        for col in df.columns:
            if col not in spec_actuals:
                new_name = col.upper() if change_case == 'upper' else col.lower()
                if new_name != col:
                    rename_map[col] = new_name

    if rename_map:
        df = df.rename(columns=rename_map)
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)

    return df
