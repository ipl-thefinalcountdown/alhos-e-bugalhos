'''
alhos_e_bugalhos
'''

import fastapi

from fastapi.responses import HTMLResponse


__version__ = '0.0.0b0'


app = fastapi.FastAPI()


@app.get('/', response_class=HTMLResponse)
async def root():
    return 'Hello!'
