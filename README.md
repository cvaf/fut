# FIFA - Player & Market Analysis

Analyzing player prices, attributes and statistics.

Credits to [S. Leone](https://www.kaggle.com/stefanoleone992/fifa-19-fifa-ultimate-team/version/1) for the original dataframe and [futbin.com](www.futbin.com). 

Through web scraping, the original dataframe was updated by fetching the attributes and prices of new players from futbin. The [database_build](https://github.com/cvaf/fut/blob/master/database_build.ipynb) notebook provides instructions for updating the dataframe. All relevant scraping functions can be found in db_functions.py

This [dashboard](https://fut-dash.herokuapp.com/) provides an interactive interface to view the relationship between Price and Performance. Code can be found in [dash_pgp.py](https://github.com/cvaf/fut/blob/master/dash_dataframes.py). Below is a screenshot of the dashboard. 

![Imgur](https://i.imgur.com/gj5WDG5.png)



