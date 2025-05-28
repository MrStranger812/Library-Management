from math import ceil
from flask import request, url_for

class Pagination:
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
    
    @property
    def pages(self):
        """Total number of pages"""
        return ceil(self.total_count / self.per_page)
    
    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1
    
    @property
    def has_next(self):
        """True if a next page exists"""
        return self.page < self.pages
    
    @property
    def offset(self):
        """Offset for SQL query"""
        return (self.page - 1) * self.per_page
    
    def get_page_items(self, items):
        """Get items for current page"""
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        return items[start:end]
    
    def get_pagination_data(self):
        """Get pagination metadata"""
        return {
            'page': self.page,
            'per_page': self.per_page,
            'total': self.total_count,
            'pages': self.pages,
            'has_prev': self.has_prev,
            'has_next': self.has_next
        }
    
    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        """
        Generate page numbers for pagination
        
        Args:
            left_edge: Number of pages on the left edge
            left_current: Number of pages left of current page
            right_current: Number of pages right of current page
            right_edge: Number of pages on the right edge
        
        Yields:
            Page numbers for pagination
        """
        last = 0
        for num in range(1, self.pages + 1):
            if (num <= left_edge or
                (self.page - left_current - 1 < num < self.page + right_current) or
                num > self.pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num

def get_pagination_args():
    """Get pagination arguments from request"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10
        if per_page > 100:
            per_page = 100
    except (TypeError, ValueError):
        page = 1
        per_page = 10
    
    return page, per_page