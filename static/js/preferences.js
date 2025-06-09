document.addEventListener('DOMContentLoaded', function() {
    loadPreferences();

    document.getElementById('preferencesForm').addEventListener('submit', function(e) {
        e.preventDefault();
        savePreferences();
    });
});

function loadPreferences() {
    fetch('/api/preferences')
        .then(response => response.json())
        .then(preferences => {
            document.getElementById('theme').value = preferences.theme || 'light';
            document.getElementById('language').value = preferences.language || 'en';
            document.getElementById('emailNotifications').checked = preferences.email_notifications || false;
            document.getElementById('smsNotifications').checked = preferences.sms_notifications || false;
            document.getElementById('timezone').value = preferences.timezone || 'UTC';
        })
        .catch(error => {
            console.error('Error loading preferences:', error);
            showAlert('Error loading preferences. Please try again.', 'danger');
        });
}

function savePreferences() {
    const formData = {
        theme: document.getElementById('theme').value,
        language: document.getElementById('language').value,
        email_notifications: document.getElementById('emailNotifications').checked,
        sms_notifications: document.getElementById('smsNotifications').checked,
        timezone: document.getElementById('timezone').value
    };

    fetch('/api/preferences', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': getApiKey()
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Preferences saved successfully!', 'success');
        } else {
            showAlert(data.message || 'Error saving preferences', 'danger');
        }
    })
    .catch(error => {
        console.error('Error saving preferences:', error);
        showAlert('Error saving preferences. Please try again.', 'danger');
    });
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