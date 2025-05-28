from flask import jsonify

class ApiResponse:
    @staticmethod
    def success(data=None, message=None, status_code=200):
        """
        Create a success response
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
        
        Returns:
            JSON response with success status
        """
        response = {
            "success": True
        }
        
        if data is not None:
            response["data"] = data
        
        if message:
            response["message"] = message
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(message, status_code=400, errors=None):
        """
        Create an error response
        
        Args:
            message: Error message
            status_code: HTTP status code
            errors: Detailed error information
        
        Returns:
            JSON response with error status
        """
        response = {
            "success": False,
            "message": message
        }
        
        if errors:
            response["errors"] = errors
        
        return jsonify(response), status_code
    
    @staticmethod
    def pagination(items, total, page, per_page, message=None):
        """
        Create a paginated response
        
        Args:
            items: List of items for current page
            total: Total number of items
            page: Current page number
            per_page: Number of items per page
            message: Optional message
        
        Returns:
            JSON response with pagination metadata
        """
        total_pages = (total + per_page - 1) // per_page
        
        response = {
            "success": True,
            "data": items,
            "pagination": {
                "total": total,
                "per_page": per_page,
                "current_page": page,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
        if message:
            response["message"] = message
        
        return jsonify(response), 200