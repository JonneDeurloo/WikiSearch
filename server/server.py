import json

from flask import Flask, jsonify, request

from packages.pagerank import pagerank
from packages.clustering import clustering
from packages.indexing import indexing
from packages.topic_modeling import topic_modeling as tm

from packages.common.article import Article



app = Flask(__name__)


@app.route("/")
def hello():

    return "Hello world!"


@app.route("/search")
def search():
    query = request.args.get('q', default='', type = str)
    indexed = indexing.get_similar(query)
    topics = tm.get_related(indexed)
    db = pagerank.create_connection()
    pagerank.create_graph(db)
    pr = pagerank.create_pagerank()
    ranked = pagerank.sort_on_pagerank(topics)
    return jsonify(create_json(ranked))

def create_json(articles):
    jsoned = []
    for article in articles:
        jsoned.append(article.get_json())
    return jsoned

if __name__ == '__main__':
    app.run(debug=True)
