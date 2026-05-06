@echo off
echo ==========================================
echo   DASHBOARD PRIX INTELLIGENCE v2.0
echo   Kitea . Jumia . Ikea
echo ==========================================
echo.
echo Activation environnement...
call conda activate prix_ecommerce

echo.
echo Lancement du Dashboard...
echo Ouvre ton navigateur sur : http://localhost:8501
echo.
cd /d %~dp0
streamlit run dashboard/app.py
pause
