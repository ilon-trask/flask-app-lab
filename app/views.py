from flask import render_template
from . import app
from dataclasses import dataclass


@app.route("/")
def index():
    return render_template("index.html", title="Home")


@dataclass()
class ResumeDetails:
    full_name: str
    role: str
    summary: str


RESUME_DETAILS = ResumeDetails(
    full_name="Demo Student",
    role="Flask Developer",
    summary="This page is included to satisfy the navigation requirement from the assignment.",
)


@app.get("/resume")
def resume():
    return render_template("resume.html", title="Resume", resume=RESUME_DETAILS)
