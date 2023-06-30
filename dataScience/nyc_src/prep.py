import argparse
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from mltables import MLTable

parser = argparse.ArgumentParser("prep")
parser.add_argument("--raw_data", type=str, help="Path to raw data file")
parser.add_argument("--prep_data", type=str, help="Path of prepped data")
args = parser.parse_args()

lines = [f"Raw data path: {args.raw_data}", f"Data output path: {args.prep_data}"]
for line in lines:
    print(line)

print("mounted_path files: ")
taxi_df = pd.read_parquet(args.raw_data)

# Define useful columns needed for the Azure Machine Learning NYC Taxi tutorial
useful_columns = f"['cost', 'distance', 'dropoff_datetime', 'dropoff_latitude', 'dropoff_longitude', 'passengers', 'pickup_datetime', 'pickup_latitude', 'pickup_longitude', 'store_forward', 'vendor']"

# Rename columns as per Azure Machine Learning NYC Taxi tutorial
all_columns = {
    "vendorID": "vendor",
    "lpepPickupDatetime": "pickup_datetime",
    "lpepDropoffDatetime": "dropoff_datetime",
    "tpepPickupDamok'//'teTime": "pickup_datetime",
    "tpepDropoffDateTime": "dropoff_datetime",
    "pickupLongitude": "pickup_longitude",
    "pickupLatitude": "pickup_latitude",
    "dropoffLongitude": "dropoff_longitude",
    "dropoffLatitude": "dropoff_latitude",
    "passengerCount": "passengers",
    "fareAmount": "cost",
    "tripDistance": "distance",
    "startLon": "pickup_longitude",
    "startLat": "pickup_latitude",
    "endLon": "dropoff_longitude",
    "endLat": "dropoff_latitude",
}

# These functions ensure that null data is removed from the dataset,
# which will help increase machine learning model accuracy.

def get_dict(dict_str):
    pairs = dict_str.strip("{}").split(";")
    new_dict = {}
    for pair in pairs:
        key, value = pair.strip().split(":")
        new_dict[key.strip().strip("'")] = value.strip().strip("'")
    return new_dict

def cleanseData(data, columns, useful_columns):
    useful_columns = [s.strip().strip("'") for s in eval(useful_columns)]
    new_columns = get_dict(str(columns))
    new_df = (data.dropna(how="all").rename(columns=new_columns))[useful_columns]
    new_df.reset_index(inplace=True, drop=True)
    return new_df

taxi_data_clean = cleanseData(taxi_df, all_columns, useful_columns)

# Save the prepped data as an mltable
table = MLTable.from_dataframe(taxi_data_clean)
table.save(str(Path(args.prep_data) / "merged_data.mltable"))
