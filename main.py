from flask import Flask, render_template, render_template_string
from flask import jsonify, send_from_directory, redirect
from flask_frozen import Freezer
import pickle, json
import sys

app = Flask(__name__)
app.config.from_object(__name__)


# Load all for openreview one time.
notes_file = open("openreview_data/json/cached_or.json", "r")

notes = json.loads(notes_file.read())
notes_keys = list(notes.keys())

notes_file.close()

# Reading paper records
paper_recs_file = open("openreview_data/json/paper_records.json", 'r')
paper_recs = json.loads(paper_recs_file.read())
paper_recs_file.close()

# Reading author records
author_recs_file = open("openreview_data/json/author_records.json", 'r')
author_recs = json.loads(author_recs_file.read())
author_recs_file.close()


titles = {}
keywords = {}

for i, (k,n) in enumerate(notes.items()):
    n["content"]["iclr_id"] = k
    titles[n["content"]["title"]] = k
    if "TL;DR" in n["content"]:
        n["content"]["TLDR"] = n["content"]["TL;DR"]
    else:
        n["content"]["TLDR"] = n["content"]["abstract"][:250] + "..."
    for k in n["content"]["keywords"]:
        keywords.setdefault(k.lower(), [])
        keywords[k.lower()].append(n)


# ENDPOINTS

@app.route('/')
def index():
    return redirect('/index.html')


@app.route('/index.html')
def home():
    return render_template('pages/home.html', **{})


@app.route('/livestream.html')
def livestream():
    return render_template('pages/main.html', **{})


@app.route('/papers.html')
def papers():
    data = {"keyword": "all",
            "page": "papers",
            "openreviews": notes.values()}
    return render_template('pages/papers.html', **data)


@app.route('/paper_vis.html')
def paperVis():
    return render_template('pages/papers_vis.html')


@app.route('/papers_old.html')
def papers_old():
    data = {"keyword": "all",
            "openreviews": notes.values()}
    return render_template('pages/keyword.html', **data)


@app.route('/papers.json')
def paper_json():
    paper_list = [value for value in notes.values()]
    return jsonify(paper_list)


@app.route('/recs.html')
def recommendations():
    data = {"choices": author_recs.keys(),
            "keywords": keywords.keys(),
            "titles": titles.keys()}
    return render_template('pages/recs.html', **data)


@app.route('/faq.html')
def faq():
    return render_template('pages/faq.html')

@app.route('/calendar.html')
def schedule():
    return render_template('pages/calendar.html')

@app.route('/socials.html')
def socials():
    return render_template('pages/socials.html')

@app.route('/sponsors.html')
def sponsors():
    return render_template('pages/sponsors.html')

@app.route('/workshops.html')
def workshops():
    return render_template('pages/workshops.html')


# Pull the OpenReview info for a poster.
@app.route('/poster_<poster>.html')
def poster(poster):
    note_id = poster
    data = {"openreview": notes[note_id], "id": note_id,
            "paper_recs" : [notes[n] for n in paper_recs[note_id]][1:]}

    return render_template('pages/page.html', **data)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/embeddings_<emb>.json')
def embeddings(emb):
    try:
        return send_from_directory('static', 'embeddings_'+emb+'.json')
    except FileNotFoundError:
        return ""



# Code to turn it all static
freezer = Freezer(app, with_no_argument_rules=False, log_url_for=False)
@freezer.register_generator
def your_generator_here():
    yield "livestream", {}
    yield "home", {}
    yield "papers", {}
    yield "papers_raw", {}
    yield "paperVis", {}
    yield "papers_v2", {}
    yield "recommendations", {}

    for i in notes.keys():
        yield "poster", {"poster": str(i)}


# Start the app
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(port=5000)
