from utils.db_manager import insert_and_get_id, execute_query
class Membership:
    @staticmethod
    def create_membership(user_id, membership_type_id, duration_months=12):
        """Create a new membership for a user"""
        from datetime import date, timedelta
        start_date = date.today()
        end_date = start_date + timedelta(days=duration_months * 30)
        
        query = """
            INSERT INTO user_memberships (user_id, membership_type_id, start_date, end_date)
            VALUES (%s, %s, %s, %s)
        """
        return insert_and_get_id(query, (user_id, membership_type_id, start_date, end_date))
    
    @staticmethod
    def get_user_current_membership(user_id):
        """Get user's current active membership"""
        query = """
            SELECT 
                um.membership_id, um.start_date, um.end_date,
                mt.name, mt.max_books_allowed, mt.loan_duration_days,
                mt.fine_rate_per_day, mt.annual_fee
            FROM user_memberships um
            JOIN membership_types mt ON um.membership_type_id = mt.membership_type_id
            WHERE um.user_id = %s 
              AND um.is_active = TRUE 
              AND um.end_date > CURDATE()
            ORDER BY um.end_date DESC
            LIMIT 1
        """
        return execute_query(query, (user_id,), dictionary=True, fetchall=False)
    
    @staticmethod
    def get_membership_types():
        """Get all available membership types"""
        query = """
            SELECT membership_type_id, name, description, max_books_allowed,
                   loan_duration_days, fine_rate_per_day, annual_fee
            FROM membership_types
            WHERE is_active = TRUE
            ORDER BY annual_fee
        """
        return execute_query(query, dictionary=True)