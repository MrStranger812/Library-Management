/**
 * Library Management System - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and popovers if using Bootstrap
    initializeBootstrapComponents();
    
    // Initialize book search functionality
    initializeBookSearch();
    
    // Initialize book form handlers
    initializeBookForms();
    
    // Initialize borrowing functionality
    initializeBorrowingFunctions();
    
    // Initialize notification system
    initializeNotifications();
});

/**
 * Initialize Bootstrap components
 */
function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Initialize book search functionality
 */
function initializeBookSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    
    if (searchInput && searchBtn) {
        // Search button click handler
        searchBtn.addEventListener('click', function() {
            searchBooks(searchInput.value);
        });
        
        // Enter key press handler
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchBooks(searchInput.value);
            }
        });
    }
}

/**
 * Search books with the given query
 */
function searchBooks(query) {
    fetch(`/api/books?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displayBooks(data);
        })
        .catch(error => {
            console.error('Error searching books:', error);
            showAlert('Error searching books. Please try again.', 'danger');
        });
}

/**
 * Display books in the table
 */
function displayBooks(books) {
    const tableBody = document.getElementById('booksTableBody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    if (books.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center">No books found</td></tr>';
        return;
    }
    
    books.forEach(book => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${book.isbn}</td>
            <td>${book.title}</td>
            <td>${book.author}</td>
            <td>${book.category || 'N/A'}</td>
            <td>${book.publication_year || 'N/A'}</td>
            <td>${book.copies_available} / ${book.total_copies}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-info view-book" data-id="${book.book_id}" data-bs-toggle="tooltip" title="View Details">
                        <i class="bi bi-eye"></i>
                    </button>
                    ${book.copies_available > 0 ? 
                        `<button class="btn btn-success borrow-book" data-id="${book.book_id}" data-bs-toggle="tooltip" title="Borrow Book">
                            <i class="bi bi-journal-arrow-down"></i>
                        </button>` : ''}
                    ${document.body.dataset.userRole === 'admin' || document.body.dataset.userRole === 'librarian' ? 
                        `<button class="btn btn-primary edit-book" data-id="${book.book_id}" data-bs-toggle="tooltip" title="Edit Book">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-danger delete-book" data-id="${book.book_id}" data-bs-toggle="tooltip" title="Delete Book">
                            <i class="bi bi-trash"></i>
                        </button>` : ''}
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    // Re-initialize tooltips for the new buttons
    const tooltips = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltips.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add event listeners to the new buttons
    addBookButtonListeners();
}

/**
 * Add event listeners to book action buttons
 */
function addBookButtonListeners() {
    // View book details
    document.querySelectorAll('.view-book').forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.dataset.id;
            window.location.href = `/books/${bookId}`;
        });
    });
    
    // Borrow book
    document.querySelectorAll('.borrow-book').forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.dataset.id;
            borrowBook(bookId);
        });
    });
    
    // Edit book
    document.querySelectorAll('.edit-book').forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.dataset.id;
            editBook(bookId);
        });
    });
    
    // Delete book
    document.querySelectorAll('.delete-book').forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.dataset.id;
            deleteBook(bookId);
        });
    });
}

/**
 * Initialize book form handlers
 */
function initializeBookForms() {
    const saveBookBtn = document.getElementById('saveBookBtn');
    if (saveBookBtn) {
        saveBookBtn.addEventListener('click', function() {
            const form = document.getElementById('addBookForm');
            if (form.checkValidity()) {
                const formData = new FormData(form);
                const bookData = Object.fromEntries(formData.entries());
                
                fetch('/api/books', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(bookData),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showAlert(data.error, 'danger');
                    } else {
                        showAlert('Book added successfully', 'success');
                        // Close modal and refresh book list
                        const modal = bootstrap.Modal.getInstance(document.getElementById('addBookModal'));
                        modal.hide();
                        searchBooks('');
                        form.reset();
                    }
                })
                .catch(error => {
                    console.error('Error adding book:', error);
                    showAlert('Error adding book. Please try again.', 'danger');
                });
            } else {
                form.reportValidity();
            }
        });
    }
}

/**
 * Borrow a book
 */
function borrowBook(bookId) {
    if (confirm('Do you want to borrow this book?')) {
        fetch(`/api/borrowings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ book_id: bookId }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(data.error, 'danger');
            } else {
                showAlert(data.message, 'success');
                // Refresh book list to update availability
                searchBooks('');
            }
        })
        .catch(error => {
            console.error('Error borrowing book:', error);
            showAlert('Error borrowing book. Please try again.', 'danger');
        });
    }
}

