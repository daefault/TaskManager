from fastapi import status
import pytest 


def create_comment(client):
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
    client.post('/api/projects', json=project_data, headers=headers)
    task_data = {
        'title': 'TAKOETONAZVANIE',
        'description': 'VOT TAK VOT',
        'status': 'pending',
        'priority': 'low', 
        "deadline": "2026-08-11T16:59:35.169Z",
        'project_id': 1,
        'assignee_ids': []
    }
    client.post('/api/tasks', json=task_data, headers=headers)
    comment_data = {
        'content': 'GGGGGGG',
        'task_id': 1
    }
    response = client.post('/api/comments', json=comment_data, headers=headers)
    return response, headers

def test_create_comment(client):
    response, _ = create_comment(client)
    assert response.status_code == status.HTTP_201_CREATED

def test_update_comment(client):
    _, headers = create_comment(client)
    update_data = {
        'content': 'SomeNewContent'
    }
    response = client.put('/api/comments/1', json=update_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK

def test_delete_comment(client):
    _, headers = create_comment(client)
    response = client.delete('/api/comments/1', headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_unauthorized(client):
    create_comment(client)
    response = client.delete('/api/comments/1')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_not_your_comment(client):
    create_comment(client)
    login_data = {
            'username': 'testuser1',
            'password': 'securepassword123'
    }
    response = client.post('/api/auth/login', json=login_data)
    data = response.json()
    access_token = data['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    update_data = {
        'content': 'SomeNewContent'
    }
    response = client.put('/api/comments/1', json=update_data, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
