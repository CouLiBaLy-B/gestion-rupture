import pandas as pd
import numpy as np
import streamlit as st
from typing import Tuple, List
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)


def filter_dataframe(df: pd.DataFrame, key: str = "filter_dataframe_on") -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns
    Args:
        df (pd.DataFrame): Original dataframe
        key (str): Unique key for Streamlit widgets
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters", key=key + "checkbox")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col], format="%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect(
            "Filter dataframe on", df.columns, key=key + "multiselect"
        )

        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")

            # Treat columns with < 10 unique values as categorical
            if is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]

            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]

            else:
                distinct_elements = sorted(df[column].unique())
                if len(distinct_elements) > 0:
                    # Convert distinct_elements to list to ensure proper handling
                    distinct_elements = list(distinct_elements)
                    # Use the first element as default only if it exists
                    default_value = [distinct_elements[0]] if distinct_elements else []
                    user_cat_input = right.multiselect(
                        f"Values for {column}",
                        distinct_elements,
                        default=default_value,
                    )
                    if user_cat_input:
                        df = df[df[column].isin(user_cat_input)]

    return df


def filter_by_country_and_proportion(
    merged_data: pd.DataFrame,
    min_countries: int,
    min_proportion: float,
    product_id_col: str,
) -> pd.DataFrame:
    """
    Filter the merged data based on minimum number of countries and proportion.

    Args:
    merged_data (pd.DataFrame): Merged dataframe
    min_countries (int): Minimum number of countries required
    min_proportion (float): Minimum proportion required
    product_id_col (str): Name of the product ID column

    Returns:
    pd.DataFrame: Filtered dataframe
    """
    filtered_data = merged_data[
        (merged_data["Proportion"] >= min_proportion)
        & (merged_data["total_by_product"] >= min_countries)
    ]
    product_keys = filtered_data[product_id_col].unique()
    return merged_data[merged_data[product_id_col].isin(product_keys)]


def filter_data_with_valid_keys(
    data: pd.DataFrame,
    product_id_col: str,
    class_id_col: str,
    min_product_id_length: int,
    no_valid_product_desc: List[str],
    valid_class_id_prefixes: List[str],
) -> pd.DataFrame:
    """
    Filter the dataframe based on product ID length and class ID prefixes.

    Args:
    data (pd.DataFrame): Input dataframe
    product_id_col (str): Name of the product ID column
    class_id_col (str): Name of the class ID column
    min_product_id_length (int): Minimum length for product IDs
    no_valid_product_desc (List[str]): List of invalid product descriptions
    valid_class_id_prefixes (List[str]): List of invalid prefixes for class IDs

    Returns:
    pd.DataFrame: Filtered dataframe
    """

    # Initialize filtered data with the input dataframe
    filtered_data = data.copy()

    # Filter product IDs by length
    filtered_data = filtered_data[filtered_data[product_id_col].str.len() > min_product_id_length]
    # Filter product descriptions if no_valid_product_desc is not empty
    if no_valid_product_desc[0] != "":

        desc_col = class_id_col[:-3] + "DESC"
        if desc_col in data.columns:
            filtered_data = filtered_data[
                ~filtered_data[desc_col].str.contains('|'.join(no_valid_product_desc), case=False, na=False)
            ]

    # Filter class IDs if valid_class_id_prefixes is not empty
    if valid_class_id_prefixes[0] != "":
        filtered_data = filtered_data[
            ~filtered_data[class_id_col].str[0].isin(valid_class_id_prefixes)
        ]

    return filtered_data
