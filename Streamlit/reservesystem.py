import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials
import altair as alt
import smtplib, ssl
from email.mime.text import MIMEText
from gspread.exceptions import APIError

#ページコンフィグ
st.set_page_config(
     page_title="機材予約システム",
     page_icon="❌",
     initial_sidebar_state="collapsed",
 )

st.title('GHK 機材予約システム')
st.markdown("## **:red[🔔お知らせ]**")
st.markdown("Nコン期間は別で機材を管理するそうです")
st.markdown("奥野or今田まで連絡を。")
