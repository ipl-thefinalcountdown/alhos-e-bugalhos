'''
alhos_e_bugalhos
'''

import collections
import functools
import os.path

import fastapi
import mako.exceptions
import mako.lookup
import mako.template
import toml

from fastapi.responses import HTMLResponse

from alhos_e_bugalhos.connections import Backend, Connection, Frontend, MultipleSettingError, SettingError
from alhos_e_bugalhos.connections.example import ExampleBackend, ExampleFrontend


__version__ = '0.0.0b0'


app = fastapi.FastAPI()

templates = mako.lookup.TemplateLookup(directories=[
    os.path.join(os.path.dirname(__file__), 'templates')
])


available_settings = {
    'input': {
        backend.TYPE_NAME: backend.SETTINGS
        for backend in Backend.__subclasses__()
    },
    'output': {
        frontend.TYPE_NAME: frontend.SETTINGS
        for frontend in Frontend.__subclasses__()
    },
}

available_providers = {
    'input': {
        backend.TYPE_NAME: backend
        for backend in Backend.__subclasses__()
    },
    'output': {
        frontend.TYPE_NAME: frontend
        for frontend in Frontend.__subclasses__()
    },
}

active_connections = []


def load_settings():
    if 'AEB_CONFIG' in os.environ:
        with open(os.environ['AEB_CONFIG']) as f:
            return toml.loads(f.read())
    return {}


def save_settings():
    if 'AEB_CONFIG' not in os.environ:
        return
    data = {}
    for connection in active_connections:
        key = str(id(connection.name))
        data[key] = {}
        data[key]['name'] = connection.name
        data[key]['input'] = {
            'type': connection.input.TYPE_NAME,
            'settings': connection.input.settings,
        }
        data[key]['output'] = {
            'type': connection.output.TYPE_NAME,
            'settings': connection.output.settings,
        }
    from pprint import pprint
    pprint(data)
    with open(os.environ['AEB_CONFIG'], 'w') as f:
        f.write(toml.dumps(data))


providers = {}
for name, data in load_settings().items():
    if 'name' not in data:
        raise SettingError(f'Missing key in config: {name}.name')
    for target in ('input', 'output'):
        if target not in data:
            raise SettingError(f'Missing section in config: {name}.{target}')
        for key in ('type', 'settings'):
            if key not in data[target]:
                raise SettingError(f'Missing section in config: {name}.{target}.{key}')
        provider_cls = available_providers[target][data[target]['type']]
        providers[target] = provider_cls(data[target]['settings'])
    active_connections.append(Connection(
        data['name'],
        providers['input'],
        providers['output'],
    ))


def template(name):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            render_params = await func(*args, **kwargs)
            try:
                return templates.get_template(
                    f'{name}.html'
                ).render(**render_params)
            except Exception:
                return mako.exceptions.html_error_template().render()
        return wrapper
    return decorator


@app.get('/', response_class=HTMLResponse)
@template('index')
async def root():
    return {
        'connections': active_connections,
        'available_settings': available_settings,
    }


@app.post('/', response_class=HTMLResponse)
@template('index')
async def add_form(request: fastapi.Request):  # noqa: C901
    validate = True
    connection_name = None
    # target, name, error string
    provider = {
        'input': None,
        'output': None,
    }
    arguments = {
        'input': {},
        'output': {},
    }
    arguments = {
        'input': collections.defaultdict(dict),
        'output': collections.defaultdict(dict),
    }
    errors = {
        'input': {},
        'output': {},
    }
    single_error = None

    # get form data
    for key, value in (await request.form()).items():
        if key == 'select-input':
            provider['input'] = value
        elif key == 'select-output':
            provider['output'] = value
        elif key == 'connection-name':
            connection_name = value
        else:
            provider_type, target, name = key.split('-', maxsplit=2)

            if target == provider[provider_type]:
                arguments[provider_type][name] = value

    if not connection_name:
        errors['connection-name'] = 'Invalid name.'

    # create providers (frontend and backend)
    providers = {}
    for type_ in ('input', 'output'):
        try:
            provider_cls = available_providers[type_][provider[type_]]
            providers[type_] = provider_cls(arguments[type_])
        except KeyError:
            errors[type_]['select'] = 'Please select a type.'
        except SettingError as e:
            single_error = e.args[0]
        except MultipleSettingError as e:
            errors[type_] = e.errors

    # add connection
    if 'input' in providers and 'output' in providers and connection_name:
        active_connections.append(Connection(
            connection_name,
            providers['input'],
            providers['output'],
        ))
        save_settings()
        validate = False

    return {
        'connections': active_connections,
        'available_settings': available_settings,
        'validate': validate,
        'single_error': single_error,
        'errors': errors,
        'form': await request.form(),
    }


@app.get('/edit/{id}', response_class=HTMLResponse)
@template('edit')
async def edit(id: int):
    # TODO: handle invalid ID
    return {
        'connection': active_connections[id],
    }


@app.post('/edit/{id}', response_class=HTMLResponse)
@template('edit')
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

    save_settings()

    return {
        'connection': active_connections[id],
        'validate': True,
        'errors': errors,
        'form': await request.form(),
    }
