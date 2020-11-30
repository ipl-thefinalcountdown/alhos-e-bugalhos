'''
alhos_e_bugalhos
'''

import os.path

import fastapi
import mako.lookup
import mako.template

from fastapi.responses import HTMLResponse


__version__ = '0.0.0b0'


app = fastapi.FastAPI()

templates = mako.lookup.TemplateLookup(directories=[
    os.path.join(os.path.dirname(__file__), 'templates')
])

active_connections = []


@app.get('/', response_class=HTMLResponse)
async def root():
    return templates.get_template('index.html').render(
        connections=active_connections,
    )
