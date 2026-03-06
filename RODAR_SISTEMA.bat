@echo off
title Sistema de Dados - KaBuM

:: ============================================================
:: Define o caminho do Python (instalado via Microsoft Store)
:: ============================================================
set PYTHON_PATH=C:\Users\daniel.teixeira\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe

:: Navega para a pasta do projeto (caminho local)
cd /d C:\Scripts\PROJETO_CONSOLIDACAO

echo ======================================================
echo   INICIALIZANDO INTERFACE DE DADOS (Streamlit)
echo ======================================================
echo.

:: Instala dependencias automaticamente (caso ainda nao tenha)
echo Verificando dependencias...
"%PYTHON_PATH%" -m pip install -r requirements.txt --quiet
echo.
echo Abrindo interface no navegador...
echo.

:: Roda o Streamlit usando o Python encontrado
"%PYTHON_PATH%" -m streamlit run app.py

pause