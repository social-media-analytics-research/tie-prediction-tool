@echo off 
set message1=This script starts the tie prediction tool frontend
set message3=You can start the frontend by pressing "Enter" twice
set message2=You can stop the frontend by pressing "CTRL+C" twice
set message4=---------------------------------------------------

echo %message1%
echo %message2%
echo %message3%
echo %message4%

pause

cd..
cd linkprediction/frontend/angular
npm run ng serve



