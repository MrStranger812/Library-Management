document.addEventListener('DOMContentLoaded', function() {
    loadUsers();

    document.getElementById('searchForm').addEventListener('submit', function(e) {
        e.preventDefault();
        loadUsers();
    });

    document.getElementById('saveUserBtn').addEventListener('click', function() {
        saveUser();
    });
});

function loadUsers() {
    const searchQuery = document.getElementById('searchQuery').value;
    const roleFilter = document.getElementById('roleFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;

    // Build query string
    let url = `/api/users?q=${encodeURIComponent(searchQuery)}&role=${encodeURIComponent(roleFilter)}&status=${encodeURIComponent(statusFilter)}`;

    fetch(url)
        .then(response => response.json())
        .then(users => {
            const tbody = document.getElementById('usersTableBody');
            tbody.innerHTML = '';

            users.forEach(user => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${user.username}</td>
                    <td>${user.full_name || ''}</td>
                    <td>${user.email}</td>
                    <td>${user.role}</td>
                    <td>
                        <span class="badge ${user.is_active ? 'bg-success' : 'bg-secondary'}">
                            ${user.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="viewUser(${user.user_id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${currentUserHasPermission('manage_users') ? `
                            <button class="btn btn-sm btn-warning" onclick="editUser(${user.user_id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.user_id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        ` : ''}
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Error loading users:', error);
            showAlert('Error loading users. Please try again.', 'danger');
        });
}

function saveUser() {
    const form = document.getElementById('addUserForm');
    const formData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        full_name: document.getElementById('fullName').value,
        role: document.getElementById('role').value
    };

    fetch('/api/users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': getApiKey()
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('addUserModal')).hide();
            form.reset();
            loadUsers();
            showAlert('User added successfully!', 'success');
        } else {
            showAlert(data.message || 'Error adding user', 'danger');
        }
    })
    .catch(error => {
        console.error('Error saving user:', error);
        showAlert('Error saving user. Please try again.', 'danger');
    });
}

function viewUser(userId) {
    // Implement view user functionality
    window.location.href = `/users/${userId}`;
}

function editUser(userId) {
    // Implement edit user functionality
    window.location.href = `/users/${userId}/edit`;
}

function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        fetch(`/api/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'X-API-Key': getApiKey()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadUsers();
                showAlert('User deleted successfully!', 'success');
            } else {
                showAlert(data.message || 'Error deleting user', 'danger');
            }
        })
        .catch(error => {
            console.error('Error deleting user:', error);
            showAlert('Error deleting user. Please try again.', 'danger');
        });
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.card'));
    setTimeout(() => alertDiv.remove(), 5000);
}

function getApiKey() {
    // Implement API key retrieval
    return localStorage.getItem('apiKey') || '';
}

function currentUserHasPermission(permission) {
    // Implement permission check
    return true; // This should be replaced with actual permission check
} 