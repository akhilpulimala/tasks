import requests
from pymongo import MongoClient
from mongoengine import Document, EmbeddedDocument, fields

# make a GET request to the REST API endpoint
# response = requests.get("https://restcountries.com/v3.1/all")

# # get the JSON data from the response
# data = response.json()

# # connect to the MongoDB instance
# client = MongoClient("mongodb://localhost:27017/")

# # create a new database and collection
# db = client["rest_countries"]
# collection = db["countries"]

# # insert the data into the collection
# for doc in data:
#     collection.insert_one(doc)

# # print the number of documents in the collection
# print(collection.count_documents({}))




class Language(EmbeddedDocument):
    name = fields.StringField(required=True)
    iso639_1 = fields.StringField(required=True)
    iso639_2 = fields.StringField(required=True)


class Country(Document):
    name = fields.StringField(required=True)
    capital = fields.StringField(required=True)
    region = fields.StringField(required=True)
    subregion = fields.StringField(required=True)
    population = fields.IntField(required=True)
    area = fields.FloatField(required=True)
    native_name = fields.StringField(required=True)
    currency = fields.StringField(required=True)
    language = fields.EmbeddedDocumentListField(Language, required=True)
    timezone = fields.ListField(fields.StringField(), required=True)


# create a new Country object
usa = Country(
    name="United States",
    capital="Washington, D.C.",
    region="Americas",
    subregion="Northern America",
    population=331002651,
    area=9826675.0,
    native_name="United States",
    currency="USD",
    language=[
        Language(name="English", iso639_1="en", iso639_2="eng"),
        Language(name="Spanish", iso639_1="es", iso639_2="spa"),
    ],
    timezone=["UTC-12:00", "UTC-11:00", "UTC-10:00", "UTC-09:00"],
)

# validate the Country object
usa.validate()
