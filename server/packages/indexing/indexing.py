from ..common.article import Article

def get_similar(query):
    a1 = Article(1, query, "This is the first result")
    a2 = Article(2, "B", "This is the second result")
    a3 = Article(3, "D", "This is the thirth result")
    a4 = Article(4, "P", "This is the fourth result")
    return [a1, a2, a3, a4]