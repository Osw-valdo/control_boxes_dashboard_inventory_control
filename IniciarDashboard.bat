@echo off

title Control Box Dashboard

cd /d C:\CONTROLBOXES_V2

call .venv\Scripts\activate.bat

start "" http://localhost:8501

streamlit run app.py