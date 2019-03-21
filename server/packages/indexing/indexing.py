from ..common.article.article import Article

def get_similar(query):
    a1 = Article(1, query, "This is the first result")
    a2 = Article(2, "Planet", "This is the second result")
    a3 = Article(3, "Mars", "This is the thirth result")
    a4 = Article(4, "Jupiter", "This is the fourth result")
    return [a1, a2, a3, a4]