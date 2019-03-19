import json


class Article(object):
    __pagerank = 0.0
    __topics = []

    # Add other variables if needed

    def __init__(self, id, title, text):
        self.id = id
        self.title = title
        self.text = text

    def get_json(self):
        data = {}
        data['id'] = self.id
        data['title'] = self.title
        data['text'] = self.text
        data['pagerank'] = self.__pagerank
        data['topics'] = self.__topics

        return data

    def set_pagerank(self, pagerank):
        self.__pagerank = pagerank

    def get_pagerank(self):
        return self.__pagerank

    def set_topics(self, topics):
        self.__topics = topics

    def get_topics(self):
        return self.__topics
