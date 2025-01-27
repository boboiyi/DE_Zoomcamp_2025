import os
import argparse
import pandas as pd
from sqlalchemy import create_engine
from time import time

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    csv_name = "output.csv"

    os.system(f"wget {url} -O {csv_name}")

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
    engine.connect()

    df = pd.read_csv(csv_name, nrows=1, compression="gzip", encoding="latin1", low_memory=False)
    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists="replace")

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000, compression="gzip", encoding="latin1", low_memory=False)

    while True:
        try:
            tic = time()
            df = next(df_iter)
            df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
            df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
            df.to_sql(table_name, con=engine, if_exists="append")
            toc = time()
            print("Inserted new chunk..., took %.3f seconds" % (toc-tic))
        except:
            print('completed')
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Ingest CSV to Postgres")
    parser.add_argument("--user", help="username for postgres db")
    parser.add_argument("--password", help="password for postgres db")
    parser.add_argument("--host", help="host for postgres db")
    parser.add_argument("--port", help="port for postgres db")
    parser.add_argument("--db", help="postgres db name")
    parser.add_argument("--table_name", help="table name within postgres db")
    parser.add_argument("--url", help="url of the csv to put into the table")
    args = parser.parse_args()
    main(args)