"""
Routes package owned exclusively by Developer 2 (Anshu Kala).
Provides blueprints for authentication, item feeds & reporting, admin optimization, and campus maps.
"""

from .auth_bp import auth_bp
from .items_bp import items_bp
from .admin_bp import admin_bp
from .campus_bp import campus_bp

__all__ = ["auth_bp", "items_bp", "admin_bp", "campus_bp"]
