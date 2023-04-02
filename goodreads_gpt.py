import openai
import streamlit as st

# Initialize the SessionState
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

# Create a Streamlit sidebar input for the OpenAI API key
api_key = st.sidebar.text_input("Enter your OpenAI API key")

# Check if the API key is valid and set the authorization header for OpenAI requests
if api_key:
    openai.api_key = api_key
    try:
        models = openai.Model.list()
        st.success("API key is valid!")
        st.session_state.api_key = api_key # Update the SessionState with the new API key
    except openai.Error as e:
        st.error("Error: {}".format(e))
else:
    st.warning("Please enter your OpenAI API key")

# Retrieve the API key from the SessionState for use in the app
api_key = st.session_state.api_key
