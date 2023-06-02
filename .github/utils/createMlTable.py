import argparse
import mltable
import pandas as pd
from pathlib import Path

def create_directories(save_dir):
    """
    Create necessary directories based on the type of the provided file path.

    Args:
        save_dir (str): The directory where the processed table will be saved.
    """
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    # Define subdirectories for MLTable and URI
    mltable_dir = save_dir / "MLTable"
    uri_dir = save_dir / "URI"

    # Check the type of the provided file path
    if mltable_dir.is_file():
        # Provided path is an MLTable file
        mltable_dir = mltable_dir.parent
    elif uri_dir.is_file():
        # Provided path is a URI file
        uri_dir = uri_dir.parent

    # Create the necessary directories
    mltable_dir.mkdir(parents=True, exist_ok=True)
    uri_dir.mkdir(parents=True, exist_ok=True)

    return mltable_dir, uri_dir


def load_data():
    """
    Load data from predefined paths.
    """
    # Define the data source
    paths = [
        {
            "pattern": f"wasbs://nyctlc@azureopendatastorage.blob.core.windows.net/{color}/puYear={year}/puMonth=*/**/*.parquet"
        }
        for color in ["green", "yellow"]
        for year in range(2015, 2020)
    ]

    # Load the data and create an ML table
    tbl = mltable.from_parquet_files(paths)
    return tbl

def preprocess_data(tbl):
    """
    Preprocess the data.

    Args:
        tbl (mltable): The mltable to preprocess.
    """
    tbl = tbl.take_random_sample(probability=0.001, seed=735)
    tbl = tbl.filter("col('tripDistance') > 0")
    tbl = tbl.drop_columns(["puLocationId", "doLocationId"])
    tbl = tbl.extract_columns_from_partition_format("/puYear={year}/puMonth={month}")

    # Set the table name
    tbl.name = "NYC_taxi"

    return tbl

def save_data(tbl, mltable_dir, uri_dir):
    """
    Save the processed data.

    Args:
        tbl (mltable): The preprocessed mltable.
        mltable_dir (Path): Directory to save the mltable.
        uri_dir (Path): Directory to save the parquet file.
    """
    # Save the ML table
    tbl.save(str(mltable_dir))

    # Convert the ML table to a pandas dataframe and save as Parquet
    df = tbl.to_pandas()
    df.to_parquet(str(uri_dir / "NYC_taxi.parquet"))

def main():
    """
    The main function that gets the save directory from the user and creates and saves the ML table.
    """
    parser = argparse.ArgumentParser(description='Create and save ML table.')
    parser.add_argument('save_directory', type=str, help='Directory to save data')
    args = parser.parse_args()

    mltable_dir, uri_dir = create_directories(args.save_directory)
    tbl = load_data()
    tbl = preprocess_data(tbl)
    save_data(tbl, mltable_dir, uri_dir)

if __name__ == "__main__":
    main()
