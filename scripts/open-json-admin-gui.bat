@echo off
setlocal EnableExtensions
set "SCRIPT=%~dp0json_admin_gui.py"
set "PYTHONW="

for %%V in (313 312 311 310 39) do (
  if exist "%LocalAppData%\Programs\Python\Python%%V\pythonw.exe" (
    set "PYTHONW=%LocalAppData%\Programs\Python\Python%%V\pythonw.exe"
    goto run_pythonw
  )
)

for %%V in (313 312 311 310 39) do (
  if exist "%ProgramFiles%\Python%%V\pythonw.exe" (
    set "PYTHONW=%ProgramFiles%\Python%%V\pythonw.exe"
    goto run_pythonw
  )
)

for %%V in (313 312 311 310 39) do (
  if exist "%ProgramFiles(x86)%\Python%%V\pythonw.exe" (
    set "PYTHONW=%ProgramFiles(x86)%\Python%%V\pythonw.exe"
    goto run_pythonw
  )
)

for /f "delims=" %%P in ('where pythonw 2^>nul') do (
  echo %%P | find /I "WindowsApps" >nul
  if errorlevel 1 (
    set "PYTHONW=%%P"
    goto run_pythonw
  )
)

for /f "delims=" %%P in ('where python 2^>nul') do (
  echo %%P | find /I "WindowsApps" >nul
  if errorlevel 1 (
    start "" "%%P" "%SCRIPT%"
    exit /b 0
  )
)

echo Python 3 was not found on this computer.
echo Please install Python from python.org first,
echo then run this launcher again.
echo.
echo Suggested command after installation:
echo python "%SCRIPT%"
pause
exit /b 1

:run_pythonw
start "" "%PYTHONW%" "%SCRIPT%"
exit /b 0
