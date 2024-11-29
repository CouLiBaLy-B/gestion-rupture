import numpy as np
import pandas as pd
import streamlit as st
from App.utils.priorite_pays import dico

# from App.utils.divers_function import data_cleaning_func
import nltk
from typing import Tuple, List

nltk.download("stopwords")


@st.cache_data
def calculate_product_class_matrix(
    data: pd.DataFrame, product_id_col: str, class_id_col: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculate the product-class matrix and total counts per product.

    Args:
    data (pd.DataFrame): Input dataframe
    product_id_col (str): Name of the product ID column
    class_id_col (str): Name of the class ID column

    Returns:
    Tuple[pd.DataFrame, pd.DataFrame]: Total counts per product
    and product-class matrix
    """
    matrix = pd.crosstab(data[product_id_col], data[class_id_col])
    total_by_product = matrix.sum(axis=1)

    products_with_multiple_classes = total_by_product[total_by_product > 1].index
    filtered_data = data[data[product_id_col].isin(products_with_multiple_classes)]
    matrix = pd.crosstab(filtered_data[product_id_col], filtered_data[class_id_col])

    total_by_product = matrix.sum(axis=1)
    total_by_product_df = pd.DataFrame(
        {
            product_id_col: total_by_product.index,
            "total_by_product": total_by_product.values,
        }
    )

    return total_by_product_df, matrix


@st.cache_data
def create_sparse_matrix(
    matrix: pd.DataFrame, product_id_col: str, class_id_col: str
) -> pd.DataFrame:
    """
    Create a sparse matrix representation from the product-class matrix.

    Args:
    matrix (pd.DataFrame): Product-class matrix
    product_id_col (str): Name of the product ID column
    class_id_col (str): Name of the class ID column

    Returns:
    pd.DataFrame: Sparse matrix representation
    """
    stacked = matrix.stack()
    non_zero = stacked[stacked != 0]
    sparse_matrix = pd.DataFrame(
        {
            product_id_col: non_zero.index.get_level_values(0).astype(str),
            class_id_col: non_zero.index.get_level_values(1).astype(str),
            "count": non_zero.values,
        }
    )
    return sparse_matrix


@st.cache_data
def create_country_product_matrix(
    data: pd.DataFrame, product_id_col: str, class_id_col: str
) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Process the data to create a new dataset with country groups and merged information.

    Args:
        data (pd.DataFrame): Input dataframe
        product_id_col (str): Name of the product ID column
        class_id_col (str): Name of the class ID column

    Returns:
        Tuple[pd.Series, pd.DataFrame]: Country groups and merged dataframe
    """
    total_by_product_df, matrix = calculate_product_class_matrix(data, product_id_col, class_id_col)
    sparse_matrix = create_sparse_matrix(matrix, product_id_col, class_id_col)

    merged_data = pd.merge(sparse_matrix, total_by_product_df, on=[product_id_col])
    merged_data["Proportion"] = merged_data["count"] / merged_data["total_by_product"]

    final_merged = merged_data.merge(
        data,
        left_on=[class_id_col, product_id_col],
        right_on=[class_id_col, product_id_col],
    )

    # Flexible country column detection
    country_columns = ["Country", "COUNTRY_KEY", "COUNTRY"]
    country_col = next((col for col in country_columns if col in final_merged.columns), None)

    if country_col is None:
        raise ValueError("No country column found in the dataset")

    country_groups = final_merged.groupby([class_id_col, product_id_col])[country_col].agg(
        lambda x: x.tolist()
    )

    return country_groups, final_merged


def process_country_priority(
    merged_data: pd.DataFrame,
    product_id_col: str,
    class_id_col: str
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Process the merged data based on country priority.

    Args:
    merged_data (pd.DataFrame): Merged dataframe
    product_id_col (str): Name of the product ID column
    class_id_col (str): Name of the class ID column

    Returns:
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Processed dataframes
    (all, equal weight, non-equal weight)
    """
    data = merged_data[
        (merged_data.total_by_product >= 2)
    ]
    product_keys = data[product_id_col].unique()
    df = merged_data[merged_data[product_id_col].isin(product_keys)]

    def calculate_weight(row):
        class_id = row[class_id_col]
        countries = row["Countries"]
        
        return sum(
            dico[country]
            if int(class_id) !=0
            else 0
            for country in countries
        )

    # Appliquer la pondération
    df["Weight"] = df.apply(calculate_weight, axis=1)
    # Identifier les sous-classes dupliquées par produit et poids
    duplicated_subclass = df.duplicated(subset=[product_id_col, "Weight"], keep=False)
    df_equal = df[duplicated_subclass & (df.Proportion == 0.5)]
    df_not_equal = df[~df.isin(df_equal)].dropna()

    return df, df_equal, df_not_equal



def process_non_equal_data(
    df_not_equal: pd.DataFrame, product_id_col: str, class_id_col: str
) -> pd.DataFrame:
    """
    Process data with non-equal weights, selecting the classification with
    the highest weight.

    Args:
    df_not_equal (pd.DataFrame): Dataframe with non-equal weights
    product_id_col (str): Name of the product ID column
    class_id_col (str): Name of the class ID column

    Returns:
    pd.DataFrame: Processed dataframe with selected classifications
    """
    df_multi_country = df_not_equal[df_not_equal.Countries.apply(len) > 1]
    max_weight_index = df_multi_country.groupby(product_id_col)["Weight"].idxmax()

    df_multi_country.loc[:, [class_id_col, f"{class_id_col[:-4]}_DESC"]] = df_multi_country.loc[
        max_weight_index, [class_id_col, f"{class_id_col[:-4]}_DESC"]
    ].values

    df_duplicate = df_multi_country.copy()
    df_duplicate.Countries = df_duplicate.Countries.str.join(",")

    new_df = (
        df_duplicate.explode("Countries").rename(columns={"Countries": "Country"}).drop_duplicates()
    )

    return new_df

