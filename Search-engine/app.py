from flask import Flask, render_template, request, json
import flask
from theguardian_search.articles_search import articles_search

app = flask.Flask(__name__)
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
    app.run()
