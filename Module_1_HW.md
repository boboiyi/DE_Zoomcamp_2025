## Question 1. Understanding docker first run
*Run docker with the python:3.12.8 image in an interactive mode, use the entrypoint bash.
What's the version of pip in the image?*

```bash
$ docker run -it --entrypoint bash python:3.12.8
Unable to find image 'python:3.12.8' locally
3.12.8: Pulling from library/python
ec162e081748: Download complete
4d8be491b866: Download complete
12f3828c4288: Download complete
Digest: sha256:2e726959b8df5cd9fd95a4cbd6dcd23d8a89e750e9c2c5dc077ba56365c6a925
Status: Downloaded newer image for python:3.12.8
root@1dc8e4878854:/# pip --version
pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```

Answer: **24.3.1**

## Question 2. Understanding Docker networking and docker-compose
*Given the following docker-compose.yaml, what is the hostname and port that pgadmin should use to connect to the postgres database?*

Since we run the containers with docker-compose, Docker creates an internal network so that containers can communicate. Pgadmin runs inside a Docker container and is on the same Docker network as the PostgreSQL container, it doesn't need to go through the host machine at all. That's why pgadmin will use hostname ```db``` and connect via ```5432``` port.

Answer: **db:5432**

## Prepare Postgres
I used the ```ingest_data.py``` script and a dedicaded image within ```Dockerfile``` to ingest Green Taxi Data into Postgres, and then used ```ingest_data_zones.ipynb``` notebook to additionally ingest Zones table into the db. All the files are within the Github directory for this Module's HW. I also changed ```ingest_data.py``` in order to correctly read the data itself from github and headers as well. Below are the bash commands:
```bash
$ docker build -t taxi_ingest:v001 .
...
Successfully built c89790f1c567
Successfully tagged taxi_ingest:v001

$ docker run -it --network=de_zoom_default taxi_ingest:v001 --user=postgres --password=postgres --host=pgdatabase --port=5432 --db=ny_taxi --table_name=green_taxi_trips --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz"
```
Through pgadmin I also confirmed the rowcount: 476386. The rowcount for Zones was: 265.

## Question 3. Trip Segmentation Count
During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, respectively, happened:

- Up to 1 mile
- In between 1 (exclusive) and 3 miles (inclusive),
- In between 3 (exclusive) and 7 miles (inclusive),
- In between 7 (exclusive) and 10 miles (inclusive),
- Over 10 miles

Solution:
- Up to 1 mile
```sql
SELECT
    COUNT(*)
FROM
    green_taxi_trips t
WHERE
	t."lpep_pickup_datetime" >= '2019-10-01 00:00:00' AND 
	t."lpep_dropoff_datetime" < '2019-11-01 00:00:00' AND
    t."trip_distance" <= 1 ;
```
Answer: 104802

- In between 1 (exclusive) and 3 miles (inclusive)
```sql
SELECT
    COUNT(*)
FROM
    green_taxi_trips t
WHERE
	t."lpep_pickup_datetime" >= '2019-10-01 00:00:00' AND 
	t."lpep_dropoff_datetime" < '2019-11-01 00:00:00' AND
    t."trip_distance" > 1 AND
	t."trip_distance" <= 3;
```
Answer: 198924

- In between 3 (exclusive) and 7 miles (inclusive)
```sql
SELECT
    COUNT(*)
FROM
    green_taxi_trips t
WHERE
	t."lpep_pickup_datetime" >= '2019-10-01 00:00:00' AND 
	t."lpep_dropoff_datetime" < '2019-11-01 00:00:00' AND
    t."trip_distance" > 3 AND
	t."trip_distance" <= 7;
```
Answer: 109603

- In between 7 (exclusive) and 10 miles (inclusive)
```sql
SELECT
    COUNT(*)
FROM
    green_taxi_trips t
WHERE
	t."lpep_pickup_datetime" >= '2019-10-01 00:00:00' AND 
	t."lpep_dropoff_datetime" < '2019-11-01 00:00:00' AND
    t."trip_distance" > 7 AND
	t."trip_distance" <= 10;
```
Answer: 27678

- Over 10 miles
```sql
SELECT
    COUNT(*)
FROM
    green_taxi_trips t
WHERE
	t."lpep_pickup_datetime" >= '2019-10-01 00:00:00' AND 
	t."lpep_dropoff_datetime" < '2019-11-01 00:00:00' AND
    t."trip_distance" > 10;
```
Answer: 35189

General answer: **104838,198924,109603,27678,35189**

## Question 4. Longest trip for each day
Which was the pick up day with the longest trip distance? Use the pick up time for your calculations.

Tip: For every day, we only care about one single trip with the longest distance.

2019-10-11
2019-10-24
2019-10-26
2019-10-31

Solution:
```sql
SELECT 
    lpep_pickup_datetime::date AS longest_trip_date
FROM 
    green_taxi_trips
WHERE 
    trip_distance = (SELECT MAX(trip_distance) FROM green_taxi_trips);
```
Answer: 2019-10-31