import pytest
from fastapi import status


def test_register_success(client):
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword123'
    }

    response = client.post('/auth/register', json=user_data)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['token_type'] == 'bearer'

    assert len(data['access_token']) > 0
    assert len(data['refresh_token']) > 0

def test_register_duplicate_user(client):
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword123'
    }
    client.post('/auth/register', json=user_data)
    response = client.post('/auth/register', json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_success(client):
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword123'
    }
    user_data_login = {
        'username': 'testuser',
        'password': 'securepassword123'
    }
    
    client.post('/auth/register', json=user_data)
    response = client.post('/auth/login', json=user_data_login)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['token_type'] == 'bearer'

    assert len(data['access_token']) > 0   
    assert len(data['refresh_token']) > 0   

def test_login_invalid_password(client):
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword123'
    }
    user_data_login = {
        'username': 'testuser',
        'password': 'NOTCORRECTPASSWORD'
    }
    client.post('/auth/register', json=user_data)
    response = client.post('/auth/login', json=user_data_login)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_incorrect_user(client):
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword123'
    }
    user_data_login = {
        'username': 'notcorrectuser676767',
        'password': 'securepassword123'
    }
    client.post('/auth/register', json=user_data)
    response = client.post('/auth/login', json=user_data_login)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_refresh_token_success(client):
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword123'
    }
    response = client.post('/auth/register', json=user_data)
    data = response.json()
    refresh_token = data['refresh_token']
    response = client.post('/auth/refresh', json={'refresh_token': refresh_token})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'access_token' in data
    assert len(data['access_token']) > 0
    assert 'refresh_token' in data
    assert len(data['refresh_token'])

def test_get_me(client):
    user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123'
        }
    response = client.post('/auth/register', json=user_data)
    data = response.json()
    access_token = data['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('/auth/me', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['username'] == 'testuser'
    assert data['email'] == 'test@example.com'
    assert 'id' in data
    assert 'password' not in data 

def test_get_me_unauthorized(client):
    response = client.get('/auth/me')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
