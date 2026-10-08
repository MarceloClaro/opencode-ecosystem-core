@echo off
setlocal
set "NGS_ANALYSIS_WORKBENCH_ORIGINAL_PATH=%PATH%"

if defined USERPROFILE set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%USERPROFILE%\bin;%PATH%"
if defined HOME set "PATH=%HOME%\.local\bin;%HOME%\.cargo\bin;%HOME%\bin;%PATH%"
if defined APPDATA set "PATH=%APPDATA%\Python\Scripts;%PATH%"
if defined LOCALAPPDATA set "PATH=%LOCALAPPDATA%\Microsoft\WinGet\Links;%PATH%"

set /p NGS_ANALYSIS_WORKBENCH_PLUGIN_VENV_VERSION=<"%~dp0PLUGIN_VENV_VERSION"
if defined CODEX_HOME (
  set "NGS_ANALYSIS_WORKBENCH_CODEX_HOME=%CODEX_HOME%"
) else if defined USERPROFILE (
  set "NGS_ANALYSIS_WORKBENCH_CODEX_HOME=%USERPROFILE%\.codex"
) else (
  echo NGS Analysis Workbench requires CODEX_HOME or USERPROFILE to store its runtime environment. 1>&2
  exit /b 1
)

set "NGS_ANALYSIS_WORKBENCH_VENV=%NGS_ANALYSIS_WORKBENCH_CODEX_HOME%\cache\ngs-analysis-workbench\venvs\%NGS_ANALYSIS_WORKBENCH_PLUGIN_VENV_VERSION%"
set "NGS_ANALYSIS_WORKBENCH_PYTHON=%NGS_ANALYSIS_WORKBENCH_VENV%\Scripts\python.exe"
set "NGS_ANALYSIS_WORKBENCH_READY=%NGS_ANALYSIS_WORKBENCH_VENV%\.ready"
set "NGS_ANALYSIS_WORKBENCH_LOCK=%NGS_ANALYSIS_WORKBENCH_VENV%.install-lock"
set "VIRTUAL_ENV="

if not exist "%NGS_ANALYSIS_WORKBENCH_PYTHON%" goto install
if not exist "%NGS_ANALYSIS_WORKBENCH_READY%" goto install
goto launch

:install
if not exist "%NGS_ANALYSIS_WORKBENCH_LOCK%\.." mkdir "%NGS_ANALYSIS_WORKBENCH_LOCK%\.."
for /f %%P in ('powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter ProcessId=$PID).ParentProcessId"') do set "NGS_ANALYSIS_WORKBENCH_PID=%%P"
if not defined NGS_ANALYSIS_WORKBENCH_PID exit /b 1
set /a NGS_ANALYSIS_WORKBENCH_WAIT=0
:install_lock
mkdir "%NGS_ANALYSIS_WORKBENCH_LOCK%" 2>nul
if not errorlevel 1 goto install_locked
if exist "%NGS_ANALYSIS_WORKBENCH_LOCK%\owner" (
  set /p NGS_ANALYSIS_WORKBENCH_OWNER=<"%NGS_ANALYSIS_WORKBENCH_LOCK%\owner"
  powershell -NoProfile -Command "if (Get-Process -Id $env:NGS_ANALYSIS_WORKBENCH_OWNER -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>nul
  if errorlevel 1 (
    del /q "%NGS_ANALYSIS_WORKBENCH_LOCK%\owner" 2>nul
    rmdir "%NGS_ANALYSIS_WORKBENCH_LOCK%" 2>nul
    goto install_lock
  )
) else (
  if %NGS_ANALYSIS_WORKBENCH_WAIT% geq 2 (
    rmdir "%NGS_ANALYSIS_WORKBENCH_LOCK%" 2>nul
    if not errorlevel 1 goto install_lock
  )
)
set /a NGS_ANALYSIS_WORKBENCH_WAIT+=1
if %NGS_ANALYSIS_WORKBENCH_WAIT% geq 110 (
  echo Timed out waiting for the shared NGS runtime installation. 1>&2
  exit /b 1
)
ping -n 2 127.0.0.1 >nul
goto install_lock

