import pandas as pd
from App.utils.add_country import add_country
import streamlit as st
from typing import Tuple, List


def finalize_country_group_merge(
    merged: pd.DataFrame,
    country_groups: pd.Series,
    product_id_col: str,
    class_id_col: str,
) -> pd.DataFrame:
    """
    Finalize the merged data by adding country information and removing
    duplicates.

    Args:
    merged (pd.DataFrame): Merged dataframe
    country_groups (pd.Series): Series containing country groups
    product_id_col (str): Name of the product ID column
    class_id_col (str): Name of the class ID column

    Returns:
    pd.DataFrame: Finalized merged dataframe
    """
    try:
        merged["Countries"] = merged.apply(
            lambda row: add_country(row[1], row[0], country_groups),
            axis=1,
        )
        merged["Countries"] = merged["Countries"].apply(tuple)
        final_merged = merged.drop_duplicates(subset=[product_id_col, class_id_col, "Countries"])
    except Exception as e:
        st.warning(f"An error occurred: {e}")
        final_merged = None
    return final_merged



def merge_and_update_classification(
    original_data: pd.DataFrame,
    updated_data: pd.DataFrame,
    product_column: str,
    classification_column: str,
) -> pd.DataFrame:
    """
    Merge two DataFrames and update the classification based on the updated_data.
    Retains only rows where the classification has changed and aligns common columns
    (except the product column) side by side.

    Args:
    original_data (pd.DataFrame): The original DataFrame containing existing data.
    updated_data (pd.DataFrame): DataFrame containing updated classifications.
    product_column (str): Column name used as the product identifier.
    classification_column (str): Column name for the classification to be updated.

    Returns:
    pd.DataFrame: A DataFrame containing rows where the classification was updated,
                with common columns (excluding product column) aligned side by side.
    """
    # Extract unique product IDs from the updated data
    updated_product_ids = updated_data[product_column].unique()

    # Filter original data to include only products present in the updated data
    filtered_original_data = original_data[original_data[product_column].isin(updated_product_ids)]

    # Preserve the original classification
    original_classification_column = f"original_{classification_column}"
    filtered_original_data[original_classification_column] = filtered_original_data[
        classification_column
    ]

    # Merge the original and updated data on the product column
    merged_data = pd.merge(
        filtered_original_data,
        updated_data,
        on=[product_column],
        how="inner",
        suffixes=("_original", "_updated"),
        indicator=True,
    )

    # Update classification: retain updated value or fallback to the original
    merged_data[classification_column] = merged_data[f"{classification_column}_updated"].fillna(
        merged_data[original_classification_column]
    )

    # Select rows where the classification has changed
    classification_updated = merged_data[
        merged_data[f"{classification_column}_original"] != merged_data[classification_column]
    ]

    # Identify common columns excluding the product column
    common_columns = [
        col
        for col in set(original_data.columns).intersection(updated_data.columns)
        if col != product_column
    ]

    # Align common columns side by side
    aligned_columns = []
    for col in common_columns:
        aligned_columns.extend([f"{col}_original", f"{col}_updated"])

    # Reorganize columns in the final DataFrame
    result_columns = (
        [product_column]
        + aligned_columns
        + [
            col
            for col in classification_updated.columns
            if col not in aligned_columns and col != "_merge" and col != product_column
        ]
    )
    result_data = classification_updated[result_columns]

    return result_data
