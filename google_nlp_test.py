import six
from google.cloud import language
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

client = language.LanguageServiceClient()

if isinstance(text, six.binary_type):
    text = text.decode('utf-8')

sentence_data_list = list()

document = types.Document(
    content=text.encode('utf-8'),
    type=enums.Document.Type.PLAIN_TEXT,
    language="en")

result = client.analyze_sentiment(document)

document_score = result.document_sentiment.score
document_magnitude = result.document_sentiment.magnitude

for sentence in result.sentences:
    sentence_dict = dict()
    sentence_dict["content"] = sentence.text.content
    sentence_dict["score"] = sentence.sentiment.score
    sentence_dict["magnitude"] = sentence.sentiment.magnitude
    sentence_data_list.append(sentence_dict)
print(json.dumps(sentence_data_list, sort_keys=True, indent=4))

