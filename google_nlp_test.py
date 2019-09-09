import six
from google.cloud import language_v1
from google.cloud.language import enums
from google.cloud.language import types
import json

text = '''So yeah, MIT is a large school and offers a number of opportunities due to its size. Caltech is also a great school and with great research opportunities due to the closeness you can have with professors.

But when you consider Caltech, you must place emphasis not only on the <i>diverse</i> course offering, but on other aspects as well.

Research is a keyfactor. Why would I say that? The faculty members accessibility is something notable in Caltech. My point is, when your mentor is a faculty member, who's readily accessible, and thus help you through you research, your reserach would definitely yield better results.

Another point worth mentioning is the fact that Caltech's curriculum tends to follow a theoretical approach.

So you see, it all depends on your expectaion and objectives (yes you have to know what you're targetting in the end).

My main focus was on the research opportunities. Thus, Caltech is the school that appealed to me.

Remember, this is just my opinion. I would love to see a debate of this topic, namely from Engineering students of both schools, who could give us firsthand experience of their majors.
    '''

client = language_v1.LanguageServiceClient()

if isinstance(text, six.binary_type):
    text = text.decode('utf-8')

sentence_data_list = list()

document = types.Document(
    content=text.encode('utf-8'),
    type=enums.Document.Type.PLAIN_TEXT)

encoding_type = enums.EncodingType.UTF8

result = client.analyze_entity_sentiment(document, encoding_type=encoding_type)

entity_data_list = list()

for entity in result.entities:
    entity_dict = dict()
    entity_dict["name"] = entity.name
    entity_dict["mentions"] = list()
    for mention in entity.mentions:
        mention_dict = dict()
        mention_dict["content"] = mention.text.content
        mention_dict["order"] = mention.text.begin_offset
        print(mention)
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
print(all_orders)
for i in range(len(entity_data_list)):
    for j in range(len(entity_data_list[i]["mentions"])):
        off_set_order = entity_data_list[i]["mentions"][j]["order"]
        entity_data_list[i]["mentions"][j]["order"] = all_orders.index(off_set_order) + 1

#print(json.dumps(entity_data_list, sort_keys=True, indent=4))