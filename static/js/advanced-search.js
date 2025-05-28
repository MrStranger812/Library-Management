document.addEventListener('DOMContentLoaded', function() {
    const advancedSearchBtn = document.getElementById('advancedSearchBtn');
    const advancedSearchForm = document.getElementById('advancedSearchForm');
    
    if (advancedSearchBtn && advancedSearchForm) {
        advancedSearchBtn.addEventListener('click', function() {
            advancedSearchForm.classList.toggle('d-none');
        });
        
        advancedSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(advancedSearchForm);
            const searchParams = new URLSearchParams();
            
            for (const [key, value] of formData.entries()) {
                if (value) {
                    searchParams.append(key, value);
                }
            }
            
            fetch(`/api/books/search?${searchParams.toString()}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        displayBooks(data.books);
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while searching');
                });
        });
    }
    
    function displayBooks(books) {
        const tableBody = document.getElementById('booksTableBody');
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        if (books.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="7" class="text-center">No books found matching your criteria</td>';
            tableBody.appendChild(row);
            return;
        }
        
        books.forEach(book => {
            // Display books (similar to your existing code)
            // ...
        });
        
        setupButtonEventListeners();
    }
});