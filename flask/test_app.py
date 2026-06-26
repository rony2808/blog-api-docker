from app import app

def test_home():
	client = app.test_client()
	response = client.get('/')
	assert response.status_code == 200
	assert response.get_json()["status"] == "running"


def test_get_articles():
	client = app.test_client()
	response = client.get('/articles')
	assert response.status_code == 200
	data = response.get_json()
	assert "articles" in data
	assert "source" in data
