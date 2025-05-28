import os
import subprocess
import shutil
from datetime import datetime
from utils.logger import get_logger
from utils.config_manager import config

logger = get_logger('backup')

class Backup:
    @staticmethod
    def create_database_backup():
        """
        Create a backup of the database
        
        Returns:
            Tuple (success, message)
        """
        try:
            # Get database configuration
            db_host = config.get('MYSQL_HOST', 'localhost')
            db_user = config.get('MYSQL_USER', 'library_app')
            db_password = config.get('MYSQL_PASSWORD', '')
            db_name = config.get('MYSQL_DB', 'library_management')
            
            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f"{db_name}_{timestamp}.sql")
            
            # Create mysqldump command
            command = [
                'mysqldump',
                f'--host={db_host}',
                f'--user={db_user}',
                f'--password={db_password}',
                '--single-transaction',
                '--routines',
                '--triggers',
                '--events',
                db_name
            ]
            
            # Execute command and save output to file
            with open(backup_file, 'w') as f:
                subprocess.run(command, stdout=f, check=True)
            
            logger.info(f"Database backup created: {backup_file}")
            return True, f"Backup created successfully: {os.path.basename(backup_file)}"
        
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            return False, f"Error creating backup: {str(e)}"
    
    @staticmethod
    def restore_database_backup(backup_file):
        """
        Restore database from backup
        
        Args:
            backup_file: Backup file name
        
        Returns:
            Tuple (success, message)
        """
        try:
            # Get database configuration
            db_host = config.get('MYSQL_HOST', 'localhost')
            db_user = config.get('MYSQL_USER', 'library_app')
            db_password = config.get('MYSQL_PASSWORD', '')
            db_name = config.get('MYSQL_DB', 'library_management')
            
            # Get backup file path
            backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')
            backup_path = os.path.join(backup_dir, backup_file)
            
            if not os.path.exists(backup_path):
                return False, f"Backup file not found: {backup_file}"
            
            # Create mysql command
            command = [
                'mysql',
                f'--host={db_host}',
                f'--user={db_user}',
                f'--password={db_password}',
                db_name
            ]
            
            # Execute command with backup file as input
            with open(backup_path, 'r') as f:
                subprocess.run(command, stdin=f, check=True)
            
            logger.info(f"Database restored from backup: {backup_file}")
            return True, "Database restored successfully"
        
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            return False, f"Error restoring database: {str(e)}"
    
    @staticmethod
    def list_backups():
        """
        List available database backups
        
        Returns:
            List of backup files with metadata
        """
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')
        if not os.path.exists(backup_dir):
            return []
        
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.sql'):
                file_path = os.path.join(backup_dir, filename)
                file_stat = os.stat(file_path)
                
                # Parse timestamp from filename
                timestamp = None
                try:
                    # Extract timestamp part (after database name and underscore)
                    timestamp_str = filename.split('_', 1)[1].split('.')[0]
                    timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                except (IndexError, ValueError):
                    # If parsing fails, use file modification time
                    timestamp = datetime.fromtimestamp(file_stat.st_mtime)
                
                backups.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'created_at': timestamp,
                    'file_path': file_path
                })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups