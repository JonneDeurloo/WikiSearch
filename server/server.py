import json

from modules.pagerank import pagerank
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def hello():
	db = pagerank.create_connection()
	pagerank.create_graph(db)
	pr = pagerank.create_pagerank()
	return jsonify(pagerank.sort_on_pagerank(pr, ["P", "G", "C", "B"]))


if __name__ == '__main__':
	app.run(debug=True)