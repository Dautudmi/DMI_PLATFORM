from dmi_core.engine import DMIEngine

from apps.portfolio.services.dmi_service import DMIService


def test_dmi_service_uses_default_engine():
    service = DMIService()

    assert isinstance(service._engine, DMIEngine)


def test_dmi_service_accepts_custom_engine():
    engine = DMIEngine()

    service = DMIService(engine=engine)

    assert service._engine is engine