import re
import six
import time
import sys

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions

"""
The design of DiscussionChuck is to provide the generic class for discussion data processing
It includes message ordering, sentiment analyze and so on

"""

# set up Data from Google NLP client
google_client = language.LanguageServiceClient()

# set up Data from Watson NLP client
watson_api = "RY0bRjK8iWHf8SzMlSk0DJwMNm6chVLy_GdVAch9klRt"
service = NaturalLanguageUnderstandingV1(
    version='2019-07-12',
    iam_apikey= watson_api,
    url='https://gateway.watsonplatform.net/natural-language-understanding/api'
)


# @param text
# @return a list of entities with salience score, [(entity name, entity salience score)...]
# I only take the overall entity sentiment and ignore the mention entity of a single word
def google_entity_extraction(text):
    # decode utf-8 format
    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language="en")
    result = google_client.analyze_entity_sentiment(document)

    entities_list = list()
    for entity in result.entities:
        if "score" in str(entity.sentiment):
            datum = list()
            datum.append(entity.name)
            datum.append(entity.sentiment.score)
            datum.append(entity.sentiment.magnitude)
            entities_list.append(datum)

    return entities_list

# Data from Watson NLP nlp
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

# Get google sentence sentiment data


# return a list of dictionaries that contains entities content, sentiment, magnitude, salience and mention
def google_entity_extraction_detailed(text):

    entity_data_list = list()
    # decode utf-8 format
    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language="en")
    result = google_client.analyze_entity_sentiment(document)

    for entity in result.entities:
        entity_dict = dict()
        entity_dict["name"] = entity.name
        entity_dict["mentions"] = list()
        for mention in entity.mentions:
            mention_dict = dict()
            mention_dict["content"] = mention.text.content
            mention_dict["order"] = mention.text.begin_offset
            mention_dict["magnitude"] = mention.sentiment.magnitude
            mention_dict["score"] = mention.sentiment.score
            entity_dict["mentions"].append(mention_dict)
        entity_dict["salience"] = entity.salience
        if "score" in str(entity.sentiment):
            entity_dict["magnitude"] = entity.sentiment.magnitude
            entity_dict["score"] = entity.sentiment.score
        else:
            entity_dict["magnitude"] = None
            entity_dict["score"] = None

        entity_data_list.append(entity_dict)

    # normalize the order number in the mentions
    all_orders = list()
    for entity in entity_data_list:
        all_orders += [mention["order"] for mention in entity["mentions"]]
    # sort order(originally offset) and put it back
    all_orders = sorted(all_orders)
    for i in range(len(entity_data_list)):
        for j in range(len(entity_data_list[i]["mentions"])):
            off_set_order = entity_data_list[i]["mentions"][j]["order"]
            entity_data_list[i]["mentions"][j]["order"] = all_orders.index(off_set_order)+1

    return entity_data_list


# return a list of dictionaries that contains sentence content, sentiment, magnitude, salience and mention
def google_sentence_extraction(text):

    sentence_data_list = list()

    # decode utf-8 format
    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language="en")
    result = google_client.analyze_sentiment(document)


    for sentence in result.sentences:
        sentence_dict = dict()
        sentence_dict["content"] = sentence.text.content
        sentence_dict["score"] = sentence.sentiment.score
        sentence_dict["magnitude"] = sentence.sentiment.magnitude
        sentence_data_list.append(sentence_dict)

    return sentence_data_list, result.document_sentiment.score, result.document_sentiment.magnitude

# one message
class DiscussionChuck:
    def __init__(self, _usid, _message, _order):
        self.user_id = _usid
        self.message = _message
        self.order = _order
        self.entity_sentiment_list = list()
        self.whole_sentiment_data = dict()


    def remove_quote_link(self, keep_quote=True, keep_link=True):
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
        return _message

    # generate entity sentiment
    # Watson NLP Mode
    # @param keep_quote True or False
    # @param keep_link True or False
    def gen_watson_entity_sentiment(self, keep_quote=True, keep_link=True):
        _message = self.remove_quote_link(keep_quote, keep_link)

        sentiment_result = watson_entity_extraction(_message)

        all_entities = sentiment_result['entities']
        self.entity_sentiment_list = [(entity['text'], [entity['sentiment']['score']]) for entity in all_entities]

    # generate entity sentiment
    # Google NLP Mode
    # @param keep_quote True or False
    # @param keep_link True or False
    def gen_google_entity_sentiment(self, keep_quote=True, keep_link=True):
        _message = self.remove_quote_link(keep_quote, keep_link)

        all_entities = google_entity_extraction(_message)

        self.entity_sentiment_list = [(entity[0], [entity[1], entity[2]]) for entity in all_entities]

    # generate all sentiment data
    # includes
    # - user id
    # - sentence sentiment/mag
    # - entity sentiment/mag
    # - overall sentiment/mag
    def gen_google_all_data(self, keep_quote=True, keep_link=True):
        _message = self.remove_quote_link(keep_quote, keep_link)
        self.whole_sentiment_data["userid"] = self.user_id
        self.whole_sentiment_data["entities"] = google_entity_extraction_detailed(_message)

        # sentence and document
        sentiment_data = google_sentence_extraction(_message)
        self.whole_sentiment_data["sentences"] = sentiment_data[0]
        self.whole_sentiment_data["score"] = sentiment_data[1]
        self.whole_sentiment_data["magnitude"] = sentiment_data[2]


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




