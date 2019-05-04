"""Fucntions and data for estimating taxes outside the income tax system.
   Examples include value added tax, financial transaction tax, and carbon tax."""

import numpy as np
import pandas as pd
import taxcalc_helpers as tch

# Source: https://www.taxpolicycenter.org/briefing-book/who-would-bear-burden-vat
VAT_INCIDENCE = pd.Series(
        index=[-1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 99.9],
        data=[3.9, 3.9, 3.6, 3.6, 3.6, 3.6, 3.6, 3.4, 3.4, 3.2, 2.8, 2.5, 2.5])
VAT_INCIDENCE /= 100

# Source: Table 5 in https://www.treasury.gov/resource-center/tax-policy/tax-analysis/Documents/WP-115.pdf
CARBON_TAX_INCIDENCE = pd.Series(
        index=[-1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 99.9],
        data=[0.8, 1.2, 1.4, 1.5, 1.6, 1.7, 1.8, 1.8, 1.8, 1.8, 1.6, 1.4, 0.7])
CARBON_TAX_INCIDENCE /= 100

# Source: Figure 1 in https://www.taxpolicycenter.org/sites/default/files/alfresco/publication-pdfs/2000587-financial-transaction-taxes.pdf
FTT_INCIDENCE = pd.Series(
        index=[-1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 99.9],
        data=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.3, 0.4, 0.8, 1.0])
FTT_INCIDENCE /= 100


def add_custom_tax(df, segment_income, w, base_income, incidence,
                   name, total=None):
    """Add a custom tax based on incidence analysis driven by percentiles.

    Args:
        df: DataFrame.
        segment_income: Income measure used to segment tax units into quantiles.
        w: Weight used to segment into quantiles (either s006 or XTOT_m).
        base_income: Income measure by which incidence is multiplied to estimate
            liability.
        incidence: pandas Series indexed on the floor of an income percentile,
            with values for the tax rate.
        name: Name of the column to add.
        total: Total amount the tax should generate. If not provided, liabilities
            are calculated only based on the incidence schedule.

    Returns:
        Nothing. Adds the column name to df representing the tax liability.
        df is also sorted by segment_income.
    """
    df.sort_values(segment_income, inplace=True)
    income_percentile = 100 * df[w].cumsum() / df[w].sum()
    tu_incidence = incidence.iloc[
        pd.cut(income_percentile,
               # Add a right endpoint. Should be 100 but sometimes a decimal gets added.
               bins=incidence.index.tolist() + [101],
               labels=False)].values
    df[name] = np.maximum(0, tu_incidence * df[base_income])
    if total is not None:
        initial_total = tch.weighted_sum(df, name)
        df[name] *= total / initial_total
    

def add_vat(df,
            segment_income='tpc_eci',
            w='XTOT_m',
            base_income='aftertax_income',
            incidence=VAT_INCIDENCE,
            name='vat',
            total=None):
    """Add value added tax based on incidence estimate from Tax Policy Center.
    
    Args:
        df: DataFrame with columns for tpc_eci, XTOT_m, and aftertax_income.
        Other arguments: Args to add_custom_tax with VAT defaults.

    Returns:
        Nothing. Adds vat to df.
        df is also sorted by tpc_eci.
    """
    add_custom_tax(df, segment_income, w, base_income, incidence, name, total)


def add_carbon_tax(df,
                   segment_income='tpc_eci',
                   w='XTOT_m',
                   base_income='aftertax_income',
                   incidence=CARBON_TAX_INCIDENCE,
                   name='carbon_tax',
                   total=None):
    """Add carbon tax based on incidence estimate from the US Treasury Department.
    
    Args:
        df: DataFrame with columns for tpc_eci, XTOT_m, and aftertax_income.
        Other arguments: Args to add_custom_tax with VAT defaults.

    Returns:
        Nothing. Adds carbon_tax to df.
        df is also sorted by tpc_eci.
    """
    add_custom_tax(df, segment_income, w, base_income, incidence, name, total)

    
def add_ftt(df,
            segment_income='tpc_eci',
            w='XTOT_m',
            base_income='aftertax_income',
            incidence=FTT_INCIDENCE,
            name='ftt',
            total=None):
    """Add financial transaction tax based on incidence estimate from Tax Policy Center.
    
    Args:
        df: DataFrame with columns for tpc_eci, XTOT_m, and aftertax_income.
        Other arguments: Args to add_custom_tax with VAT defaults.

    Returns:
        Nothing. Adds ftt to df.
        df is also sorted by tpc_eci.
    """
    add_custom_tax(df, segment_income, w, base_income, incidence, name, total)