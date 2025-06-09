document.addEventListener('DOMContentLoaded', function() {
    loadFines();

    document.getElementById('finesFilterForm').addEventListener('submit', function(e) {
        e.preventDefault();
        loadFines();
    });
});

function loadFines() {
    const searchQuery = document.getElementById('searchQuery').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const dateFilter = document.getElementById('dateFilter').value;

    // Build query string
    let url = `/api/fines?q=${encodeURIComponent(searchQuery)}&status=${encodeURIComponent(statusFilter)}&date=${encodeURIComponent(dateFilter)}`;

    fetch(url)
        .then(response => response.json())
        .then(fines => {
            const tbody = document.getElementById('finesTableBody');
            tbody.innerHTML = '';

            fines.forEach(fine => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${fine.user_name || 'N/A'}</td>
                    <td>${fine.amount}</td>
                    <td>
                        <span class="badge ${fine.status === 'paid' ? 'bg-success' : 'bg-warning'}">
                            ${fine.status}
                        </span>
                    </td>
                    <td>${new Date(fine.date).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="viewFine(${fine.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${fine.status === 'unpaid' ? `
                            <button class="btn btn-sm btn-success" onclick="payFine(${fine.id})">
                                <i class="fas fa-dollar-sign"></i>
                            </button>
                        ` : ''}
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Error loading fines:', error);
            showAlert('Error loading fines. Please try again.', 'danger');
        });
}

function viewFine(fineId) {
    // Implement view fine functionality
    window.location.href = `/fines/${fineId}`;
}

function payFine(fineId) {
    if (confirm('Are you sure you want to mark this fine as paid?')) {
        fetch(`/api/fines/${fineId}/pay`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': getApiKey()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadFines();
                showAlert('Fine marked as paid successfully!', 'success');
            } else {
                showAlert(data.message || 'Error paying fine', 'danger');
            }
        })
        .catch(error => {
            console.error('Error paying fine:', error);
            showAlert('Error paying fine. Please try again.', 'danger');
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