import fastapi.testclient
import pytest

import alhos_e_bugalhos


@pytest.fixture
def client():
    return fastapi.testclient.TestClient(alhos_e_bugalhos.app)
