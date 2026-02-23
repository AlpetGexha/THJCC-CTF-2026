"""Module providing a function generating random text."""

import random
import string
from urllib.parse import urlparse

import joblib
import markdown
from bs4 import BeautifulSoup
from flask import current_app
from markupsafe import escape


def generate_random_string(length):
    """
    Generating random string
    Args:
        length (int): Length of generated string
    """
    letters = string.ascii_letters
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


def markdown_to_html_secure(markdown_text, img_to_text=False):
    """
    Turn markdown into html content securely
    Args:
        markdown_text (string): Content in Markdown format
        img_to_text (bool,optional): Mark image as (圖片)
    """
    content = markdown.markdown(markdown_text)

    soup = BeautifulSoup(content, "html.parser")
    ps = soup.find_all("p")
    for p in ps:
        try:
            if "\n" in p.string:
                p.string = p.string.replace("\n", "<br>")
        except TypeError:
            pass

    links = soup.find_all("a")
    for link in links:
        if "href" in link.attrs:
            url = link.attrs["href"]
            parsed_result = urlparse(url)
            if parsed_result.scheme not in ["http", "https"]:
                link.attrs["href"] = ""
                link.attrs["target"] = "#"
                link.attrs["rel"] = "noopener noreferrer"
                link.string = "URL已被移除"
            else:
                link.attrs["target"] = "_blank"
                link.attrs["rel"] = "noopener"
                link.attrs["href"] = "/redirect?url=" + link.attrs["href"]

    imgs = soup.find_all("img")
    for img in imgs:
        img.attrs["src"] = (
            current_app.config["IMAGE_PROXY_URL"] + "/" + img.attrs["src"]
        )
        if img_to_text:
            img.string = "(圖片)"

    content = str(soup)
    if escape("<br>") in content:
        content = content.replace(escape("<br>"), "<br>")
    return content


def check_for_spam(text):
    """
    Checks if a given text is spam or not.

    Args:
        text (str): The input text to check.

    Returns:
        int: The prediction, 1 for spam or 0 for not spam.
    """
    model = joblib.load("spam_classifier.joblib")
    vectorizer = joblib.load("vectorizer.joblib")

    text_tfidf = vectorizer.transform([text])

    prediction = model.predict(text_tfidf)

    del model, vectorizer
    return 1 if prediction[0] == "spam" else 0
