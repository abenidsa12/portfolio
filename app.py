from flask import Flask, make_response, redirect, render_template, request, url_for
from flask_mail import Mail, Message
import yaml
from datetime import date
import os
from dotenv import load_dotenv
import pandas as pd

app = Flask(__name__, template_folder='templates')

LANGUAGES = ["en", "de"]
DEFAULT_LANGUAGE = "en"

def load_yaml(lang):
    filename = "info.yaml" if lang == DEFAULT_LANGUAGE else f"info_{lang}.yaml"
    with open(f"static/data/{filename}", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)

def get_language():
    # Explicit choice (?lang=) wins, then the remembered choice, then the browser/system language
    lang = request.args.get("lang")
    if lang in LANGUAGES:
        return lang
    lang = request.cookies.get("lang")
    if lang in LANGUAGES:
        return lang
    return request.accept_languages.best_match(LANGUAGES, default=DEFAULT_LANGUAGE)

@app.route("/")
def home():
    lang = get_language()
    resume_data = load_yaml(lang)
    skills = resume_data['skills']
    mid = len(skills)//2
    skills_l = skills[:mid]
    skills_r = skills[mid:]
    portfolio = resume_data.get('portfolio', [])

    response = make_response(render_template("index.html", data = resume_data, t = resume_data['ui'], lang = lang, skills_l = skills_l, skills_r = skills_r, portfolio = portfolio))
    if request.args.get("lang") in LANGUAGES:
        response.set_cookie("lang", lang, max_age=60*60*24*365, samesite="Lax")
    response.headers["Vary"] = "Accept-Language, Cookie"
    return response

if __name__ == "__main__":
    app.run(debug=False)
