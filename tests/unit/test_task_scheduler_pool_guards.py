from backend.config import settings
from backend.services.task_scheduler_service import TaskSchedulerService


def test_domain_circuit_opens_after_threshold(monkeypatch):
    monkeypatch.setattr(settings, "REQUEST_DOMAIN_FAILURE_THRESHOLD", 2)
    monkeypatch.setattr(settings, "REQUEST_DOMAIN_COOLDOWN_SECONDS", 60)

    service = TaskSchedulerService(db=None)
    TaskSchedulerService._domain_fail_state.clear()

    domain = "m.100qiu.com"
    assert service._is_domain_circuit_open(domain) is False

    service._record_domain_result(domain, success=False, status_code=429)
    assert service._is_domain_circuit_open(domain) is False

    service._record_domain_result(domain, success=False, status_code=429)
    assert service._is_domain_circuit_open(domain) is True

    service._record_domain_result(domain, success=True, status_code=200)
    assert service._is_domain_circuit_open(domain) is False
