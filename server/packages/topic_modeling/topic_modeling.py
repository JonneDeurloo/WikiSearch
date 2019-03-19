from ..common.article import Article

def get_related(articles):
    related = []
    #for article in articles:
    a = Article(6, 'F', 'This is the nth result')
    related.append(a)
    return articles + related