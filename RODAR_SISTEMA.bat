@echo off
title Sistema de Dados - KaBuM
echo ======================================================
echo   INICIALIZANDO INTERFACE DE DADOS (Streamlit)
echo ======================================================
echo.
echo Verificando dependencias...
:: Opcional: pip install -r requirements.txt
streamlit run app.py
pause
