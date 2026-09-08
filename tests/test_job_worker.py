from app.agent.jobs import _json_value


def test_job_worker_decodes_json_strings():
    assert _json_value('{"question":"hello"}') == {"question": "hello"}
    assert _json_value('["viewer"]') == ["viewer"]


def test_job_worker_keeps_decoded_values():
    value = {"question": "hello"}
    assert _json_value(value) is value
