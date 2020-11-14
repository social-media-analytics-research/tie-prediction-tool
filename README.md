# No-Code Tie Predictions in Social Media Networks

## Table of Contents
  * [Introduction](#introduction)
  * [Demonstration](#demonstration)
  * [Version History](#version-history)
  * [Dependencies](#dependencies)
  * [Setup](#setup)
  * [Application Start/Stop](#application-start-and-stop)
 * [Source Download](#source-download)

## Introduction
<p> This repository contains the source code of a no-code platform for tie prediction analysis in social media networks. <br> This platform is open source and uses the well-established python packages "NetworkX" (https://networkx.org/) and <br> "Scikit-Learn" as a foundation (https://scikit-learn.org/stable/). Contributions to this public repository are welcome, as <br> they may enhance this tool.<p>

![figure1](https://user-images.githubusercontent.com/11438779/98134465-14b62400-1ebf-11eb-8a4a-b6ecd6b68c7e.png)

The platform enables conducting tie prediction analysis without the need to resort to coding. Common tie <br> prediction approaches can be configured via the plaform's dashboard. The open source paradigm enables <br> augmenting the platform with furher algorithms or adjusting already incorporated algorithms. This is facilitated <br> by the fact that this tool relies on algorithms from well-established and well-documented python packages <br> (see above).

## Demonstration
The following steps illustrate an exemplary pipeline for no-code tie predictions in social media networks.

### Data Import
- Navigate to the tie prediction dashboard and select "+" to open the following window:

![figure2](https://user-images.githubusercontent.com/11438779/98134891-83937d00-1ebf-11eb-8af5-8f254e62df83.png)

- Import a network dataset in a suitable format (see the folder "2-sampledata" for exemplary datasets)
- Please Note: Ensure the node ids of your network dataset start with index 1

### Prediction Setup
- Select the created project, which leads to the following window:

![figure3](https://user-images.githubusercontent.com/11438779/98136811-9d35c400-1ec1-11eb-983c-deb8ecd687fe.png)

- Select "Settings"
- Add topology-based tie prediction methods via "+" (e.g., Adamic-Adar)
- Add social theory-based tie prediction methods via "+" (e.g., homophily)
- Add a machine learning classifier via "Create" (e.g., Decision Tree)
- Configure further attributes, if possible (e.g., homophily weightings)
- Configure the evaluation setup (e.g., the train-test-split ratio)
- Save the prediction setup with the corresponding button
   
- Execute the prediction with the corresponding button "Predict", which should lead to the following window:
   
![figure4](https://user-images.githubusercontent.com/11438779/98136882-ade63a00-1ec1-11eb-9f74-36e5d3417620.png)

- This window displays the achieved AUC and whether machine learning was used to derive this AUC value 
- Moreover, it displays when this AUC value was achieved
- Lastly, it provides further data about the considered social media network

### Prediction Evaluation 
- Navigate to the visualization tab to see the prediction results within the imported network:

![figure5](https://user-images.githubusercontent.com/11438779/98136910-b50d4800-1ec1-11eb-8af1-6a2043a84018.PNG)

- Specific dyads can be analyzed (click on the first node, hold CTRL, then click on the second node).
- Green: True positive predicitons. Red: False positive/false negative predictions. Blue: True negative predictions.
- Can be deactivated to substantially increase prediction velocity (see the folder linkprediction\prediction_methods) 

- Navigate to the evaluation tab to see the corresponding achieved AUC scores:

![figure6](https://user-images.githubusercontent.com/11438779/98137352-2ea53600-1ec2-11eb-918f-8f72368117f9.png)

- Displays the achieved AUC scores for each approach both as a plot and as a table.
- If a train-test-split was chosen, the buttons on the right corner can be used to view the train/test AUC scores.

## Version History
- Current version: `1.0`
- Version history: (this is the first productive version)
- For planned features in future versions, see the document "1)roadmap.txt" in the folder "3-documentation"

## Dependencies
- node.js (see https://nodejs.org/ or the folder "4-resources")
- python (see https://www.python.org/ or the folder "4-resources")
- postreSQL (see https://www.postgresql.org/)
- pgadmin (optional, if a database interface is desired) (see https://www.pgadmin.org/)
- anaconda (optional, if source code adjustments are planned) (see https://www.anaconda.com/)

## Setup

### Dependencies Setup (Windows/Linux)
- Download and install postgresSQL (see https://www.postgresql.org/)
  - Keep the default installation settings
  - Add postgresSQL bin file location (e.g., C:\Program Files\PostgreSQL\13\bin) as PATH variable

- Install node.js (see https://nodejs.org/ or the folder "4-resources")
  - Keep the default installation settings

### Automated Database Schema, Frontend, and Backend Setup (Windows only)
- You can setup the application automatically by running the application-install.bat file (64 bit or 32 bit)
  - Please Note: The postgresSQL server should start on windows startup (see under services.msc)
  - Please Note: The password is `12345`

### Manual Database Schema, Frontend, and Backend Setup (Windows/Linux)

#### Manual Database Schema Setup
- Open cmd in the folder "1-database" (by typing "cmd" in the file explorer bar)
- Run: "psql.exe -h 127.0.0.1 -p 5432 -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS ""uuid-ossp"";"
- Run twice: "psql.exe -h 127.0.0.1 -p 5432 -U postgres -d postgres -f db-schema.sql"
  - Please Note: The password is `12345`

#### Manual Frontend Setup
- Open cmd or terminal in the root repository directory
- Navigate to the directory "linkprediction/frontend/angular"
- Install the node packages with "npm install"

#### Manual Backend Setup
- Install python (see https://www.python.org/ or the folder "4-resources")
- Open cmd or terminal the "5-sources" repository directory
- Install the python libraries with "pip install -r requirements.txt"

## Application Start and Stop

### Automated Start/Stop (Windows only)
- You can start the components automatically by running the -start.bat files and pressing "Enter" twice in each cmd
- Open the frontend-dashboard.url file
- You can stop the components by pressing "CRTL+C" twice in the corresponding cmd windows
- The dashboard is accessible via the URL "localhost:4200"
- The backend is accessible via the URL "localhost:8080/api"

### Manual Start/Stop (Windows/Linux, alternative to automated)

#### Manual Frontend Start/Stop
- Open cmd or terminal in the root repository directory
- Navigate to the directory "linkprediction/frontend/angular"
- Start the frontend in local server with"npm run ng serve"
- Open the frontend-dashboard.url file
- The dashboard is accessible via the URL "localhost:4200"
- You can stop the componenent by closing the cmd window

#### Manual Backend Start/Stop
- Open command line tool in the cloned repository directory
- Start backend in local server with "python -m linkprediction"
- The backend is accessible via the URL "localhost:8080/api"
- You can stop the componenent by closing the cmd window
