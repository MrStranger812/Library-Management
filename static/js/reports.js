document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('reportFilterForm').addEventListener('submit', function(e) {
        e.preventDefault();
        generateReport();
    });
});

function generateReport() {
    const reportType = document.getElementById('reportType').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const resultsDiv = document.getElementById('reportResults');
    resultsDiv.innerHTML = '<div class="text-center">Loading...</div>';

    // Example API endpoint, adjust as needed
    let url = `/api/reports?type=${encodeURIComponent(reportType)}&start=${encodeURIComponent(startDate)}&end=${encodeURIComponent(endDate)}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Render report data (this is a placeholder, adjust as needed)
            if (data && data.length > 0) {
                let html = '<table class="table table-bordered"><thead><tr>';
                Object.keys(data[0]).forEach(key => {
                    html += `<th>${key}</th>`;
                });
                html += '</tr></thead><tbody>';
                data.forEach(row => {
                    html += '<tr>';
                    Object.values(row).forEach(val => {
                        html += `<td>${val}</td>`;
                    });
                    html += '</tr>';
                });
                html += '</tbody></table>';
                resultsDiv.innerHTML = html;
            } else {
                resultsDiv.innerHTML = '<div class="alert alert-info">No data found for the selected report.</div>';
            }
        })
        .catch(error => {
            console.error('Error generating report:', error);
            resultsDiv.innerHTML = '<div class="alert alert-danger">Error generating report. Please try again.</div>';
        });
} 