﻿# -*- coding: utf-8 -*-
import streamlit as st

st.set_page_config(page_title="TEST", page_icon="")

st.title(" TEST APP")
st.write("If you see this, Streamlit works!")

name = st.text_input("Your name")
if name:
    st.success(f"Hello {name}!")