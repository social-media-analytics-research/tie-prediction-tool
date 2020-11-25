@echo off 
set message1=This script installs the tie prediction tool
set message2=You can start the intallation by pressing any button
set message3=---------------------------------------------------
set message4=Installation started... You may need to accept the administrative prompt

echo %message1%
echo %message2%
echo %message3%

pause

echo %message4%

cd ..
cd 4-resources
python-3.8.6-32.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
cd..
cd 1-database
psql.exe -h 127.0.0.1 -p 5432 -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS ""uuid-ossp"";"
psql.exe -h 127.0.0.1 -p 5432 -U postgres -d postgres -f db-schema.sql"
psql.exe -h 127.0.0.1 -p 5432 -U postgres -d postgres -f db-schema.sql"
cd..
cd 4-resources
pip install -r requirements.txt
cd..
cd linkprediction/frontend/angular
npm install
