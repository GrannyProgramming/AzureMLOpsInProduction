import logging
import mltable
import os
from loggingConfig import setup_logging


# Configure logging
log_file_path = "../resources/mylog.log"
setup_logging(log_file_path, level="INFO")
logger = logging.getLogger(__name__)

# create directory for saving data
save_dir = '../../../dataScience/src/data'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
    logger.info(f"Created directory for saving data: {save_dir}")

# glob the parquet file paths for years 2015-19, all months.
paths = [
    {
        "pattern": f"wasbs://nyctlc@azureopendatastorage.blob.core.windows.net/{color}/puYear={year}/puMonth=*/**/*.parquet"
    }
    for color in ["green", "yellow"]
    for year in range(2015, 2020)
]
logger.info(f"Parquet file paths globbed: {paths}")

# create a table from the parquet paths
tbl = mltable.from_parquet_files(paths)
logger.info(f"Table created from parquet files.")

# sample a smaller portion of the data
tbl = tbl.take_random_sample(probability=0.001, seed=735)
logger.info(f"Table sampled. ")

# filter trips with a distance > 0
tbl = tbl.filter("col('tripDistance') > 0")
logger.info(f"Table filtered by trip distance > 0.")

# Drop columns
tbl = tbl.drop_columns(["puLocationId", "doLocationId"])
logger.info(f"Columns puLocationId and doLocationId dropped.")

# Create two new columns - year and month - where the values are taken from the path
tbl = tbl.extract_columns_from_partition_format("/puYear={year}/puMonth={month}")
logger.info(f"New columns 'year' and 'month' created.")

# print the first 5 records of the table as a check
print(tbl.show(5))
logger.info("Printed the first 5 records of the table.")

# save the table
tbl.save(save_dir)
logger.info(f"Table saved to {save_dir}")
