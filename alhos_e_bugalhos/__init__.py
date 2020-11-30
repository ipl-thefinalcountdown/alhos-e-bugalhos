'''
alhos_e_bugalhos
'''

import os.path

import fastapi
import mako.lookup
import mako.template

from fastapi.responses import HTMLResponse

from alhos_e_bugalhos.connections import Connection
from alhos_e_bugalhos.connections.example import ExampleBackend, ExampleFrontend


__version__ = '0.0.0b0'


app = fastapi.FastAPI()

templates = mako.lookup.TemplateLookup(directories=[
    os.path.join(os.path.dirname(__file__), 'templates')
])

active_connections = [
    Connection(
        'Example 1',
        ExampleBackend('0.0.0.0', 8080),
        ExampleFrontend('http://localhost/example1'),
    ),
    Connection(
        'Example 2',
        ExampleBackend('0.0.0.0', 8081),
        ExampleFrontend('http://localhost/example2'),
    ),
    Connection(
        'Example 3',
        ExampleBackend('0.0.0.0', 8082),
        ExampleFrontend('http://localhost/example3'),
    ),
    Connection(
        'Example 4',
        ExampleBackend('0.0.0.0', 8083),
        ExampleFrontend('http://localhost/example4'),
    ),
    Connection(
        'Example 5',
        ExampleBackend('0.0.0.0', 8084),
        ExampleFrontend('http://localhost/example5'),
    ),
    Connection(
        'Example 6',
        ExampleBackend('0.0.0.0', 8086),
        ExampleFrontend('http://localhost/example6'),
    ),
]


@app.get('/', response_class=HTMLResponse)
async def root():
    return templates.get_template('index.html').render(
        connections=active_connections,
    )
