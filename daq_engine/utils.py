import redis
from pymongo import MongoClient
from urllib import parse

REDIS_HOST = "180.201.163.246"
REDIS_PORT = 42001
REDIS_PASSWORD = "151425"

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, password=REDIS_PASSWORD)
redis_conn = redis.Redis(connection_pool=pool)


def get_redis_conn():
    return redis_conn


MONGO_HOST = "180.201.163.246"
MONGO_PORT = 43001
MONGO_DB = "ms_daq_engine"
MONGO_USERNAME = parse.quote_plus("wyx151425")
MONGO_PASSWORD = parse.quote_plus("MsMongo001@dmin")

client = MongoClient(
    "mongodb://{0}:{1}@{2}:{3}/{4}".format(MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST, str(MONGO_PORT), MONGO_DB))
mongo_conn = client[MONGO_DB]


def get_mongo_conn():
    return mongo_conn
