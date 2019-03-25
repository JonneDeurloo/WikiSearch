from ..common.article.article import Article

def get_related(articles):
    articles += [Article(6, 'Sun', 'This is the nth result')]
    for article in articles:
        article.set_topics([article.title, "Another one", "Another one"])
    return articles