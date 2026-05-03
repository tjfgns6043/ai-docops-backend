from libs.common.status import JOB_COMPLETED, JOB_FAILED, JOB_RUNNING, can_transition_job


def test_forbidden_job_status_transitions_are_blocked() -> None:
    assert not can_transition_job(JOB_COMPLETED, JOB_RUNNING)
    assert not can_transition_job(JOB_FAILED, JOB_COMPLETED)


def test_allowed_job_status_transition() -> None:
    assert can_transition_job(JOB_RUNNING, JOB_COMPLETED)
