import redis
from pymongo import MongoClient

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWORD = "151425"

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, password=REDIS_PASSWORD)
redis_conn = redis.Redis(connection_pool=pool)

def get_redis_conn():
    return redis_conn

MONGO_HOST = "127.0.0.1"
MONGO_PORT = 27017
MONGO_DB = "ms-daq-engine"
MONGO_USERNAME = "wyx151425"
MONGO_PASSWORD = "151425"

client = MongoClient("mongodb://%s:%s@%s:%s/%s" % (MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST, str(MONGO_PORT), MONGO_DB))
mongo_conn = client[MONGO_DB]

def get_mongo_conn():
    return mongo_conn
