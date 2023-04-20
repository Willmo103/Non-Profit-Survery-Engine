import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your_secret_key_here"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "survey.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = True


# TODO create a unified store of environment variables, either in dockerfile or in config.py,
# but remove the redundancy of having them in both places
