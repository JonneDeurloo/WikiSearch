import json


class Article(object):
    pagerank = 0.0

    def __init__(self, id, title, text):
        self.id = id
        self.title = title
        self.text = text

    def get_json(self):
        data = {}
        data['id'] = self.id
        data['title'] = self.title
        data['text'] = self.text
        data['pagerank'] = self.pagerank

        return data

    def set_pagerank(self, pagerank):
        self.pagerank = pagerank
