import pytest
from fastapi.testclient import TestClient
from main import app
import asyncio


@pytest.fixture(scope="session")
def event_loop(request):  # pylint: disable=unused-argument
    """
    Create an instance of the default event loop for each test case.
    (overwrites same-named lower-scoped fixture from aiohttp test utils)
    """

    asyncio_loop = asyncio.get_event_loop_policy().new_event_loop()
    yield asyncio_loop
    asyncio_loop.close()


@pytest.fixture(scope="session")
def loop(event_loop):  # pylint: disable=redefined-outer-name
    """
    Override default loop fixture with pytest-asyncio event_loop to avoid
    running two loops (which leads to a conflict)

    https://github.com/pytest-dev/pytest-asyncio/issues/170
    """

    return event_loop


@pytest.fixture(scope="session")
def client():
    client = TestClient(app)
    return client


