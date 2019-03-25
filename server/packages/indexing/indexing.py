#from ..common.article import Article
import sys
import os
from nltk.corpus import stopwords

def article_list(file):

    articles = []
    with open(file, 'r', encoding="utf8") as tf:
        index = 0
        for line in tf:
            line = line.replace('\n', ' ').replace('\t', ' ')
            split = line.split(' ', 1)
            if split[0] == '#Article:':
                #print('Article line')
                articles.append(split[1])
                index += 1
            elif line == ' ' or line[0] == '#':
                continue
            else:
                #print('Normal line')
                articles[index-1] += line

    return articles

def tokenize_article(art_text):

    en_stops = stopwords.words('english')
    art_text = art_text.lower()

    text_arr = art_text.split(' ')




file = "articles_in_plain_text.txt"
art = article_list(file)
print(art[0])
print("================================================================================================================================")
print(art[1])
print("================================================================================================================================")
print(art[2])





#from ..common.article.article import Article

#def get_similar(query):
#    a1 = Article(1, query, "This is the first result")
#    a2 = Article(2, "Planet", "This is the second result")
#    a3 = Article(3, "Mars", "This is the thirth result")
#    a4 = Article(4, "Jupiter", "This is the fourth result")
#    return [a1, a2, a3, a4]
