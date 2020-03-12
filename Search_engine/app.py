import flask
from flask import render_template, request

from Search_engine.articles_search import articles_search

# Creates the Flask application object
app = flask.Flask(__name__)
# Starts the debugger
app.config["DEBUG"] = True


@app.route('/')
def home():
    return render_template("search.html")


@app.route('/search', methods=['GET', 'POST'])
def search():
    for key, value in request.form.items():
        keywords = value
        results = articles_search(keywords)
        return render_template("results.html", res=results)


if __name__ == '__main__':
    # Runs the application server
    app.run()
