import argparse
from pathlib import Path
import mltable
from workflowhelperfunc.workflowhelper import setup_logger, log_event

## This logic needs to be reviewed and updated, don't think deleting a file is the right way to go
def create_directories(save_dir, logger):
    """
    Create necessary directories.

    Args:
        save_dir (str): The directory where the processed table will be saved.
        logger (Logger): Logger object for logging events.
    """
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    # Define subdirectories for MLTable 
    mltable_dir = save_dir / "MLTable"

    # Check if a file with the same name exists
    if mltable_dir.is_file():
        log_event(logger, 'info', f"A file with the same name '{mltable_dir}' already exists. \
                   Deleting it.")
        mltable_dir.unlink()

    # Create the subdirectories if they do not exist
    mltable_dir.mkdir(parents=True, exist_ok=True)

    return mltable_dir


def load_data():
    """
    Load data from predefined paths.

    Returns:
        mltable.mltable: The loaded ML table.
    """
    # Define the data source
    paths = [
        {
            "pattern": f"wasbs://nyctlc@azureopendatastorage.blob.core.windows\
                .net/{color}/puYear={year}/puMonth=*/**/*.parquet"
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
        tbl (mltable.mltable): The mltable to preprocess.

    Returns:
        mltable.mltable: The preprocessed ML table.
    """
    tbl = tbl.take_random_sample(probability=0.001, seed=735)
    tbl = tbl.filter("col('tripDistance') > 0")
    tbl = tbl.drop_columns(["puLocationId", "doLocationId"])
    tbl = tbl.extract_columns_from_partition_format("/puYear={year}/puMonth={month}")

    # Set the table name
    tbl.name = "NYC_taxi"

    return tbl

def save_data(tbl, mltable_dir):
    """
    Save the processed data.

    Args:
        tbl (mltable.mltable): The preprocessed mltable.
        mltable_dir (Path): Directory to save the mltable.
    """
    # Save the ML table
    tbl.save(str(mltable_dir))


def main():
    """
    The main function that gets the save directory from the user and creates and saves the ML table.
    """
    logger = setup_logger(__name__)

    try:
        parser = argparse.ArgumentParser(description='Create and save ML table.')
        parser.add_argument('save_directory', type=str, help='Directory to save data')
        args = parser.parse_args()

        mltable_dir = create_directories(args.save_directory, logger)
        tbl = load_data()
        tbl = preprocess_data(tbl)
        save_data(tbl, mltable_dir)

        log_event(logger, 'info', "ML table created and saved successfully.")
    except Exception as error:
        log_event(logger, 'error', f"An error occurred: {str(error)}")


if __name__ == "__main__":
    main()
    
