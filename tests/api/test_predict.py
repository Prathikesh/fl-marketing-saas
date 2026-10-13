from fl_marketing.api.main import app


def test_app_exposes_expected_routes():
    paths = {route.path for route in app.routes}
    assert {"/predict", "/feedback", "/audit", "/tenants", "/health"} <= paths
