import streamlit as st
import pandas as pd
from App.utils.data_process import TextProcessor


class DataSimilarityProcessor:
    def __init__(self, text_processor: TextProcessor):
        """
        Initialise le processeur de similarité de données.
        
        Args:
            text_processor (TextProcessor): Processeur de texte
        """
        self.text_processor = text_processor

    # @staticmethod
    # @st.cache_data
    def remove_country_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Supprime la colonne de pays du DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame à traiter
        
        Returns:
            pd.DataFrame: DataFrame sans colonne de pays
        """
        country_columns = ["Country", "COUNTRY_KEY", "COUNTRY"]
        for col in country_columns:
            if col in df.columns:
                return df.drop(col, axis=1)
        return df

    def add_text_similarity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajoute des mesures de similarité textuelle au DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame d'entrée
        
        Returns:
            pd.DataFrame: DataFrame avec mesures de similarité
        """
        # Nettoyer les descriptions d'articles
        df["ITEM_DESC_before_clean"] = df["ITEM_DESC_original"].apply(
            self.text_processor.clean_text
        )
        df["ITEM_DESC_after_clean"] = df["ITEM_DESC_updated"].apply(
            self.text_processor.clean_text
        )

        # Supprimer les mots vides
        for col in ["ITEM_DESC_before_clean", "ITEM_DESC_after_clean"]:
            df[col] = df[col].apply(self.text_processor.remove_stop_words)

        # Standardiser le texte
        for col in ["ITEM_DESC_before_clean", "ITEM_DESC_after_clean"]:
            df[col] = df[col].apply(self.text_processor.standardize_text)

        # Calculer la similarité cosinus
        df["Cosine_Similarity"] = df.apply(
            lambda row: self.text_processor.calculate_cosine_similarity(
                row["ITEM_DESC_after_clean"], row["ITEM_DESC_before_clean"]
            ),
            axis=1,
        )

        return df
