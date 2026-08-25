import pytest 
from fastapi import status


def create_project(client):
    user_data_1 = {
        'username': 'testuser1',
        'email': 'test1@example.com',
        'password': 'securepassword123'
    }
    user_data_2 = {
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'securepassword123'
    }
    client.post('/api/auth/register', json=user_data_1)
    response = client.post('/api/auth/register', json=user_data_2)
    data = response.json()
    access_token = data['access_token']
    project_data = {
        'name': 'testproject',
        'description': 'some description',
        'status': 'active',
        'member_ids': [1]
    }
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post('/api/projects', json=project_data, headers=headers)
    return response, headers

def test_create_project_success(client):
    response, _ = create_project(client)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    members = [m['id'] for m in data['members']]
    assert members == [1,2]

def test_create_project_unauthorized(client):
    user_data_1 = {
            'username': 'testuser1',
            'email': 'test1@example.com',
            'password': 'securepassword123'
        }
    user_data_2 = {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'securepassword123'
        }
    client.post('/api/auth/register', json=user_data_1)
    client.post('/api/auth/register', json=user_data_2)
    project_data = {
        'name': 'testproject',
        'description': 'some description',
        'status': 'active',
        'member_ids': [1]
    }
    response = client.post('/api/projects', json=project_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_my_projects(client):
    _, headers = create_project(client)
    response = client.get('/api/projects', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 4

def test_update_project_success(client): 
    _, headers = create_project(client)
    update_data = {
        'name': 'newName',
        'description': 'someNewDescr',
        'status': 'archived'
    }
    response = client.put('/api/projects/1', json=update_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK

def test_delete_project_success(client):
    _, headers = create_project(client)
    response = client.delete('/api/projects/1', headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_get_members_in_project_success(client):
    _, headers = create_project(client)
    response = client.get('/api/projects/1/members', headers=headers)
    assert response.status_code == status.HTTP_200_OK

def test_update_members_in_project_success(client):
    user_data_1 = {
                'username': 'testuser1',
                'email': 'test1@example.com',
                'password': 'securepassword123'
            }
    user_data_2 = {
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'securepassword123'
    }
    client.post('/api/auth/register', json=user_data_1)
    response = client.post('/api/auth/register', json=user_data_2)
    data = response.json()
    access_token = data['access_token']
    project_data = {
        'name': 'testproject',
        'description': 'some description',
        'status': 'active',
        'member_ids': []
    }
    headers = {'Authorization': f'Bearer {access_token}'}
    client.post('/api/projects', json=project_data, headers=headers)
    members_ids = [1]
    response = client.put('/api/projects/1/members', json={'member_ids': members_ids}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    members = [m['id'] for m in data['members']]
    assert members == [1,2]

def test_add_member_success(client):
    user_data_1 = {
                    'username': 'testuser1',
                    'email': 'test1@example.com',
                    'password': 'securepassword123'
                }
    user_data_2 = {
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'securepassword123'
    }
    client.post('/api/auth/register', json=user_data_1)
    response = client.post('/api/auth/register', json=user_data_2)
    data = response.json()
    access_token = data['access_token']
    project_data = {
        'name': 'testproject',
        'description': 'some description',
        'status': 'active',
        'member_ids': []
    }
    headers = {'Authorization': f'Bearer {access_token}'}
    client.post('/api/projects', json=project_data, headers=headers)
    response = client.post('/api/projects/1/members/1', headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    members = [m['id'] for m in data['members']]
    assert members == [1,2]

def test_remove_member_success(client):
    _, headers = create_project(client)
    response = client.delete('/api/projects/1/members/1', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    members = [m['id'] for m in data['members']]
    assert members == [2]

def test_remove_owner(client):
    _, headers = create_project(client)
    response = client.delete('/api/projects/1/members/2', headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST