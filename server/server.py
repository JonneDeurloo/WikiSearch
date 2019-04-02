import json
import time

from packages.pagerank import pagerank
from packages.indexing import indexing
from packages.indexing import firstlines
from packages.clustering import clustering
from packages.topic_modeling import topic_modeling as tm

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

dataset = 'enwiki-20190301'


@app.route("/")
def hello():
    return get_succes_page("Hello!")


@app.route("/search")
@cross_origin()
def search():
    query = request.args.get('q', default='', type=str)
    # query parser
    parsed_query = None

    # get matching articles
    matched = None

    # find related articles
    clustering.create_connection()
    related = clustering.get_articles(query.replace(',', ' '))

    # rank articles based on PageRank
    pagerank.create_connection()
    pageranked = pagerank.get_pagerank(related)
    sort = sorted(pageranked, key=lambda x: x.get_pagerank(), reverse=True)
    return jsonify(create_json(sort))


@app.route("/pagerank")
def build_pagerank():
    pagerank.create_connection()
    pagerank.create_pagerank(dataset)
    return get_succes_page("PageRank created!")


@app.route("/firstlines")
def build_wiki():
    firstlines.create_connection()
    firstlines.create_table_wiki()
    firstlines.create_wiki()
    return get_succes_page("Wiki created!")

@app.route("/clustering")
def build_clustering():
    clustering.create_cluster()
    clustering.create_rcluster()
    return get_succes_page("Clustering done!")


@app.route("/indexing")
def build_indexing():
    indexing.create_connection()
    indexing.create_indexing(dataset, force=True)
    return get_succes_page("Indexing created!")


@app.route("/links")
def build_links():
    pagerank.create_connection()
    pagerank.create_table_pagerank()
    pagerank.find_links(dataset)
    return get_succes_page("Links created!")


def create_json(articles):
    jsoned = []
    for article in articles:
        jsoned.append(article.get_json())
    return jsoned


def get_succes_page(text):
    return f"<div style='position: absolute; top: 0; bottom: 0; left: 0; right: 0; display: flex; justify-content: center; align-items: center;'>{text}</div>"


if __name__ == '__main__':
    app.run(debug=True)
