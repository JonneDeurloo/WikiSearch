import json

from packages.pagerank import pagerank
from packages.clustering import clustering
from packages.indexing import indexing
from packages.topic_modeling import topic_modeling as tm

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
def hello():
    return "Hello world!"


@app.route("/search")
@cross_origin()
def search():
    query = request.args.get('q', default='', type=str)
    # queryList = query.split(',')

    # get matching articles
    # create connection with indexing database
    indexed = indexing.get_similar(query)

    # find related articles
    # create connection with topics database
    topics = tm.get_related(indexed)

    # rank articles based on PageRank
    pagerank.create_connection()
    ranked = pagerank.sort_on_pagerank(topics)
    return jsonify(create_json(ranked))


@app.route("/pagerank")
def build_pagerank():
    pagerank.create_connection()
    pagerank.create_pagerank()
    return get_succes_page("PageRank created!")

@app.route("/indexing")
def build_indexing():
    indexing.create_connection()
    indexing.create_indexing()
    return get_succes_page("Indexing created!")


@app.route("/wiki")
def build_wiki():
    pagerank.create_connection()
    pagerank.create_table_wiki()
    pagerank.create_wiki('enwiki-20190301')
    return get_succes_page("WikiDB created!")


def create_json(articles):
    jsoned = []
    for article in articles:
        jsoned.append(article.get_json())
    return jsoned


def get_succes_page(text):
    return f"<div style='position: absolute; top: 0; bottom: 0; left: 0; right: 0; display: flex; justify-content: center; align-items: center;'>{text}</div>"


if __name__ == '__main__':
    app.run(debug=True)
