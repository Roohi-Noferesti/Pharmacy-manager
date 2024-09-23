# adapters/ui_adapter.py
from flask import Flask, render_template

class UIAdapter:
    def __init__(self):
        self.app = Flask(__name__)

    def run(self):
        self.app.run(debug=True)

    def render_template(self, template_name, **context):
        return render_template(template_name, **context)
