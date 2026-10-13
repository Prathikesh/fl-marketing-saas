from fl_marketing.api.main import app


def test_app_exposes_expected_routes():
    paths = set(app.openapi()["paths"].keys())
    assert {"/predict", "/feedback", "/audit", "/tenants", "/health"} <= paths
