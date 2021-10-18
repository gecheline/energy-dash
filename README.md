# World Electricity Dashboard

The dashboard displays visualizations of data in the Total Electricity table, downloaded from the Energy Statistics Database at the UNDATA website: http://data.un.org/Data.aspx?d=EDATA&f=cmID%3aEL . The visualizations focus on energy generation by fuel type and energy consumption by sector, as well an explorer of all data available in the table per country for a given year.

### Dependencies
The dashboard is built using dash and plotly.express. The list of dependencies includes:
```
numpy==1.21.2
pandas==1.3.3
plotly==5.3.1
dash==2.0.0
dash-bootstrap-components==0.13.1
dash-core-components==2.0.0
dash-html-components==2.0.0
dash-table==5.0.0
country-converter==0.7.3 # for conversion between country names and ISO-3 codes.
whitenoise==5.3.0 # used only for running on Heroku
```
In a conda environment, all dependencies should be easily installed with
```
pip install numpy pandas dash dash-bootstrap-components country_converter whitenoise
```

### Running the app locally
To run the app locally, clone the repo and run
```
python app.py
```
From there, navigate to the provided IP address to view the dashboard in a browser.

### Live demo
Alternatively, you can view the dashboard directly as a [heroku app](https://electricity-casestudy.herokuapp.com/)