import falcon
import falcon.asgi
from graphene import ObjectType, String, List, Field, ID, Float, Int, Mutation, Schema
from graphene.relay import Node, Connection, ConnectionField
from graphene_mongo import MongoengineObjectType
from mongoengine import connect, Document, EmbeddedDocument, fields
from geopy.distance import distance
from falcon import HTTPNotFound

from graphql import graphql

# connect to the MongoDB database
connect('rest_countries')

# define embedded documents
class Language(EmbeddedDocument):
    name = fields.StringField(required=True)
    iso639_1 = fields.StringField(required=True)
    iso639_2 = fields.StringField(required=True)

# define document
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
    location = fields.PointField(required=True)

    def distance_to(self, lat, lng):
        country_location = (self.location.latitude, self.location.longitude)
        query_location = (lat, lng)
        return distance(country_location, query_location).km

# define the GraphQL types
class LanguageType(ObjectType):
    name = String(required=True)
    iso639_1 = String(required=True)
    iso639_2 = String(required=True)

class CountryType(MongoengineObjectType):
    class Meta:
        model = Country
        interfaces = (Node, )

    distance_to = Float(lat=Float(required=True), lng=Float(required=True))

    def resolve_distance_to(self, info, lat, lng):
        return self.distance_to(lat, lng)

class CountryConnection(Connection):
    class Meta:
        node = CountryType

# define the GraphQL queries
class Query(ObjectType):
    node = Node.Field()
    countries = ConnectionField(CountryConnection)
    country = Field(CountryType, id=ID(required=True))
    countries_nearby = List(CountryType, lat=Float(required=True), lng=Float(required=True))
    countries_by_language = List(CountryType, language=String(required=True))

    def resolve_countries(self, info, **kwargs):
        return Country.objects.all()

    def resolve_country(self, info, id):
        country = Country.objects.with_id(id)
        if not country:
            raise HTTPNotFound(title="Country not found", description=f"Country with id {id} not found")
        return country

    def resolve_countries_nearby(self, info, lat, lng):
        countries = Country.objects.all()
        countries = sorted(countries, key=lambda country: country.distance_to(lat, lng))
        return countries

    def resolve_countries_by_language(self, info, language):
        return Country.objects(language__name=language)

# define the GraphQL mutations
class EditCountryMutation(Mutation):
    class Arguments:
        id = ID(required=True)
        name = String()
        capital = String()
        region = String()
        subregion = String()
        population = Int()
        area = Float()
        native_name = String()
        currency = String()
        timezone = List(String)

    country = Field(CountryType)

    def mutate(self, info, id, **kwargs):
        country = Country.objects.with_id(id)
        if not country:
            raise HTTPNotFound(title="Country not found", description=f"Country with id{id}")

schema = Schema(query=Query)

class GraphQLResource:
     async def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.content_type = falcon.MEDIA_TEXT  # Default is JSON, so override
        resp.text = (
            "-------------Welcome------------"
        )
     async def on_post(self, req, resp):
        query = req.media.get('query')
        result = graphql(schema, query)
        resp.media = result.to_dict()

app = falcon.asgi.App()
app.add_route('/graphql', GraphQLResource())
