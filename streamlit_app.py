# Import python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import pandas as pd
import requests   # ✅ FIX 1: moved import to top

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
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
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

        # ✅ FIX 2: dynamic API call instead of hardcoded watermelon
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}"
        )

        # ✅ FIX 3: show proper dataframe
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

# -------------------------------
# SMOOTHIEFRUIT API SECTION
# -------------------------------
# ✅ FIX 4: correct URL (remove markdown format)
smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

# ✅ FIX 5: correct dataframe usage
st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
