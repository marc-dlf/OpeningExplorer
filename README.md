# OpeningExplorer

A Dash applications which enables to search for a Chess.com usernames and get the
positions where the player has the worst win rate in order to spot areas of improvement
for opening training. 

![Alt text](/img/dash_screenshot.png?raw=true)

## Setup

Inside the repo create a data folder by running the following command in your terminal:

```mkdir data```

If poetry (a python dependencies solver) is not installed on your system, you should run:

```pip install poetry```

Then you can setup your environment by running:

```poetry install```

This will install all the dependencies in a virtualenvironment manage by poetry.

## Run Dash App

Run from the root of the repo :

```poetry run python src/app.py```

Then go to the port http://127.0.0.1:8050/ to try the app! Once you submit a player 
name, if the csv containing his games is not already present in the data folder it 
will be constructed from the Fetcher class which can take some time. But once it 
is done, when querying the same username it is faster. 

## Unit testing

To run unit tests:

```poetry run pytest```