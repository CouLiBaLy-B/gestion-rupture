import streamlit as st
from App.class_input_box.input_box import InputsBox
from App.utils.merge_dataframe import merge_and_update_classification, finalize_country_group_merge
from App.functions_rupture.functions_gestion import (
    create_country_product_matrix,
    process_country_priority,
)
from App.utils.data_process import TextProcessor
from App.utils.data_similarity import DataSimilarityProcessor
from App.utils.standadisation import dictionnaire, liste_stopword
from App.utils.data_display import display_data, display_data_refbem
from App.utils.filter_dataframe import (
    filter_dataframe,
    filter_data_with_valid_keys,
    filter_by_country_and_proportion,
)
import hydralit_components as hc


over_theme = {
    "txc_inactive": "white",
    "menu_background": "#dcdcdc",
    "txc_active": "Black",
    "option_active": "#1587EA",
}

font_fmt = {"font-class": "h1", "font-size": "100%", "color": "black"}

def config_page():
    st.set_page_config(
        page_title="Gestion des ruptures",
        page_icon="images/Carrefour_logo.png",
        initial_sidebar_state="collapsed",
        layout="wide",
    )
    hide_streamlit_style = """
        <style>
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def display_filters(input_box):
    col1, col2 = st.columns(2)
    with col1:
        product_id = input_box.get_product_id()
        no_valid_product_desc = input_box.valid_class_desc()
    with col2:
        class_id = input_box.get_class_id()
        valid_class_id = input_box.valid_class_id()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nb_countries = input_box.get_number_countries()
    with col2:
        proportion = input_box.get_proportion()
    with col3:
        min_product_id = input_box.valid_produict_id()
    with col4:
        show_proportion = input_box.show_proportion()

    return (
        product_id,
        class_id,
        min_product_id,
        valid_class_id,
        nb_countries,
        proportion,
        show_proportion,
        no_valid_product_desc
    )


text_processor = TextProcessor(dictionnaire=dictionnaire, liste_stopword=liste_stopword)
data_processor = DataSimilarityProcessor(text_processor)



def process_data(
    data,
    product_id,
    class_id,
    min_product_id,
    valid_class_id,
    nb_countries,
    proportion,
    show_proportion,
    no_valid_product_desc
):
    data = filter_data_with_valid_keys(data, product_id, class_id, min_product_id, no_valid_product_desc, valid_class_id)

    Country, merged = create_country_product_matrix(data, str(product_id), class_id)

    data_with_pro = finalize_country_group_merge(merged, Country, product_id, class_id)

    if show_proportion:
        st.markdown(f"""
        ## <font color='blue'>Data with proportion</font>
        """, unsafe_allow_html=True)
        display_data(data_with_pro,  key ="1")


    st.markdown(f"""
    ## <font color='blue' center>The data below is filtered as follows:</font>
    
    - Number of countries greater than or equal to **{nb_countries}**
    - The proportion with the highest **{class_id}** is greater than or equal to **{proportion}**
    """, unsafe_allow_html=True)
    data_countries_ratio = filter_by_country_and_proportion(
        data_with_pro, nb_countries, proportion, product_id
    )
    if data_countries_ratio.empty:
        st.markdown(f"""
        ## <font color='red' center>No result for the above criterion</font>
        """, unsafe_allow_html=True)
    else:
        display_filtered_data(data, data_countries_ratio, product_id, class_id)
    data_not_codify = data_with_pro[~data_with_pro.isin(data_countries_ratio)].copy()
    display_country_priority(data_not_codify, data, product_id, class_id)


def display_filtered_data(data, data_countries_ratio, product_id, class_id):
    df = data_processor.remove_country_column(data_countries_ratio)
    max_number_index = df.groupby(product_id)["count"].idxmax()
    df_max_number = df.loc[max_number_index]
    df_max_number.drop(["Countries"], axis=1, inplace=True)

    finale_df = merge_and_update_classification(data, df_max_number, product_id, class_id)
    option_data = [
            {"icon": "🆚", "label": "Data without decision-making"},
            {"icon": "🤝", "label": "Data with proposed changes"},
    ]
    # display a horizontal version of the option bar
    option = hc.option_bar(
            option_definition=option_data,
            # title="Que vous voulez faire ?",
            key="PrimaryOption_",
            override_theme=over_theme,
            font_styling=font_fmt,
            horizontal_orientation=True,
        )
    if option == "Data without decision-making":
        display_data(data,  key="2")
    elif option == "Data with proposed changes":
        # display_data(finale_df,  key="3")
        tab3, tab4 = st.tabs(["Data with proposed changes", "Data for Refbem"])
        with tab3:
            display_data(finale_df,  key="4")
        with tab4:
            display_data_refbem(
                finale_df, product_id=product_id, class_id=class_id,  key="5"
            )


def display_country_priority(data_with_pro, data, product_id, class_id):
    st.markdown(f"""
        ## <font color='blue'>Country priority</font>
        """, unsafe_allow_html=True)
    priority_data, df_equa, df_nequa = process_country_priority(data_with_pro, product_id, class_id)

    font_fmt = {"font-class": "h2", "font-size": "100%", "color": "black"}
    option_data = [
            {"icon": "🆚", "label": "More than 2 countries"},
            {"icon": "🤝", "label": "One vs One"},
    ]
    # display a horizontal version of the option bar
    option = hc.option_bar(
            option_definition=option_data,
            # title="Que vous voulez faire ?",
            key="PrimaryOption",
            override_theme=over_theme,
            font_styling=font_fmt,
            horizontal_orientation=True,
            )
    if option == "More than 2 countries":
        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "Data without decision-making",
                "Equality case and more than 1",
                "Cases of inequality",
                "Data with proposed changes more than 2",
            ]
        )
        
        with tab1:
            display_data(priority_data,  key="6")
        with tab2:
            display_data(df_equa, key="7")
        with tab3:
            df_nequa_ = df_nequa[df_nequa.total_by_product.apply(lambda x: int(x) > 2)]
            display_data(df_nequa_, key="8")
        with tab4:
            display_proposed_changes(df_nequa_, data, product_id, class_id)
    elif option == "One vs One":
        display_one_vs_one(df_nequa, data, product_id, class_id)


def display_proposed_changes(df_nequa_, data, product_id, class_id):
    max_poids_index = df_nequa_.groupby(product_id)["Weight"].idxmax()
    df_max_poids = df_nequa_.loc[max_poids_index]
    df_max_poids.drop(["COUNTRY_KEY"], axis=1, inplace=True)
    finale_df_ = merge_and_update_classification(data, df_max_poids, product_id, class_id)
    tab1, tab2 = st.tabs(["Data with proposed changes", "Data for Refbem"])

    with tab1:
        display_data(finale_df_, key="9")
    with tab2:
        display_data_refbem(
            finale_df_, product_id=product_id, class_id=class_id,  key="10"
        )


def display_one_vs_one(df_nequa, data, product_id, class_id):
    df_nequa_1 = df_nequa[df_nequa.total_by_product.apply(lambda x: int(x) == 2)]
    if not df_nequa_1.empty:
        max_poids_index1 = df_nequa_1.groupby(product_id)["Weight"].idxmax()
        df_max_poids1 = df_nequa_1.loc[max_poids_index1]
        df_max_poids1.drop(["COUNTRY_KEY"], axis=1, inplace=True)
        finale_df_1 = data_processor.add_text_similarity(
            merge_and_update_classification(data, df_max_poids1, product_id, class_id)
        )

        tab1, tab2 = st.tabs(["Data with proposed changes", "Data for Refbem"])
        with tab1:
            tab3, tab4 = st.tabs(["Same country", "Not same country"])
            with tab3:
                display_data(
                    finale_df_1[
                        finale_df_1[["COUNTRY_KEY", "Countries"]].apply(
                            lambda x: x[0] in x[1], axis=1
                        )
                    ],
                    key="11"
                )
            with tab4:
                display_data(
                    finale_df_1[
                        finale_df_1[["COUNTRY_KEY", "Countries"]].apply(
                            lambda x: x[0] not in x[1], axis=1
                        )
                    ],
                    key="12"
                )
        with tab2:
            tab3, tab4 = st.tabs(["Same country", "Not same country"])
            with tab3:
                display_data_refbem(
                    finale_df_1[
                        finale_df_1[["COUNTRY_KEY", "Countries"]].apply(
                            lambda x: x[0] in x[1], axis=1
                        )
                    ],
                    product_id=product_id,
                    class_id=class_id,
                    different_country=False, key="13"
                )
            with tab4:
                display_data_refbem(
                    finale_df_1[
                        finale_df_1[["COUNTRY_KEY", "Countries"]].apply(
                            lambda x: x[0] not in x[1], axis=1
                        )
                    ],
                    product_id=product_id,
                    class_id=class_id,
                    key="14"
                )
    else:
        st.write("No one vs one case")


def app():
    css = """
    <style>
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #2D3E50;
        }
        .subtitle {
            font-size: 24px;
            font-weight: bold;
            color: #4A6F8A;
        }
        .description {
            font-size: 18px;
            color: #6C8798;
        }
    </style>
    """
    
    # Appliquer les styles CSS
    st.markdown(css, unsafe_allow_html=True)
    
    
    st.markdown("""<h1 style='text-align: center;
                background-color: #1587EA;
                color: #ece5f6'>Gestion des ruptures famille</h1>""",
                unsafe_allow_html=True)

    input_box = InputsBox()
    data = input_box.get_data()

    if data is not None and data.shape[0] != 0:
        st.markdown(f"""
        ## <font color='blue'>Data</font>
        """, unsafe_allow_html=True)
        data.fillna("0", inplace=True)
        st.dataframe(filter_dataframe(data))

        st.markdown(f"""
        ## <font color='blue'>Parameters:</font>
        """, unsafe_allow_html=True)
        (
            product_id,
            class_id,
            min_product_id,
            valid_class_id,
            nb_countries,
            proportion,
            show_proportion,
            no_valid_product_desc
        ) = display_filters(input_box)
        list_product_selected = (
            filter_dataframe(data, "data_filter_by_holding")[product_id].unique().tolist()
        )
        if list_product_selected is not None and len(list_product_selected) > 0:
            data_selected = data[data[product_id].isin(list_product_selected)]
        else:
            st.warning("No addictionnal filter selecting")
            data_selected = data.copy()

        # Modify the RUN button to set session state
        if st.button("RUN", key="run_button",  type="primary"):
            st.session_state.run_clicked = True

        try:
            # Only process and display results when run_clicked is True
            if st.session_state.run_clicked:
                try:
                    process_data(
                        data_selected,
                        product_id,
                        class_id,
                        min_product_id,
                        valid_class_id,
                        nb_countries,
                        proportion,
                        show_proportion,
                        no_valid_product_desc
                    )
                    st.success("Done!", icon="✅")
                    # st.balloons()
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}", icon="🚨")
        except Exception as e:
            pass
    else:
        st.info(
            """Ensure that column names are capitalized and that product_id
            and class_id descriptions are present, as well as a country 
            column.""",
            icon="ℹ️",
        )


if __name__ == "__main__":
    config_page()

    st.sidebar.markdown(
        '<a href="https://docs.google.com/document/d/1WQwr5D87ZHSlBRWQw7KMbBhbEdFS4dlhltFDgZBNP4U/edit?usp=sharing">Documentation utilisateur</a>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<a href="https://docs.google.com/spreadsheets/d/123hVTOFpBT-C6mCnrOBh8fFIhSi8FxiuyHZJAQu8bDc/edit#gid=1220891905">Example of input</a>',
        unsafe_allow_html=True,
    )
    app()
