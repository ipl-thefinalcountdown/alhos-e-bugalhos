'''
alhos_e_bugalhos
'''

import collections
import functools
import os.path
import uuid

import fastapi
import fastapi.staticfiles
import mako.exceptions
import mako.lookup
import mako.template
import tomlkit

from fastapi.responses import HTMLResponse, RedirectResponse

# import to make sure they are in __subclasses__
import alhos_e_bugalhos.connections.backends  # noqa: F401
import alhos_e_bugalhos.connections.frontends  # noqa: F401

from alhos_e_bugalhos.connections import Backend, Connection, Frontend, MultipleSettingError, SettingError


__version__ = '0.0.0b0'


app = fastapi.FastAPI()

img_directory = os.path.abspath(os.path.join(__file__, '..', '..', 'img'))

app.mount('/img', fastapi.staticfiles.StaticFiles(directory=img_directory), name='img')

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

available_text_settings = {
    'input': {
        backend.TYPE_NAME: backend.TEXT_SETTINGS
        for backend in Backend.__subclasses__()
    },
    'output': {
        frontend.TYPE_NAME: frontend.TEXT_SETTINGS
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

active_connections = {}


def load_settings():
    if 'AEB_CONFIG' in os.environ:
        try:
            with open(os.environ['AEB_CONFIG'], 'r') as f:
                return tomlkit.parse(f.read())
        except FileNotFoundError:
            pass
    return {}


def save_settings():
    if 'AEB_CONFIG' not in os.environ:
        return
    data = {}
    for key, connection in active_connections.items():
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
        # XXX skip generated settings
        for target in ('input', 'output'):
            for name, value in data[key][target]['settings'].copy().items():
                if '@HOST@' in value:
                    del data[key][target]['settings'][name]
            if not data[key][target]['settings']:
                del data[key][target]['settings']
    with open(os.environ['AEB_CONFIG'], 'w') as f:
        f.write(tomlkit.dumps(data))


providers = {}
for name, data in load_settings().items():
    if 'name' not in data:
        raise SettingError(f'Missing key in config: {name}.name')
    for target in ('input', 'output'):
        if target not in data:
            raise SettingError(f'Missing section in config: {name}.{target}')
        if 'type' not in data[target]:
            raise SettingError(f'Missing section in config: {name}.{target}.type')
        provider_cls = available_providers[target][data[target]['type']]
        providers[target] = provider_cls(data[target].get('settings', {}))
    active_connections[name] = Connection(
        data['name'],
        providers['input'],
        providers['output'],
    )


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
async def root(request: fastapi.Request):
    return {
        'request': request,
        'connections': active_connections.values(),
        'available_settings': available_settings,
        'available_text_settings': available_text_settings,
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
        active_connections[uuid.uuid4()] = Connection(
            connection_name,
            providers['input'],
            providers['output'],
        )
        validate = False
        save_settings()

    return {
        'request': request,
        'connections': active_connections.values(),
        'available_settings': available_settings,
        'available_text_settings': available_text_settings,
        'validate': validate,
        'single_error': single_error,
        'errors': errors,
        'form': await request.form(),
    }


@app.get('/delete/{id}', response_class=HTMLResponse)
async def delete(id: int, request: fastapi.Request):
    del active_connections[list(active_connections.keys())[id]]
    save_settings()
    return RedirectResponse(url='/')


@app.get('/edit/{id}', response_class=HTMLResponse)
@template('edit')
async def edit(id: int, request: fastapi.Request):
    # TODO: handle invalid ID
    return {
        'request': request,
        'connection': list(active_connections.values())[id],
        'available_text_settings': available_text_settings,
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
            getattr(list(active_connections.values())[id], target).update_setting(name, value)
        except SettingError as e:
            # TODO: customize the exception
            errors[target][name].append(e.args[0])

    save_settings()

    return {
        'request': request,
        'connection': list(active_connections.values())[id],
        'available_text_settings': available_text_settings,
        'validate': True,
        'errors': errors,
        'form': await request.form(),
    }
