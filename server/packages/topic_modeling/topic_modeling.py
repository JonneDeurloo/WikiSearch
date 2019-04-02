import pickle
import os

from ..classes.article import Article
from ..dbmanager import dbmanager as DBM


def create_connection():
    """ Create a database connection to an SQLite database """

    global db

    db = DBM.create_connection('wiki')


def get_topics(title, ids=False):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    pickle_in = open(dir_path + "/clean_topic_df.pkl", "rb")
    topic_model = pickle.load(pickle_in)

    topics = []

    try:
        if ids:
            topics = topic_model.loc[topic_model['title']
                                     == title, 'topic_id'].iloc[0]
        else:
            topics = topic_model.loc[topic_model['title']
                                     == title, 'topics'].iloc[0]

    except KeyError:
        print("No article with the title '" + title + "'")

    return topics


def add_topics(articles):
    """ Get related articles based on another article """

    result = []

    for article in articles:
        topics = get_topics(article.title)
        article.set_topics(topics)
        result.append(article)

    return result


def get_articles(title):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    pickle_in = open(dir_path + "/topic_id_title.pkl", "rb")
    topic_model_id = pickle.load(pickle_in)

    topic_ids = get_topics(title, True)

    articles = []

    cursor = db.cursor()
    cursor.execute('''SELECT title, text FROM wiki''')
    values = cursor.fetchall()
    values_dict = dict((x, y) for x, y in values)

    for id in topic_ids:
        titles = set(
            topic_model_id.loc[topic_model_id['topic_id'] == id, 'title'].iloc[0])

        for topic_title in titles:
            value = None

            try:
                value = values_dict[topic_title]
            except KeyError:
                print("Can't find article with title '" + topic_title + "'")
            if value != None:
                text = value

                article = Article(topic_title, text)
                articles.append(article)

    pickle_in.close()
    
    return articles
