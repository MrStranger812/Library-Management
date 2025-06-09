document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    loadBooks();
    loadCategories();

    // Set up event listeners
    document.getElementById('searchForm').addEventListener('submit', function(e) {
        e.preventDefault();
        loadBooks();
    });

    document.getElementById('saveBookBtn').addEventListener('click', function() {
        saveBook();
    });
});

function loadBooks() {
    const searchQuery = document.getElementById('searchQuery').value;
    const categoryFilter = document.getElementById('categoryFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;

    fetch(`/api/books?q=${searchQuery}&category=${categoryFilter}&status=${statusFilter}`)
        .then(response => response.json())
        .then(books => {
            const tbody = document.getElementById('booksTableBody');
            tbody.innerHTML = '';

            books.forEach(book => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${book.title}</td>
                    <td>${book.author}</td>
                    <td>${book.isbn}</td>
                    <td>${book.category_name || 'Uncategorized'}</td>
                    <td>
                        <span class="badge ${book.available_copies > 0 ? 'bg-success' : 'bg-danger'}">
                            ${book.available_copies > 0 ? 'Available' : 'Borrowed'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="viewBook(${book.book_id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${currentUserHasPermission('manage_books') ? `
                            <button class="btn btn-sm btn-warning" onclick="editBook(${book.book_id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteBook(${book.book_id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        ` : ''}
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Error loading books:', error);
            showAlert('Error loading books. Please try again.', 'danger');
        });
}

function loadCategories() {
    fetch('/api/categories')
        .then(response => response.json())
        .then(categories => {
            const categorySelects = [
                document.getElementById('categoryFilter'),
                document.getElementById('category')
            ];

            categorySelects.forEach(select => {
                if (select) {
                    select.innerHTML = '<option value="">All Categories</option>';
                    categories.forEach(category => {
                        const option = document.createElement('option');
                        option.value = category.category_id;
                        option.textContent = category.name;
                        select.appendChild(option);
                    });
                }
            });
        })
        .catch(error => {
            console.error('Error loading categories:', error);
            showAlert('Error loading categories. Please try again.', 'danger');
        });
}

function saveBook() {
    const form = document.getElementById('addBookForm');
    const formData = {
        title: document.getElementById('title').value,
        author: document.getElementById('author').value,
        isbn: document.getElementById('isbn').value,
        category_id: document.getElementById('category').value,
        description: document.getElementById('description').value
    };

    fetch('/api/books', {
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
            bootstrap.Modal.getInstance(document.getElementById('addBookModal')).hide();
            form.reset();
            loadBooks();
            showAlert('Book added successfully!', 'success');
        } else {
            showAlert(data.message || 'Error adding book', 'danger');
        }
    })
    .catch(error => {
        console.error('Error saving book:', error);
        showAlert('Error saving book. Please try again.', 'danger');
    });
}

function viewBook(bookId) {
    // Implement view book functionality
    window.location.href = `/books/${bookId}`;
}

function editBook(bookId) {
    // Implement edit book functionality
    window.location.href = `/books/${bookId}/edit`;
}

function deleteBook(bookId) {
    if (confirm('Are you sure you want to delete this book?')) {
        fetch(`/api/books/${bookId}`, {
            method: 'DELETE',
            headers: {
                'X-API-Key': getApiKey()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadBooks();
                showAlert('Book deleted successfully!', 'success');
            } else {
                showAlert(data.message || 'Error deleting book', 'danger');
            }
        })
        .catch(error => {
            console.error('Error deleting book:', error);
            showAlert('Error deleting book. Please try again.', 'danger');
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