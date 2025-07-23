from flask import Blueprint, jsonify, request, render_template
from app.util.query_cache import get_cache_stats, clear_query_cache

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api/cache/stats')
def cache_stats():
    """Get statistics about the query cache"""
    stats = get_cache_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })

@api_blueprint.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the query cache"""
    clear_query_cache()
    return jsonify({
        'success': True,
        'message': 'Cache cleared successfully'
    })

@api_blueprint.route('/monitoring')
def monitoring_dashboard():
    """Render the performance monitoring dashboard"""
    return render_template('monitoring.html')

# Add this to the app/__init__.py file:
# from app.views.api import api_blueprint
# app.register_blueprint(api_blueprint)
