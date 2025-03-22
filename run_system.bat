@echo off
echo Starting Calibration Analyzer System...

REM Start the API server in a new command window
start cmd /k "echo Starting API server... && python api_server.py"

REM Wait for the server to initialize
echo Waiting for API server to initialize...
timeout /t 5 /nobreak

REM Start the Tkinter frontend
echo Starting Tkinter frontend...
start cmd /k "python tkinter_frontend.py"

echo System started. You can now use the application.