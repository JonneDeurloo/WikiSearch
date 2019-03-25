# WikiSearch

This is a project for the course Web Information Retrieval and Data Mining on the TU/e.

## How To

Before using this, make sure you have installed the following packages:

```
pip install flask, flask-cors, networkx
```

After that, make sure that the common folder contains the the folder `dataset/enwiki-20190301` and that this contains the complete datadump.

When these are installed and the dataset is loaded, the pagerank database can be used as follows:

1. Change the cmd directory to `WikiSearch/server` and run the command `python server.py`. This will start the server on `127.0.0.1:5000`.
2. In your browser, navigate to the following webpage: `http://127.0.0.1:5000/wiki` to create and build the test wiki table.
3. Then navigate to: `http://127.0.0.1:5000/pagerank` to create and build the pagerank table.
4. Last, go to the folder `WikiSearch/frontend` and open `index.html`. This will open the webpage that has a connection to the server.
5. Feel free to search for Earth in the search bar!
