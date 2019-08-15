"""
The design of DiscussionChuck is to provide the generic class for discussion data processing
It includes message ordering, sentiment analyze and so on

"""

# one message
class DiscussionChuck:
    def __init__(self, _usid, _message, _order):
        self.user_id = _usid
        self.message = _message
        self.order = _order
        self.entity_sentiment_dict = dict()


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




