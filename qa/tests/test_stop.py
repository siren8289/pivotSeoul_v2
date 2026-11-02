from qa.hooks.stop_qa import should_block


def test_clean_tree_allows_stop() -> None:
    assert should_block({"reason": "end_turn"}, ["README.md"], None, None) is None


def test_code_change_without_report_blocks() -> None:
    reason = should_block({"reason": "end_turn"}, ["front/src/App.tsx"], None, 10.0)
    assert reason is not None
    assert "qa/run_qa.py" in reason


def test_report_newer_than_code_allows_stop() -> None:
    assert should_block({"reason": "end_turn"}, ["qa/run_qa.py"], 20.0, 10.0) is None


def test_second_stop_does_not_loop() -> None:
    assert should_block({"reason": "end_turn", "stopHookActive": True}, ["ai/src/service.py"], None, 10.0) is None


def test_session_end_does_not_block() -> None:
    assert should_block({"reason": "shutdown"}, ["back/src/main/java/App.java"], None, 10.0) is None
