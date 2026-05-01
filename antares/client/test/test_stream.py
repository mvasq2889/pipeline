import pytest

from antares_client import StreamingClient


def is_kafka_installed():
    try:
        import confluent_kafka

        return True
    except ImportError:
        return False


@pytest.mark.skipif(not is_kafka_installed(), reason="confluent_kafka not installed")
def test_confluent_kafka_installed():
    topics = ["some_topic"]
    streaming_client = StreamingClient(
        topics=topics, api_key="api_key", api_secret="api_secret"
    )
    assert streaming_client.topics == topics


@pytest.mark.skipif(is_kafka_installed(), reason="confluent_kafka installed")
def test_confluent_kafka_not_installed():
    with pytest.raises(ImportError):
        assert StreamingClient()
