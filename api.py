from flask import Blueprint, jsonify, request
from models import Article

api_bp = Blueprint('api', __name__)

@api_bp.route('/articles', methods=['GET'])
def get_articles():
    articles = Article.query.all()
    return jsonify([{
        'id': article.id,
        'title': article.title,
        'content': article.content
    } for article in articles])

@api_bp.route('/article/<int:id>', methods=['GET'])
def get_article(id):
    article = Article.query.get_or_404(id)
    return jsonify({
        'id': article.id,
        'title': article.title,
        'content': article.content
    })
