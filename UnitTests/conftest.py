def pytest_configure():
    import pytest
    from .test_data_helper import generate_user_email, generate_user_name

    @pytest.fixture
    def user_data():
        return {
            "email": generate_user_email(),
            "name": generate_user_name()
        }