from paste.script.util import secret

def test_random():
    for length in (1, 10, 100):
        data = secret.random_bytes(length)
        assert isinstance(data, bytes)
        assert len(data) == length

def test_secret_string():
    data = secret.secret_string()
    assert isinstance(data, str)

    data = secret.secret_string(20)
    assert isinstance(data, str)
    assert len(data) == 20