/**
 * Edit a book
 */
function editBook(bookId) {
    // Fetch book details
    fetch(`/api/books/${bookId}`)
        .then(response => response.json())
        .then(book => {
            // Populate edit form
            document.getElementById('editBookId').value = book.book_id;
            document.getElementById('editIsbn').value = book.isbn;
            document.getElementById('editTitle').value = book.title;
            document.getElementById('editAuthor').value = book.author;
            document.getElementById('editCategory').value = book.category || '';
            document.getElementById('editPublicationYear').value = book.publication_year || '';
            document.getElementById('editCopies').value = book.total_copies;
            
            // Show edit modal
            const editModal = new bootstrap.Modal(document.getElementById('editBookModal'));
            editModal.show();
        })
        .catch(error => {
            console.error('Error fetching book details:', error);
            showAlert('Error fetching book details. Please try again.', 'danger');
        });
}

/**
 * Delete a book
 */
function deleteBook(bookId) {
    if (confirm('Are you sure you want to delete this book? This action cannot be undone.')) {
        fetch(`/api/books/${bookId}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(data.error, 'danger');
            } else {
                showAlert('Book deleted successfully', 'success');
                // Refresh book list
                searchBooks('');
            }
        })
        .catch(error => {
            console.error('Error deleting book:', error);
            showAlert('Error deleting book. Please try again.', 'danger');
        });
    }
}

/**
 * Initialize borrowing functions
 */
function initializeBorrowingFunctions() {
    // Return book button handlers
    document.querySelectorAll('.return-book').forEach(button => {
        button.addEventListener('click', function() {
            const borrowingId = this.dataset.id;
            returnBook(borrowingId);
        });
    });
}

/**
 * Return a borrowed book
 */
function returnBook(borrowingId) {
    if (confirm('Do you want to return this book?')) {
        fetch(`/api/borrowings/${borrowingId}/return`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(data.error, 'danger');
            } else {
                showAlert(data.message, 'success');
                // Refresh borrowings list
                window.location.reload();
            }
        })
        .catch(error => {
            console.error('Error returning book:', error);
            showAlert('Error returning book. Please try again.', 'danger');
        });
    }
}

/**
 * Initialize notification system
 */
function initializeNotifications() {
    const notificationBell = document.getElementById('notificationBell');
    const notificationCount = document.getElementById('notificationCount');
    const notificationList = document.getElementById('notificationList');
    
    if (notificationBell && notificationCount && notificationList) {
        // Fetch notifications
        fetchNotifications();
        
        // Mark notification as read when clicked
        notificationList.addEventListener('click', function(e) {
            const notificationItem = e.target.closest('.notification-item');
            if (notificationItem) {
                const notificationId = notificationItem.dataset.id;
                markNotificationAsRead(notificationId);
            }
        });
    }
}

/**
 * Fetch user notifications
 */
function fetchNotifications() {
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            updateNotificationUI(data);
        })
        .catch(error => {
            console.error('Error fetching notifications:', error);
        });
}

/**
 * Update notification UI
 */
function updateNotificationUI(notifications) {
    const notificationCount = document.getElementById('notificationCount');
    const notificationList = document.getElementById('notificationList');
    
    if (!notificationCount || !notificationList) return;
    
    // Update notification count
    const unreadCount = notifications.filter(n => !n.is_read).length;
    notificationCount.textContent = unreadCount;
    notificationCount.style.display = unreadCount > 0 ? 'inline-block' : 'none';
    
    // Update notification list
    notificationList.innerHTML = '';
    
    if (notifications.length === 0) {
        notificationList.innerHTML = '<div class="dropdown-item text-center">No notifications</div>';
        return;
    }
    
    notifications.forEach(notification => {
        const item = document.createElement('div');
        item.className = `dropdown-item notification-item ${notification.is_read ? '' : 'unread'}`;
        item.dataset.id = notification.notification_id;
        
        // Format date
        const date = new Date(notification.created_at);
        const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        
        item.innerHTML = `
            <div class="notification-content">
                <p>${notification.message}</p>
                <small class="text-muted">${formattedDate}</small>
            </div>
        `;
        
        notificationList.appendChild(item);
    });
}

/**
 * Mark notification as read
 */
function markNotificationAsRead(notificationId) {
    fetch(`/api/notifications/${notificationId}/read`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        // Refresh notifications
        fetchNotifications();
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertContainer, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = bootstrap.Alert.getOrCreateInstance(alertContainer);
        alert.close();
    }, 5000);
}