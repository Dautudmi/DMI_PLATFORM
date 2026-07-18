from apps.portfolio.services.client_batch_processor import ClientBatchProcessor


def test_client_batch_processor_processes_all_clients_successfully():
    def handler(client_id: str):
        return f"done:{client_id}"

    processor = ClientBatchProcessor(handler)

    result = processor.process(["client_a", "client_b"])

    assert result.total_clients == 2
    assert result.success_count == 2
    assert result.failed_count == 0
    assert result.is_success is True
    assert result.has_failed is False
    assert result.results[0].client_id == "client_a"
    assert result.results[0].success is True
    assert result.results[0].data == "done:client_a"


def test_client_batch_processor_continues_when_one_client_fails():
    def handler(client_id: str):
        if client_id == "bad_client":
            raise ValueError("client failed")

        return f"done:{client_id}"

    processor = ClientBatchProcessor(handler)

    result = processor.process(["client_a", "bad_client", "client_b"])

    assert result.total_clients == 3
    assert result.success_count == 2
    assert result.failed_count == 1
    assert result.is_success is False
    assert result.has_failed is True

    failed = result.results[1]
    assert failed.client_id == "bad_client"
    assert failed.success is False
    assert failed.data is None
    assert failed.error == "client failed"


def test_client_batch_processor_rejects_none_handler():
    try:
        ClientBatchProcessor(None)
    except ValueError as exc:
        assert str(exc) == "handler must not be None"
    else:
        assert False


def test_client_batch_processor_rejects_none_client_ids():
    processor = ClientBatchProcessor(lambda client_id: client_id)

    try:
        processor.process(None)
    except ValueError as exc:
        assert str(exc) == "client_ids must not be None"
    else:
        assert False


def test_client_batch_processor_marks_empty_client_id_as_failed():
    processor = ClientBatchProcessor(lambda client_id: client_id)

    result = processor.process(["client_a", "", "   ", None])

    assert result.total_clients == 4
    assert result.success_count == 1
    assert result.failed_count == 3

    assert result.results[0].success is True
    assert result.results[1].success is False
    assert result.results[1].error == "client_id is empty"
    assert result.results[2].success is False
    assert result.results[2].error == "client_id is empty"
    assert result.results[3].success is False
    assert result.results[3].error == "client_id is empty"