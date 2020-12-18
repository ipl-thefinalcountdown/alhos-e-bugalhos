import csv
import io
import uuid

import dicttoxml
import fastapi
import json2html
import yaml

from fastapi.responses import HTMLResponse, PlainTextResponse

import alhos_e_bugalhos
import alhos_e_bugalhos.connections


class HTMLFrontend(alhos_e_bugalhos.connections.Frontend):
    TYPE_NAME = 'HTML'
    SETTINGS = {}

    def register(self, get_data):
        self._id = uuid.uuid4()
        self._app = fastapi.FastAPI()

        @self._app.get('/', response_class=HTMLResponse)
        def dispatch():
            return json2html.json2html.convert(json=get_data())

        self._settings['URL'] = f'@HOST@/{self._id}'

        alhos_e_bugalhos.app.mount(f'/{self._id}', self._app)

    def unresgister(self):
        # fastapi doesn't let us remove the mount so we replace it
        alhos_e_bugalhos.app.mount(f'/{self._id}', fastapi.FastAPI())


class RESTJsonFrontend(alhos_e_bugalhos.connections.Frontend):
    TYPE_NAME = 'REST JSON'
    SETTINGS = {}

    def register(self, get_data):
        self._id = uuid.uuid4()
        self._app = fastapi.FastAPI()

        @self._app.get('/')
        def dispatch():
            return get_data()

        self._settings['URL'] = f'@HOST@/{self._id}'

        alhos_e_bugalhos.app.mount(f'/{self._id}', self._app)

    def unresgister(self):
        # fastapi doesn't let us remove the mount so we replace it
        alhos_e_bugalhos.app.mount(f'/{self._id}', fastapi.FastAPI())


class XMLFrontend(alhos_e_bugalhos.connections.Frontend):
    TYPE_NAME = 'XML'
    SETTINGS = {}

    def register(self, get_data):
        self._id = uuid.uuid4()
        self._app = fastapi.FastAPI()

        @self._app.get('/', response_class=PlainTextResponse)
        def dispatch():
            return dicttoxml.dicttoxml(get_data())

        self._settings['URL'] = f'@HOST@/{self._id}'

        alhos_e_bugalhos.app.mount(f'/{self._id}', self._app)

    def unresgister(self):
        # fastapi doesn't let us remove the mount so we replace it
        alhos_e_bugalhos.app.mount(f'/{self._id}', fastapi.FastAPI())


class CSVFrontend(alhos_e_bugalhos.connections.Frontend):
    TYPE_NAME = 'CSV'
    SETTINGS = {}

    def register(self, get_data):
        self._id = uuid.uuid4()
        self._app = fastapi.FastAPI()

        @self._app.get('/', response_class=PlainTextResponse)
        def dispatch():
            data = get_data()
            xml_data = io.StringIO()
            writer = csv.DictWriter(xml_data, fieldnames=data.keys())
            writer.writeheader()
            writer.writerow(data)
            return xml_data.getvalue()

        self._settings['URL'] = f'@HOST@/{self._id}'

        alhos_e_bugalhos.app.mount(f'/{self._id}', self._app)

    def unresgister(self):
        # fastapi doesn't let us remove the mount so we replace it
        alhos_e_bugalhos.app.mount(f'/{self._id}', fastapi.FastAPI())


class YAMLFrontend(alhos_e_bugalhos.connections.Frontend):
    TYPE_NAME = 'YAML'
    SETTINGS = {}

    def register(self, get_data):
        self._id = uuid.uuid4()
        self._app = fastapi.FastAPI()

        @self._app.get('/', response_class=PlainTextResponse)
        def dispatch():
            return yaml.dump(get_data())

        self._settings['URL'] = f'@HOST@/{self._id}'

        alhos_e_bugalhos.app.mount(f'/{self._id}', self._app)

    def unresgister(self):
        # fastapi doesn't let us remove the mount so we replace it
        alhos_e_bugalhos.app.mount(f'/{self._id}', fastapi.FastAPI())
