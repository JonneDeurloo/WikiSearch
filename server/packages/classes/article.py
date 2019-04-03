import json


class Article(object):
    __pagerank = 0.0
    __cosine_sim = 0.0
    __topics = []

    # Add other variables if needed

    def __init__(self, id, title, text):
        self.id = id
        self.title = title
        self.text = text

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(('id', self.id))

    def get_json(self):
        data = {}
        data['title'] = self.title
        data['text'] = self.text
        data['cosine_sim'] = self.__cosine_sim
        data['pagerank'] = self.__pagerank
        data['topics'] = self.__topics
        data['harmonic_mean'] = self.get_harmonic_mean()

        return data

    def set_pagerank(self, pagerank):
        self.__pagerank = float(pagerank)

    def get_pagerank(self):
        return self.__pagerank

    def set_topics(self, topics):
        self.__topics = topics

    def get_topics(self):
        return self.__topics

    def set_similarity(self, similarity):
        self.__cosine_sim = float(similarity)

    def get_similarity(self):
        return self.__cosine_sim

    def get_harmonic_mean(self):
        top = self.__pagerank * self.__cosine_sim
        bottom = 50000 * self.__pagerank +  self.__cosine_sim
        return top / bottom
