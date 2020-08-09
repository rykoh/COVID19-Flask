"""Prepare data for Plotly Dash."""
import pandas as pd
import numpy as np
from pymongo import MongoClient



def create_dataframe():
    client =  MongoClient("mongodb+srv://covid19Scraper:Covid-19@cluster0-rvjf8.mongodb.net/FlaskTable?retryWrites=true&w=majority")
    db = client.FlaskTable
    name = 'AllDataVals'
    collection = db[name]    
    dataFrame = pd.DataFrame(list(collection.find()))
    #Delete unwanted columns
    del dataFrame['_id']
    del dataFrame['index']

    """Create Pandas DataFrame from MONGODB collection."""
    return dataFrame