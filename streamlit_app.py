import streamlit as st
import requests  # ✅ Fix 3: moved import to top
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import pandas as pd

# title
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
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
# Convert the snowpark dataframe to a pandas dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()

# MULTISELECT
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # ✅ Fix 1: replaced undefined fruit_dict.keys()
    max_selections=5
)

# -------------------------------
# INSERT ORDER INTO SNOWFLAKE
# -------------------------------
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '  # ✅ Fix 2: typo ingredients_sttring → ingredients_string
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )
        st_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # -------------------------------
    # INSERT QUERY
    # -------------------------------
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

# New section to display smoothiefroot nutrition information
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
