from flask import Flask, redirect, render_template, request, url_for
from flask_mail import Mail, Message
import yaml
from datetime import date
import os
from dotenv import load_dotenv
import pandas as pd

app = Flask(__name__, template_folder='templates')

def load_yaml():
    with open("static/data/info.yaml") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)

@app.route("/")
def home():
    resume_data = load_yaml()
    skills = resume_data['skills']
    mid = len(skills)//2
    skills_l = skills[:mid]
    skills_r = skills[mid:]
    portfolio = resume_data.get('portfolio', [])

    return render_template("index.html", data = resume_data, skills_l = skills_l, skills_r = skills_r, portfolio = portfolio)

if __name__ == "__main__":
    app.run(debug=False)