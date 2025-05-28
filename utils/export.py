import csv
import io
from flask import make_response
from datetime import datetime
import pdfkit  # You'll need to install this: pip install pdfkit

def export_to_csv(data, filename, headers=None):
    """
    Export data to CSV file
    
    Args:
        data: List of dictionaries or tuples
        filename: Name of the file to be downloaded
        headers: List of column headers (optional)
    
    Returns:
        Flask response object with CSV attachment
    """
    si = io.StringIO()
    writer = csv.writer(si)
    
    # Write headers
    if headers:
        writer.writerow(headers)
    elif data and isinstance(data[0], dict):
        writer.writerow(data[0].keys())
    
    # Write data
    if data and isinstance(data[0], dict):
        for row in data:
            writer.writerow(row.values())
    else:
        writer.writerows(data)
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    output.headers["Content-type"] = "text/csv"
    
    return output

def export_to_pdf(data, filename, headers=None, title="Exported Data"):
    """
    Export data to PDF file
    
    Args:
        data: List of dictionaries or tuples
        filename: Name of the file to be downloaded
        headers: List of column headers (optional)
        title: Title for the PDF document
    
    Returns:
        Flask response object with PDF attachment
    """
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            h1 {{ text-align: center; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <table>
            <thead>
                <tr>
    """
    
    # Add headers to HTML
    if headers:
        for header in headers:
            html_content += f"<th>{header}</th>"
    elif data and isinstance(data[0], dict):
        for key in data[0].keys():
            html_content += f"<th>{key}</th>"
    
    html_content += """
                </tr>
            </thead>
            <tbody>
    """
    
    # Add data rows to HTML
    if data and isinstance(data[0], dict):
        for row in data:
            html_content += "<tr>"
            for value in row.values():
                html_content += f"<td>{value}</td>"
            html_content += "</tr>"
    else:
        for row in data:
            html_content += "<tr>"
            for value in row:
                html_content += f"<td>{value}</td>"
            html_content += "</tr>"
    
    html_content += """
            </tbody>
        </table>
        <p style="text-align: center; margin-top: 20px;">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </body>
    </html>
    """
    
    # Convert HTML to PDF
    pdf = pdfkit.from_string(html_content, False)
    
    # Create response
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    
    return response