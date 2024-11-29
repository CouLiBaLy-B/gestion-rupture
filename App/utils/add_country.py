from typing import List


def add_country(produit_id: str, class_id: str, Country) -> List[str]:
    """
    Retrieve the list of countries for a given product ID and class ID.

    Args:
    product_id (str): The product ID
    class_id (str): The class ID
    country_groups (pd.Series): Series containing country groups

    Returns:
    List[str]: List of countries for the given product and class
    """
    return Country.get((produit_id, class_id), [])
