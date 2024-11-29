import streamlit as st
import pandas as pd
import numpy as np


def display_data(df: pd.DataFrame, key: str = "0") -> None:
    """
    Display a pandas DataFrame with a title and a data editor.
    """
    if df.empty:
        st.write("No result for the above criterion")
    else:
        df = df.copy()
        df["Evaluation"] = True
        st.data_editor(df, key=key)


def display_data_refbem(
    df: pd.DataFrame,
    product_id: str,
    class_id: str,
    different_country: bool = True,
    key: str = "0"
) -> None:
    """
    Display a pandas DataFrame with a title and a data editor.
    """
    if df.empty:
        st.write("No result for the above criterion")
    else:
        # st.subheader(title)
        if different_country:
            df_refbem = df[["COUNTRY_KEY", "ITEM_KEY_original", product_id, class_id + "_updated"]]
            df_refbem = df_refbem.rename(
                columns={"ITEM_KEY_original": "ITEM_KEY", class_id + "_updated": "class_id"}
            )
            st.data_editor(df_refbem, key=key)
        else:
            df_refbem = df[
                [
                    "COUNTRY_KEY",
                    "ITEM_KEY_updated",
                    "ITEM_KEY_original",
                    product_id,
                    class_id + "_updated",
                    class_id + "_original",
                ]
            ]
            df_refbem["ITEM_KEY"] = df_refbem[["ITEM_KEY_updated", "ITEM_KEY_original"]].apply(
                lambda x: x[0] if "R" in x[1] else x[1], axis=1
            )
            df_refbem[class_id] = df_refbem[
                ["ITEM_KEY_original", class_id + "_updated", class_id + "_original"]
            ].apply(lambda x: x[1] if "R" in x[0] else x[2], axis=1)
            st.data_editor(
                df_refbem[
                    [
                        "COUNTRY_KEY",
                        "ITEM_KEY_original",
                        product_id,
                        class_id + "_updated",
                        class_id + "_original",
                    ]
                ],
                key=key,
            )
