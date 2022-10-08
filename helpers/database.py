from pymongo import MongoClient
from ssl import CERT_NONE

# connect to mongodb
mongoconnection = MongoClient("", ssl=True, ssl_cert_reqs=CERT_NONE)
db = mongoconnection.get_database('')