from flask import Flask, jsonify, request
import mysql.connector
import redis
import json
import os

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'database'),
        user=os.environ.get('DB_USER', 'blog_user'),
        password=os.environ.get('DB_PASSWORD', 'blog_password'),
        database=os.environ.get('DB_NAME', 'blog_db')
    )

def get_redis():
    return redis.Redis(
        host=os.environ.get('REDIS_HOST', 'redis'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        decode_responses=True
    )

@app.route('/')
def home():
    return jsonify({
        "message": "Blog API",
        "version": "1.0",
        "status": "running"
    })

@app.route('/articles', methods=['GET'])
def get_articles():
    try:
        r = get_redis()
        cached = r.get('articles')
        if cached:
            return jsonify({
                "source": "cache",
                "articles": json.loads(cached)
            })
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, title, content, created_at FROM articles")
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        articles = [
            {"id": row[0], "title": row[1], "content": row[2], "created_at": str(row[3])}
            for row in rows
        ]
        r.setex('articles', 60, json.dumps(articles))
        return jsonify({"source": "database", "articles": articles})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    try:
        r = get_redis()
        cached = r.get(f'article:{article_id}')
        if cached:
            return jsonify({
                "source": "cache",
                "article": json.loads(cached)
            })
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, title, content, created_at FROM articles WHERE id = %s",
            (article_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        db.close()
        if not row:
            return jsonify({"error": "Article not found"}), 404
        article = {
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "created_at": str(row[3])
        }
        r.setex(f'article:{article_id}', 60, json.dumps(article))
        return jsonify({"source": "database", "article": article})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/articles', methods=['POST'])
def create_article():
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        if not title or not content:
            return jsonify({"error": "title and content are required"}), 400
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO articles (title, content) VALUES (%s, %s)",
            (title, content)
        )
        db.commit()
        article_id = cursor.lastrowid
        cursor.close()
        db.close()
        r = get_redis()
        r.delete('articles')
        return jsonify({"message": "Article created", "id": article_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
