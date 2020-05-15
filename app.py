import streamlit as st

import requests

from SessionState import get

from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")
PWD: Secret = config("PASSWORD", cast=Secret)
API_KEY: Secret = config("API_KEY", cast=Secret)

def check_password():
    session_state = get(password='')

    if session_state.password != str(PWD):
        pwd_placeholder = st.sidebar.empty()
        pwd = pwd_placeholder.text_input("Password:", value="", type="password")
        session_state.password = pwd
        if session_state.password == str(PWD):
            pwd_placeholder.empty()
            return True
        elif session_state.password != '':
            st.error("the password you entered is incorrect")
            return False
    else:
        return True

def main():

    st.write("## House price prediction model (example)")

    try:
        response = requests.get("http://restbot.cwerner.ai/api/health/heartbeat")

        # validate response? HearbeatResult.validate(response.json())    
        status = "alive ❤️" if response.json().get('is_alive') else "dead 💔"
        info = f"### Current status   \n🤖 is {status}"
        st.sidebar.info(info)
    except requests.exceptions.ConnectionError:
        status = "not reachable"
        info = f"### Current status   \n🤖 is {status}"
        st.sidebar.warning(info)
        return

    # let user define input
    median_income_in_block = st.number_input('Median income in block', value=8.3252)
    median_house_age_in_block = st.number_input('Median house age in block', value=41)
    average_rooms = st.number_input('Average rooms', value=5, format="%d")
    average_bedrooms = st.number_input('Average bedrooms', value=3)
    population_per_block = st.number_input('Population per block', value=2_000)
    average_house_occupancy = st.number_input('Average house occupancy', value=3)
    block_latitude = st.number_input('Block latitude', value=44)
    block_longitude = st.number_input('Block longitude', value=-150)

    if st.sidebar.button('Call model'):
        response = requests.post(
            "http://restbot.cwerner.ai/api/model/predict",
            json={
                "median_income_in_block":median_income_in_block,
                "median_house_age_in_block":median_house_age_in_block,
                "average_rooms":average_rooms,
                "average_bedrooms":average_bedrooms,
                "population_per_block":population_per_block,
                "average_house_occupancy":average_house_occupancy,
                "block_latitude":block_latitude,
                "block_longitude":block_longitude
            },
            headers={"token": str(API_KEY)}
        )
        
        amount = response.json()["median_house_value"]
        currency = response.json()["currency"]

        if response.status_code == 200:
            st.sidebar.success(f'Prediction: {int(amount)} {currency}')
        else:
            st.sidebar.error(f'An error occured: {response.text}')

def display_info():

    st.info("👈🏻 please authenticate first")

if __name__ == '__main__':
    st.write("# 🤖 RestBOT Control Interface")

    authenticated = check_password()
    if authenticated:
        main()
    else:
        display_info()
