@echo off 
set message1=This script starts the tie prediction tool backend
set message3=You can start the backend by pressing "Enter" twice
set message2=You can stop the backend by pressing "CTRL+C" twice
set message4=---------------------------------------------------

echo %message1%
echo %message2%
echo %message3%
echo %message4%

pause

python -m linkprediction



