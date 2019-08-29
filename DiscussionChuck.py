import re
import six
import time

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions

"""
The design of DiscussionChuck is to provide the generic class for discussion data processing
It includes message ordering, sentiment analyze and so on

"""

# set up google client
google_client = language.LanguageServiceClient()

# set up watson client
watson_api = "RY0bRjK8iWHf8SzMlSk0DJwMNm6chVLy_GdVAch9klRt"
service = NaturalLanguageUnderstandingV1(
    version='2019-07-12',
    iam_apikey= watson_api,
    url='https://gateway.watsonplatform.net/natural-language-understanding/api'
)

# @param text
# @return a list of entities with salience score, [(entity name, entity salience score)...]
def google_entity_extraction(text):
    # decode utf-8 format
    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)
    entities = google_client.analyze_entities(document).entities


    # save output
    entity_list = list()

    return entity_list

# watson nlp
def watson_entity_extraction(text):
    response = None
    while response is None:
        try:
            response = service.analyze(
                text=text,
                features=Features(entities=EntitiesOptions(sentiment=True)),
                language="en"
            ).get_result()
        except Exception as e:
            response = None
            time.sleep(2)
            print(e)
            print()
            print("Resent the request and Wait for Watson respond...")

    return response

# one message
class DiscussionChuck:
    def __init__(self, _usid, _message, _order):
        self.user_id = _usid
        self.message = _message
        self.order = _order
        self.entity_sentiment_list = list()


    # generate entity sentiment
    # Watson NLP Mode
    # @param keep_quote True or False
    # @param keep_link True or False
    def gen_entity_sentiment(self, keep_quote=True, keep_link=True):
        _message = self.message
        if not keep_quote:
            quote_pattern = re.compile(r'.*?(<quote>.*?</quote>).*?')
            all_quotes = re.findall(quote_pattern, _message)
            for quote in all_quotes:
                _message = _message.replace(quote, "")

        if not keep_link:
            link_pattern = re.compile(r'.*?(<url>.*?</url>).*?')
            all_links = re.findall(link_pattern, _message)
            for link in all_links:
                _message = _message.replace(link, "")

        sentiment_result = watson_entity_extraction(_message)

        all_entities = sentiment_result['entities']
        self.entity_sentiment_list = [(entity['text'], entity['sentiment']['score']) for entity in all_entities]



# one discussion that contains multiple messages
class DiscussionChuckContainer:
    def __init__(self):
        self.chuckList = []

    def append(self, _chuck):
        self.chuckList.append(_chuck)

    # return a list of all chucks from the target user
    def getUserChucks(self, _user):
        targetChucks = list()
        for chuck in self.chuckList:
            if _user == chuck.user_id:
                targetChucks.append(chuck)
        return targetChucks

    def __getitem__(self, item):
        return self.chuckList[item]

    def __len__(self):
        return len(self.chuckList)

    # return the list of all chucks from the user who has the most one in this container
    def getUserMostChucks(self):
        all_users = set()
        for chuck in self.chuckList:
            all_users.add(chuck.user_id)

        user_most_chucks = []
        for user in all_users:
            chuck = self.getUserChucks(user)
            if len(chuck) > len(user_most_chucks):
                user_most_chucks = chuck
        return user_most_chucks




