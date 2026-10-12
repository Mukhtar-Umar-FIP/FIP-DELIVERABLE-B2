"""
Web front end for the support system.
Run with:  python app.py   then open http://127.0.0.1:5000
"""

import os

from flask import Flask, render_template, request, redirect, url_for

from support_system import SupportSystem, show_replies

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sample_requests.json")

system = SupportSystem()
system.load_from_file(DATA_FILE)

# A short message shown at the top of the page after an action
message = {"text": ""}


def set_message(text):
    message["text"] = text


@app.route("/")
def home():
    sort_by = request.args.get("sort", "date")
    search_text = request.args.get("search", "").strip()

    if search_text:
        found = system.search_by_id(search_text)
        if found:
            requests_list = [found]
        else:
            requests_list = system.search_by_name(search_text)
    else:
        requests_list = system.sort_requests(sort_by)

    text = message["text"]
    set_message("")

    return render_template(
        "index.html",
        requests_list=requests_list,
        queue=list(system.queue),
        sort_by=sort_by,
        search_text=search_text,
        message=text,
        undo_count=len(system.undo_stack),
    )


@app.route("/add", methods=["POST"])
def add():
    added = system.add_request(
        request.form["id"],
        request.form["name"],
        request.form["email"],
        request.form["issue"],
        request.form["date"],
        request.form["priority"],
    )
    if added:
        set_message("Request " + request.form["id"] + " added.")
    else:
        set_message("Could not add: request ID " + request.form["id"] + " already exists or is empty.")
    return redirect(url_for("home"))


@app.route("/process", methods=["POST"])
def process():
    done = system.process_next()
    if done:
        set_message("Processed request " + done["id"] + " (now Resolved).")
    else:
        set_message("The queue is empty.")
    return redirect(url_for("home"))


@app.route("/urgent/<request_id>", methods=["POST"])
def urgent(request_id):
    system.mark_urgent(request_id)
    set_message("Request " + request_id + " marked as High priority.")
    return redirect(url_for("home"))


@app.route("/status/<request_id>", methods=["POST"])
def status(request_id):
    system.update_status(request_id, request.form["status"])
    set_message("Status of " + request_id + " changed to " + request.form["status"] + ".")
    return redirect(url_for("home"))


@app.route("/undo", methods=["POST"])
def undo():
    set_message(system.undo())
    return redirect(url_for("home"))


@app.route("/request/<request_id>")
def view_request(request_id):
    found = system.search_by_id(request_id)
    if found is None:
        set_message("Request " + request_id + " not found.")
        return redirect(url_for("home"))
    return render_template("request.html", req=found, reply_lines=show_replies(found["replies"]))


@app.route("/reply/<request_id>", methods=["POST"])
def reply(request_id):
    system.add_reply(request_id, request.form["message"])
    return redirect(url_for("view_request", request_id=request_id))


if __name__ == "__main__":
    app.run(debug=True)
