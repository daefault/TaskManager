import pytest
from fastapi import status


def create_task(client):
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
        'assignee_ids': [2]
    }
    response = client.post('/api/tasks', json=task_data, headers=headers)
    return response, headers

def test_create_task_success(client):
    response, _ = create_task(client)
    assert response.status_code == status.HTTP_201_CREATED

def test_get_my_tasks_success(client):
    _, headers = create_task(client)
    response = client.get('/api/tasks/my', headers=headers)
    assert response.status_code == status.HTTP_200_OK

def test_update_task_success(client):
    _, headers = create_task(client)
    update_data = {
        'title': 'SOmeNewTItle',
        'priority': 'high'
    }
    response = client.put('/api/tasks/1', json=update_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK

def test_delete_task_success(client):
    _, headers = create_task(client)
    response = client.delete('/api/tasks/1', headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_get_my_assigned_tasks(client):
    _, headers = create_task(client)
    response = client.get('/api/tasks/assigned/2', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    tasks_ids = [t['id'] for t in data]
    assert tasks_ids == [1]

def test_update_assignees_success(client):
    _, headers = create_task(client)
    assignee_ids = []
    response = client.put('/api/tasks/1/assignees', json={'assignee_ids': assignee_ids}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    a_ids = [a['id'] for a in data['assignees']]
    assert a_ids == []

def test_add_one_assignee_success(client):
    _, headers = create_task(client)
    response = client.post('/api/tasks/1/assignees/1', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    a_ids = [a['id'] for a in data['assignees']]
    assert a_ids == [1, 2]

def test_remove_one_assignee_success(client):
    _, headers = create_task(client)
    response = client.delete('/api/tasks/1/assignees/2', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    a_ids = [a['id'] for a in data['assignees']]
    assert a_ids == []
