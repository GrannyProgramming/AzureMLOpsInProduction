import argparse
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from glob import glob

def create_and_save_table(save_dir):
    """
    Create a DataFrame from parquet files, perform preprocessing, and save the result.
    
    Args:
        save_dir (str): The directory to save the processed DataFrame.
    """
    # Create directory for saving data
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    # Glob the parquet file paths for years 2015-19, all months.
    paths = [
        glob(f"wasbs://nyctlc@azureopendatastorage.blob.core.windows.net/{color}/puYear={year}/puMonth=*/**/*.parquet")
        for color in ["green", "yellow"]
        for year in range(2015, 2020)
    ]

    # Flatten the list of paths
    paths = [item for sublist in paths for item in sublist]

    # Read the parquet files into a DataFrame
    df = pd.concat([pd.read_parquet(path) for path in paths])

    # Sample a smaller portion of the data
    df = df.sample(frac=0.001, random_state=735)

    # Filter trips with a distance > 0
    df = df[df['tripDistance'] > 0]

    # Drop columns
    df = df.drop(["puLocationId", "doLocationId"], axis=1)

    # TODO: Create two new columns - year and month - where the values are taken from the path
    # This part depends on the format of your Parquet data, and it's not straightforward to implement it without knowing the structure of your data

    # Print the first 5 records of the table as a check
    print(df.head(5))

    # Save the DataFrame as a parquet file
    df.to_parquet(save_dir / 'NYC_taxi.parquet')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create and save DataFrame.')
    parser.add_argument('save_directory', type=str, help='Directory to save data')
    args = parser.parse_args()

    # Call the function to create and save the DataFrame
    create_and_save_table(args.save_directory)
