import django
from pathlib import Path


def pytest_configure(config):
    from django.conf import settings

    BASE_DIR = Path(__file__).resolve().parent

    settings.configure(
        SECRET_KEY="test",
        BASE_DIR=BASE_DIR,
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
        INSTALLED_APPS=[
            # "django.contrib.messages",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            # "django.contrib.sessions",
            "django.contrib.sites",
            "gdaps",
            "conjunto",
            "tests.test_app",
        ],
        PLUGIN1={"OVERRIDE": 20},
        PROJECT_NAME="foo_bar",
        PROJECT_TITLE="Foo Bar",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [BASE_DIR / "templates"],
                "APP_DIRS": True,
            },
        ],
    )

    django.setup()
