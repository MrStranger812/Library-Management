# tests/api/test_auth_api.py
import pytest
from flask import url_for

class TestAuthAPI:
    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Test123!',
            'full_name': 'New User'
        })
        assert response.status_code == 201
        assert response.json['success'] is True
    
    def test_login_success(self, client, user_factory):
        """Test successful login"""
        user = user_factory(password='Test123!')
        response = client.post('/api/auth/login', json={
            'username': user.username,
            'password': 'Test123!'
        })
        assert response.status_code == 200
        assert 'access_token' in response.json
    
    def test_logout_success(self, client, auth_headers):
        """Test successful logout"""
        response = client.post('/api/auth/logout', headers=auth_headers)
        assert response.status_code == 200