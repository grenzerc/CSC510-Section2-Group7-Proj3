"""Use Case #15 -- Chat with the food assistant.

ChatServiceImpl talks to a local Ollama at localhost:11434 using qwen2.5:1.5b.
Half of this file only makes sense with Ollama up and half only makes sense
with it down, so the tests skip themselves accordingly. To see the interesting
failure, stop Ollama and run it again.
"""

import urllib.error
import urllib.request

import pytest

from api_helpers import api_request, register_and_login, require_backend

OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"


def ollama_is_up():
    try:
        with urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=2):
            return True
    except (urllib.error.URLError, OSError):
        return False


OLLAMA_UP = ollama_is_up()


@pytest.fixture(scope="module", autouse=True)
def backend():
    require_backend()


@pytest.fixture(scope="module")
def customer():
    _, token = register_and_login("customer", "chatter")
    return token


def test_the_assistant_cannot_be_used_without_logging_in():
    """This proves the endpoint is behind authentication."""
    status, body = api_request("POST", "/api/chat", {"message": "hello"})

    assert status == 401, body


def test_a_driver_cannot_use_the_assistant():
    """This proves extension 1a.

    DRIVER is missing from this endpoint's role list while it is present on the
    order endpoints. Passing here documents the inconsistency rather than
    endorsing it -- see the use case.
    """
    _, driver = register_and_login("driver", "hungry_driver")

    status, body = api_request("POST", "/api/chat", {"message": "hello"}, token=driver)

    assert status == 403, body


@pytest.mark.skipif(not OLLAMA_UP, reason="no Ollama on localhost:11434")
def test_the_assistant_answers_a_greeting(customer):
    """This proves the main success scenario, when the model is actually there."""
    status, body = api_request(
        "POST", "/api/chat", {"message": "hello"}, token=customer, timeout=120
    )

    assert status == 200, body
    assert body["message"].strip(), "the assistant returned an empty reply"
    assert not body["message"].startswith("Error:"), body["message"]


@pytest.mark.skipif(
    OLLAMA_UP, reason="only meaningful with Ollama stopped -- stop it and rerun"
)
def test_an_unreachable_model_is_reported_as_a_failure(customer):
    """This proves extension 4a, and it is the code-rot finding.

    Expected to fail. ChatServiceImpl wraps the whole call in catch (Exception)
    and returns 200 with "Error: Connection refused" in the same field a real
    answer would use. The client has no way to tell the two apart, and the
    user is shown raw exception text as though the assistant had said it.
    """
    status, body = api_request(
        "POST", "/api/chat", {"message": "hello"}, token=customer, timeout=60
    )

    assert status >= 500, (
        f"backend hid an unreachable model behind {status} "
        f"with body {body.get('message')!r}"
    )
