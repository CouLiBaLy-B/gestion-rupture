import streamlit as st
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Callable
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem.snowball import FrenchStemmer


class TextProcessor:
    def __init__(self, dictionnaire: dict, liste_stopword: List[str]):
        """
        Initialise le processeur de texte avec un dictionnaire de standardisation et une liste de mots à supprimer.
        
        Args:
            dictionnaire (dict): Dictionnaire de standardisation des mots
            liste_stopword (List[str]): Liste des mots à supprimer
        """
        self.dictionnaire = dictionnaire
        self.liste_stopword = [str(item) for item in liste_stopword]
        self.en_stemmer = PorterStemmer()
        self.fr_stemmer = FrenchStemmer()

    def clean_text(self, text: str) -> str:
        """
        Nettoie et normalise le texte.
        
        Args:
            text (str): Texte à nettoyer
        
        Returns:
            str: Texte nettoyé
        """
        text = text.lower().strip()
        text = text.replace("'", " ").replace("/", " ")
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub("[^A-Za-z ,éêèîôœàâ]+", " ", text)
        return text

    def remove_stop_words(self, text: str) -> str:
        """
        Supprime les mots vides en anglais et en français.
        
        Args:
            text (str): Texte à traiter
        
        Returns:
            str: Texte sans mots vides
        """
        en_stops = set(stopwords.words("english") + self.liste_stopword)
        fr_stops = set(stopwords.words("french") + self.liste_stopword)

        cleaned_words = []
        for ingredient in text.split(" "):
            cleaned_ingredient = " ".join(
                [word for word in ingredient.split(" ") 
                if word.lower() not in en_stops and word.lower() not in fr_stops]
            )
            cleaned_words.append(cleaned_ingredient)

        return " ".join(cleaned_words)

    def standardize_text(self, text: str) -> str:
        """
        Standardise les mots selon le dictionnaire.
        
        Args:
            text (str): Texte à standardiser
        
        Returns:
            str: Texte standardisé
        """
        words = text.split(" ")
        standardized_words = [
            self.dictionnaire.get(word, word) for word in words
        ]
        return " ".join(standardized_words)

    def stem_text(self, text: str, language: str = 'english') -> str:
        """
        Applique la racinisation (stemming) au texte.
        
        Args:
            text (str): Texte à raciniser
            language (str, optional): Langue de racinisation. Defaults to 'english'.
        
        Returns:
            str: Texte racinisé
        """
        stemmer = self.en_stemmer if language == 'english' else self.fr_stemmer
        words = text.split(" ")
        stemmed_words = [stemmer.stem(word) for word in words]
        return " ".join(stemmed_words)

    @staticmethod
    def calculate_cosine_similarity(text1: str, text2: str) -> float:
        """
        Calcule la similarité cosinus entre deux textes.
        
        Args:
            text1 (str): Premier texte
            text2 (str): Deuxième texte
        
        Returns:
            float: Similarité cosinus
        """
        vectorizer = CountVectorizer()
        vectors = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(vectors[0], vectors[1])
        return similarity[0][0]