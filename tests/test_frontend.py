from hwstats.frontend import app


def test_index() -> None:
    """Test the index page"""
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
        assert b"Hardware Stats" in response.data
