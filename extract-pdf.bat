@echo off
setlocal
REM ============================================================
REM  MinerU launcher (GPU / VLM)
REM  Usage:
REM    - Drag a PDF / image / DOCX / PPTX / XLSX onto this file
REM    - or run:  extract-pdf.bat "C:\path\to\file.pdf"
REM  Output goes to the "output" folder next to this file.
REM ============================================================
set "MINERU=%~dp0.venv\Scripts\mineru.exe"
set "OUTDIR=%~dp0output"
set "MINERU_DEVICE_MODE=cuda"
set "MINERU_MODEL_SOURCE=modelscope"
REM The MinerU CLI defaults to one hour. Dense math PDFs can take longer on 8 GB GPUs.
if "%MINERU_TASK_RESULT_TIMEOUT_SECONDS%"=="" set "MINERU_TASK_RESULT_TIMEOUT_SECONDS=43200"

if "%~1"=="" (
  echo.
  echo  Usage: drag a PDF onto this file, or run:
  echo     extract-pdf.bat "C:\path\to\file.pdf"
  echo.
  pause
  exit /b 1
)

echo.
echo  Extracting with MinerU VLM on GPU:
echo     %~1
echo  Result timeout: %MINERU_TASK_RESULT_TIMEOUT_SECONDS% seconds
echo.
"%MINERU%" -p "%~1" -o "%OUTDIR%" -b vlm-engine
echo.
echo  Done. Open the result here:
echo     %OUTDIR%
echo.
pause
endlocal
