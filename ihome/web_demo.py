from flask import Blueprint

html = Blueprint("web_html", __name__)


@html.route("/<re(r'.*'):file_name>")
def get_html():
    """�ṩhtml�ļ�"""
    pass
