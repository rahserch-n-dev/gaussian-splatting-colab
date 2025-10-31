from src.core import env


def test_full_env_report_contains_keys():
    report = env.full_env_report()
    assert "python" in report
    assert "system" in report
    assert "torch" in report


def test_torch_info_shape():
    t = env.get_torch_info()
    assert isinstance(t, dict)
    # installed may be True or False depending on environment
    assert "installed" in t
