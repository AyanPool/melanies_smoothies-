# Import python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# -------------------------------
# TITLE
# -------------------------------
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# -------------------------------
# USER INPUT
# -------------------------------
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# -------------------------------
# SNOWFLAKE CONNECTION
# -------------------------------
session = Session.builder.configs(st.secrets["snowflake"]).create()

# -------------------------------
# FETCH FRUIT OPTIONS FROM SNOWFLAKE
# -------------------------------
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col('FRUIT_NAME'), col('SEARCH_ON'))

fruit_rows = my_dataframe.collect()

# Create mapping: UI name → API name
fruit_dict = {row["FRUIT_NAME"]: row["SEARCH_ON"] for row in fruit_rows}

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    list(fruit_dict.keys()),
    max_selections=5
)

# -------------------------------
# INSERT ORDER INTO SNOWFLAKE
# -------------------------------
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        st.subheader(fruit_chosen + ' Nutrition Information')

        # Use SEARCH_ON for API
        search_value = fruit_dict[fruit_chosen]

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_value}"
        )

        # Display nutrition data
        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Insert into Snowflake
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

# -------------------------------
# DEFAULT API TEST (OPTIONAL)
# -------------------------------
st.header("🍉 Test API (Watermelon)")

smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

st.dataframe(
    data=smoothiefroot_response.json(),
    use_container_width=True
)
