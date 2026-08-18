@echo off
rem Uruchamia panel dowodzenia na localhost (Windows).
rem Cala logika bootstrapu (venv, zaleznosci) siedzi w panel.py.
rem Zmienne srodowiskowe: DASHBOARD_PORT, DASHBOARD_CONFIG,
rem DASHBOARD_PROJECT_ROOT, DASHBOARD_DATA - opis w panel.py.

where python >nul 2>nul
if %errorlevel%==0 (
  python "%~dp0panel.py" %*
  goto :eof
)

where py >nul 2>nul
if %errorlevel%==0 (
  py "%~dp0panel.py" %*
  goto :eof
)

echo Nie znalazlem Pythona. Zainstaluj Python 3.11+ z python.org i zaznacz "Add to PATH".
exit /b 1
