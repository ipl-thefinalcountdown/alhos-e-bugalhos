'''
alhos_e_bugalhos
'''

import collections
import os.path

import fastapi
import mako.lookup
import mako.template

from fastapi.responses import HTMLResponse

from alhos_e_bugalhos.connections import Backend, Connection, Frontend, SettingError
from alhos_e_bugalhos.connections.example import ExampleBackend, ExampleFrontend


__version__ = '0.0.0b0'


app = fastapi.FastAPI()

templates = mako.lookup.TemplateLookup(directories=[
    os.path.join(os.path.dirname(__file__), 'templates')
])

active_connections = [
    Connection(
        'Example 1',
        ExampleBackend({
            'Host': '0.0.0.0',
            'Port': 8081,
        }),
        ExampleFrontend({
            'URL': 'http://localhost/example1',
        }),
    ),
    Connection(
        'Example 2',
        ExampleBackend({
            'Host': '0.0.0.0',
            'Port': 8082,
        }),
        ExampleFrontend({
            'URL': 'http://localhost/example2',
        }),
    ),
    Connection(
        'Example 3',
        ExampleBackend({
            'Host': '0.0.0.0',
            'Port': 8083,
        }),
        ExampleFrontend({
            'URL': 'http://localhost/example3',
        }),
    ),
    Connection(
        'Example 4',
        ExampleBackend({
            'Host': '0.0.0.0',
            'Port': 8084,
        }),
        ExampleFrontend({
            'URL': 'http://localhost/example4',
        }),
    ),
    Connection(
        'Example 5',
        ExampleBackend({
            'Host': '0.0.0.0',
            'Port': 8085,
        }),
        ExampleFrontend({
            'URL': 'http://localhost/example5',
        }),
    ),
    Connection(
        'Example 6',
        ExampleBackend({
            'Host': '0.0.0.0',
            'Port': 8086,
        }),
        ExampleFrontend({
            'URL': 'http://localhost/example6',
        }),
    ),
]


@app.get('/', response_class=HTMLResponse)
async def root():
    return templates.get_template('index.html').render(
        connections=active_connections,
    )


@app.get('/edit/{id}', response_class=HTMLResponse)
async def edit(id: int):
    # TODO: handle invalid ID
    return templates.get_template('edit.html').render(
        connection=active_connections[id],
    )


@app.post('/edit/{id}', response_class=HTMLResponse)
async def edit_form(id: int, request: fastapi.Request):
    # target, name, error string
    errors = {
        'input': collections.defaultdict(list),
        'output': collections.defaultdict(list),
    }

    for key, value in (await request.form()).items():
        target, name = key.split('-', maxsplit=1)  # XXX !! only 1 worded names supported
        try:
            getattr(active_connections[id], target).update_setting(name, value)
        except SettingError as e:
            # TODO: customize the exception
            errors[target][name].append(e.args[0])

    return templates.get_template('edit.html').render(
        connection=active_connections[id],
        validate=True,
        errors=errors,
        form=await request.form(),
    )
