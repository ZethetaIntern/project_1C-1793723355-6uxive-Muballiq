@echo off
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python src\pipeline.py
streamlit run app.py
pause
