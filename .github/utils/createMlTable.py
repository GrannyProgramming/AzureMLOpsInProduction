import argparse
import mltable
from pathlib import Path

def create_and_save_ml_table(save_dir):
    """
    Create an ML table from parquet files, perform preprocessing, and save the result.
    
    Args:
        save_dir (str): The directory to save the processed table.
    """
    # Create directory for saving data
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    # Glob the parquet file paths for years 2015-19, all months.
    paths = [
        {
            "pattern": f"wasbs://nyctlc@azureopendatastorage.blob.core.windows.net/{color}/puYear={year}/puMonth=*/**/*.parquet"
        }
        for color in ["green", "yellow"]
        for year in range(2015, 2020)
    ]

    # Create a table from the parquet paths
    tbl = mltable.from_parquet_files(paths)

    # Sample a smaller portion of the data
    tbl = tbl.take_random_sample(probability=0.001, seed=735)

    # Filter trips with a distance > 0
    tbl = tbl.filter("col('tripDistance') > 0")

    # Drop columns
    tbl = tbl.drop_columns(["puLocationId", "doLocationId"])

    # Create two new columns - year and month - where the values are taken from the path
    tbl = tbl.extract_columns_from_partition_format("/puYear={year}/puMonth={month}")

    # Print the first 5 records of the table as a check
    print(tbl.show(5))

    # Save the table
    tbl.save(str(save_dir))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create and save ML table.')
    parser.add_argument('save_directory', type=str, help='Directory to save data')
    args = parser.parse_args()

    # Call the function to create and save the ML table
    create_and_save_ml_table(args.save_directory)
