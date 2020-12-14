import bs4

import alhos_e_bugalhos


def test_edit_success(client):
    data = {
        'input-Host': '1.1.1.1',
        'input-Port': '8080',
        'output-URL': 'https://localhost/example_edit',
    }

    response = client.post('/edit/0', data=data)

    assert response.status_code == 200

    soup = bs4.BeautifulSoup(response.text)

    for field_name in data:
        field = soup.find(id=field_name)
        assert 'is-valid' in field['class']
        assert 'is-invalid' not in field['class']
        assert not field.parent.find('div', class_='invalid-feedback')

    conn = alhos_e_bugalhos.active_connections[0]
    assert conn.input.settings['Host'] == '1.1.1.1'
    assert conn.input.settings['Port'] == 8080
    assert conn.output.settings['URL'] == 'https://localhost/example_edit'


def test_edit_fail(client):
    conn = alhos_e_bugalhos.active_connections[0]

    conn.input.update_setting('Host', '0.0.0.0')
    conn.input.update_setting('Port', 8081)
    conn.output.update_setting('URL', 'https://localhost/example1')

    response = client.post(
        '/edit/0',
        data={
            'input-Host': '1.1.1.1',
            'input-Port': 'not an int',
            'output-URL': 'not a url',
        },
    )

    assert response.status_code == 200

    soup = bs4.BeautifulSoup(response.text)

    # valid
    field = soup.find(id='input-Host')
    assert 'is-valid' in field['class']
    assert 'is-invalid' not in field['class']
    assert not field.parent.find('div', class_='invalid-feedback')

    # invalid
    for field_name in ('input-Port', 'output-URL'):
        field = soup.find(id=field_name)
        assert 'is-valid' not in field['class']
        assert 'is-invalid' in field['class']
        assert field.parent.find('div', class_='invalid-feedback')

    assert conn.input.settings['Host'] == '1.1.1.1'
    assert conn.input.settings['Port'] == 8081
    assert conn.output.settings['URL'] == 'https://localhost/example1'
