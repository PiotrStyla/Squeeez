@echo off
setlocal
set PATH=C:\mingw64\bin;%PATH%

echo Compiling LSTM test...
echo.

g++ -O2 -std=c++17 -o test_lstm.exe test_lstm.cpp -I.

if %ERRORLEVEL% EQU 0 (
  echo.
  echo SUCCESS! Test compiled!
  echo Running tests...
  echo.
  test_lstm.exe
) else (
  echo.
  echo FAILED! Check errors above.
)