:install_locked
echo %NGS_ANALYSIS_WORKBENCH_PID%>"%NGS_ANALYSIS_WORKBENCH_LOCK%\owner"
if exist "%NGS_ANALYSIS_WORKBENCH_PYTHON%" if exist "%NGS_ANALYSIS_WORKBENCH_READY%" goto install_done
for %%D in ("%NGS_ANALYSIS_WORKBENCH_ORIGINAL_PATH:;=" "%") do call :find_path_runtime_python "%%~D"
if not defined NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON if defined USERPROFILE call :find_runtime_python "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python"
if not defined NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON (
  where python3 >nul 2>&1
  if not errorlevel 1 set "NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON=python3"
)
if not defined NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON (
  where python >nul 2>&1
  if not errorlevel 1 set "NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON=python"
)
if not defined NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON (
  echo NGS Analysis Workbench requires bundled Codex Python or python3/python on PATH. 1>&2
  set "NGS_ANALYSIS_WORKBENCH_EXIT_CODE=127"
  goto install_cleanup
)
"%NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON%" -m venv --without-pip "%NGS_ANALYSIS_WORKBENCH_VENV%"
if errorlevel 1 goto install_failed
"%NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON%" -m pip --python "%NGS_ANALYSIS_WORKBENCH_PYTHON%" install --requirement "%~dp0requirements.txt" 1>&2
if errorlevel 1 goto install_failed

type nul > "%NGS_ANALYSIS_WORKBENCH_READY%"
if errorlevel 1 goto install_failed

:install_done
del /q "%NGS_ANALYSIS_WORKBENCH_LOCK%\owner"
rmdir "%NGS_ANALYSIS_WORKBENCH_LOCK%"
goto launch

:install_failed
set "NGS_ANALYSIS_WORKBENCH_EXIT_CODE=%ERRORLEVEL%"
:install_cleanup
del /q "%NGS_ANALYSIS_WORKBENCH_LOCK%\owner"
rmdir "%NGS_ANALYSIS_WORKBENCH_LOCK%"
goto finish

:launch
pushd "%~dp0"
if "%~1"=="" (
  "%NGS_ANALYSIS_WORKBENCH_PYTHON%" -m ngs_workbench_mcp
) else (
  "%NGS_ANALYSIS_WORKBENCH_PYTHON%" -m %~1
)
set "NGS_ANALYSIS_WORKBENCH_EXIT_CODE=%ERRORLEVEL%"
popd
goto finish

:finish
if not defined NGS_ANALYSIS_WORKBENCH_EXIT_CODE set "NGS_ANALYSIS_WORKBENCH_EXIT_CODE=%ERRORLEVEL%"
if "%NGS_ANALYSIS_WORKBENCH_EXIT_CODE%"=="9009" (
  echo NGS Analysis Workbench requires bundled Codex Python or python3/python on PATH. 1>&2
)
exit /b %NGS_ANALYSIS_WORKBENCH_EXIT_CODE%

:find_path_runtime_python
if defined NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON exit /b 0
for %%R in ("%~1") do set "NGS_ANALYSIS_WORKBENCH_RUNTIME_BIN=%%~fR"
for %%R in ("%NGS_ANALYSIS_WORKBENCH_RUNTIME_BIN%\..\..\..") do set "NGS_ANALYSIS_WORKBENCH_RUNTIME_ROOT=%%~fR"
if /I "%NGS_ANALYSIS_WORKBENCH_RUNTIME_BIN%"=="%NGS_ANALYSIS_WORKBENCH_RUNTIME_ROOT%\dependencies\bin\override" call :find_runtime_python "%NGS_ANALYSIS_WORKBENCH_RUNTIME_ROOT%\dependencies\python"
if /I "%NGS_ANALYSIS_WORKBENCH_RUNTIME_BIN%"=="%NGS_ANALYSIS_WORKBENCH_RUNTIME_ROOT%\dependencies\bin\fallback" call :find_runtime_python "%NGS_ANALYSIS_WORKBENCH_RUNTIME_ROOT%\dependencies\python"
exit /b 0

:find_runtime_python
if defined NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON exit /b 0
if exist "%~1\python.exe" set "NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON=%~1\python.exe"
if not defined NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON if exist "%~1\python\python.exe" set "NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON=%~1\python\python.exe"
if not defined NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON if exist "%~1\bin\python.exe" set "NGS_ANALYSIS_WORKBENCH_RUNTIME_PYTHON=%~1\bin\python.exe"
exit /b 0
