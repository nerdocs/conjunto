import logging
import os
from pathlib import Path

import requests
from django.apps import apps
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Download libraries and save them into the static folder.

    The `libraries` dict has the name of the library as key, and a list of
    3-tuples, each containing:
      - the local file path of the downloaded file
      - the URL to download the file
      - a mode how to write the file: "w" for text files, "wb" for binary files like
        icon fonts

    """

    unpkg_path = "https://unpkg.com"
    # tabler-icons:
    ti_version = "3.31.0"
    ti_path = f"https://unpkg.com/@tabler/icons-webfont@{ti_version}/dist"
    tabler_version = "1.2.0"
    tabler_path = f"https://cdn.jsdelivr.net/npm/@tabler/core@{tabler_version}/dist"

    libraries: dict[str, list[tuple[str, str, str]]] = {
        "dropzone": [
            (
                "js/dropzone.min.js",
                f"{unpkg_path}/dropzone@5/dist/min/dropzone.min.js",
                "w",
            ),
            (
                "js/dropzone.js",
                f"{unpkg_path}/dropzone@5/dist/dropzone.js",
                "w",
            ),
            (
                "css/dropzone.min.css",
                f"{unpkg_path}/dropzone@5/dist/min/dropzone.min.css",
                "w",
            ),
            (
                "css/dropzone.css",
                f"{unpkg_path}/dropzone@5/dist/dropzone.css",
                "w",
            ),
        ],
        "htmx": [
            ("js/htmx/htmx.js", "https://unpkg.com/htmx.org@latest/dist/htmx.js", "w"),
            (
                "js/htmx/htmx.min.js",
                f"{unpkg_path}/htmx.org@latest/dist/htmx.min.js",
                "w",
            ),
            (
                "js/htmx/ext/ws.js",
                f"{unpkg_path}/htmx.org@latest/dist/ext/ws.js",
                "w",
            ),
            (
                "js/htmx/ext/debug.js",
                f"{unpkg_path}/htmx.org@latest/dist/ext/debug.js",
                "w",
            ),
        ],
        # "bootstrap": [
        #     (
        #         "js/bootstrap.bundle.min.js",
        #         f"{unpkg_path}/bootstrap@latest/dist/js/bootstrap.bundle.min.js",
        #         "w",
        #     ),
        #     (
        #         "js/bootstrap.bundle.min.js.map",
        #         f"{unpkg_path}/bootstrap@latest/dist/js/bootstrap.bundle.min
        #         .js.map",
        #         "w",
        #     ),
        #     (
        #         "css/bootstrap.min.css",
        #         f"{unpkg_path}/bootstrap@latest/dist/css/bootstrap.min.css",
        #         "w",
        #     ),
        #     (
        #         "css/bootstrap.min.css.map",
        #         f"{unpkg_path}/bootstrap@latest/dist/css/bootstrap.min.css.map",
        #         "w",
        #     ),
        # ],
        "bootstrap-icons": [
            (
                "css/bootstrap-icons.css",
                f"{unpkg_path}/bootstrap-icons@latest/font/bootstrap-icons.css",
                "w",
            ),
            (
                "css/fonts/bootstrap-icons.woff",
                f"{unpkg_path}/bootstrap-icons@latest/font/fonts/bootstrap-icons.woff",
                "wb",
            ),
            (
                "css/fonts/bootstrap-icons.woff2",
                f"{unpkg_path}/bootstrap-icons@latest/font/fonts/bootstrap-icons.woff2",
                "wb",
            ),
        ],
        "sortable": [
            (
                "js/Sortable.min.js",
                "https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js",
                "w",
            ),
            (
                "js/Sortable.js",
                "https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.js",
                "w",
            ),
        ],
        "tabler": [
            (
                "css/tabler.css",
                f"{tabler_path}/css/tabler.css",
                "w",
            ),
            (
                "css/tabler.min.css",
                f"{tabler_path}/css/tabler.min.css",
                "w",
            ),
            (
                "js/tabler.js",
                f"{tabler_path}/js/tabler.js",
                "w",
            ),
            (
                "js/tabler.min.js",
                f"{tabler_path}/js/tabler.min.js",
                "w",
            ),
            (
                "css/fonts/tabler-icons.woff",
                f"{ti_path}/fonts/tabler-icons.woff",
                "wb",
            ),
            (
                "css/fonts/tabler-icons.woff2",
                f"{ti_path}/fonts/tabler-icons.woff2",
                "wb",
            ),
            (
                "css/tabler-icons.css",
                f"{ti_path}/tabler-icons.css",
                "w",
            ),
            (
                "css/tabler-icons.min.css",
                f"{ti_path}/tabler-icons.min.css",
                "w",
            ),
        ],
        "litepicker": [
            (
                "js/litepicker.js",
                f"{unpkg_path}/litepicker/dist/litepicker.js",
                "w",
            )
        ],
        "alpine": [
            (
                "js/alpine.js",
                f"{unpkg_path}/alpinejs/dist/cdn.js",
                "w",
            ),
            (
                "js/alpine.min.js",
                f"{unpkg_path}/alpinejs/dist/cdn.min.js",
                "w",
            ),
        ],
        "fslightbox": [
            (
                "js/fslightbox.js",
                f"{unpkg_path}/fslightbox",
                "w",
            ),
        ],
        "chartjs": [
            (
                "js/chart.min.js",
                f"{unpkg_path}/chart.js@4.4.9/dist/chart.umd.js",
                "w",
            )
        ],
    }
    help = (
        "DEV COMMAND: downloads needed Javascript/CSS libraries and fonts for "
        "Conjunto."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "library",
            help="Specify the library to download. Available are: "
            f"{[lib for lib in self.libraries]}",
        )

    def handle(self, *args, **options):
        target_path_root = (
            Path(apps.get_app_config("conjunto").path) / "static" / "conjunto"
        )
        if options["library"] not in self.libraries:
            return (
                f"No library named '{options['library']}' found. Available are:"
                f" {[lib for lib in self.libraries]}"
            )

        library = self.libraries[options["library"]]
        for file_name, url, mode in library:
            data = requests.get(url)
            if data.status_code != 200:
                self.stderr.write(f"Could not read {url}")
            else:
                os.makedirs(
                    os.path.dirname(target_path_root / file_name), exist_ok=True
                )
                self.stdout.write(f"{file_name}, {url}")
                with open(target_path_root / file_name, mode) as f:
                    if mode == "w":
                        f.write(data.text)
                    elif mode == "wb":
                        f.write(data.content)
