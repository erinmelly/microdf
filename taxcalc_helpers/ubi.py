import numpy as np
import pandas as pd
import taxcalc_helpers as tch

def ubi_or_bens(df, ben_cols, max_ubi='max_ubi', ubi='ubi', bens='bens'):
    """Calculates whether a tax unit will take UBI or benefits,
       and adjusts values accordingly.

    Args:
        df: DataFrame.
        ben_cols: List of columns for benefits.
        max_ubi: Column name of the maximum UBI, before accounting
            for benefits. Defaults to 'max_ubi'.
        ubi: Column name to add representing the UBI. Defaults to 'ubi'.
        bens: Column name to add representing total benefits (after adjustment).
            Defaults to 'bens'.

    Returns:
        Nothing. Benefits in ben_cols are adjusted, ubi and bens columns
        are added, and expanded_income and aftertax_income are updated
        according to the net difference.
    """
    total_bens = df[ben_cols].sum(axis=1)
    take_ubi = df[max_ubi] > total_bens
    df[ubi] = np.where(take_ubi, df[max_ubi], 0)
    for ben in ben_cols:
        df[ben] *= np.where(take_ubi, 0, 1)
    df[bens] = df[ben_cols].sum(axis=1)
    # Update expanded and aftertax income.
    diff = df.ubi + df.bens - total_bens
    df.expanded_income += diff
    df.aftertax_income += diff
