import pandas as pd
import streamlit as st


class InputsBox:
    def __init__(self):
        self.data = None
        self.columns = None
        self.product_id = None
        self.class_id = None

    def get_data(self):
        uploaded_file = st.file_uploader(
            "Choose a CSV file with the separator ';' ", type=["csv"]
        )

        if uploaded_file is not None:
            # try :
            self.data = pd.read_csv(
                uploaded_file, dtype=str, sep=";", encoding="latin-1"
            )

            # except :
            #    self.data = pd.read_csv(
            # uploaded_file,dtype=str,
            # sep=";",
            # encoding="utf-8" )

            self.columns = self.data.columns.tolist()
        return self.data

    def valid_produict_id(self) -> int:
        min_len = st.number_input(
            "Minimum len of product_id",
            max_value=25,
            min_value=1,
            value=2,
            key="pp"
        )
        return min_len

    def valid_class_id(self) -> str:
        valid = st.text_input(
            "First element of No valid class_id separed by ;"
        )
        return valid.split(";")

    def valid_class_desc(self) -> str:
        valid = st.text_input(
            "No valid class_desc separed by ;"
        )
        return valid.split(";")

    def get_product_id(self) -> str:
        self.product_id = st.selectbox(
            "product_id (BARCODE)", options=self.columns, key="product_id"
        )
        return self.product_id

    def get_class_id(self) -> str:
        self.class_id = st.selectbox(
            "class_id (WW_CLASS_KEY)", options=self.columns, key="class_id"
        )
        return self.class_id

    def get_countries(self) -> list:
        countries = st.multiselect(
            "Select countries : ",
            tuple(self.data.COUNTRY_KEY.unique()),
            key="countries",
        )
        return countries

    def get_number_countries(self) -> int:
        nb_countries = st.number_input(
            "Number of countries",
            min_value=1,
            max_value=20,
            value=1,
            key="Number of countries",
        )
        return nb_countries

    def get_proportion(self) -> float:
        proportion = st.number_input(
            "Proportion",
            min_value=0.10, max_value=1.00, value=0.75, key="proportion"
        )
        return proportion

    def show_proportion(self) -> bool:
        show_condition = st.checkbox(
            "Show data with ratios ", value=True, key="show_ratio_checkbox"
        )
        return show_condition
