import subprocess
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Load configuration from environment variables
DB_HOST = os.getenv('MYSQL_HOST', 'localhost')
DB_PORT = os.getenv('MYSQL_PORT', '3307')
DB_USER = os.getenv('MYSQL_USER', 'root')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
DB_NAME = os.getenv('MYSQL_DB', 'hero_db')
OUTPUT_FILE = os.getenv('DB_OUTPUT_FILE', 'updated_db.sql')
CHECK_EVERY = int(os.getenv('DB_CHECK_EVERY', '10'))

# Detect mysqldump path based on OS
def get_mysqldump_path():
    """Auto-detect mysqldump path based on environment."""
    custom_path = os.getenv('MYSQLDUMP_PATH')
    
    if custom_path and os.path.exists(custom_path):
        return custom_path
    
    # Try common paths
    if os.name == 'nt':  # Windows
        common_paths = [
            r'D:\xampp\mysql\bin\mysqldump.exe',
            r'C:\xampp\mysql\bin\mysqldump.exe',
            r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe',
            r'C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysqldump.exe',
        ]
    else:  # Linux/Mac
        common_paths = [
            '/usr/bin/mysqldump',
            '/usr/local/bin/mysqldump',
            '/opt/mysql/bin/mysqldump',
        ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"✅ Found mysqldump at: {path}")
            return path
    
    # Fallback to system PATH
    return 'mysqldump'


MYSQLDUMP_PATH = get_mysqldump_path()


def export_database():
    """Export database using mysqldump utility."""
    
    if DB_PASSWORD:
        command = [
            MYSQLDUMP_PATH,
            f'--host={DB_HOST}',
            f'--port={DB_PORT}',
            f'--user={DB_USER}',
            f'--password={DB_PASSWORD}',
            '--routines',
            '--triggers',
            '--single-transaction',
            DB_NAME
        ]
    else:
        command = [
            MYSQLDUMP_PATH,
            f'--host={DB_HOST}',
            f'--port={DB_PORT}',
            f'--user={DB_USER}',
            '--routines',
            '--triggers',
            '--single-transaction',
            DB_NAME
        ]

    try:
        with open(OUTPUT_FILE, 'w') as f:
            subprocess.run(command, stdout=f, stderr=subprocess.PIPE, check=True)
        now = datetime.now().strftime('%H:%M:%S')
        print(f"[{now}] ✅ Database exported to {OUTPUT_FILE}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Export failed: {e.stderr.decode()}")
        return False
    except FileNotFoundError:
        print(f"❌ mysqldump not found at: {MYSQLDUMP_PATH}")
        print("   Install MySQL Server or set MYSQLDUMP_PATH in .env")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during export: {str(e)}")
        return False


def get_db_last_modified():
    """Check the last modification time of the database."""
    
    try:
        import MySQLdb
        conn = MySQLdb.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            passwd=DB_PASSWORD,
            db='information_schema'
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(UPDATE_TIME) 
            FROM TABLES 
            WHERE TABLE_SCHEMA = %s
        """, (DB_NAME,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return str(result[0]) if result and result[0] else None
    except MySQLdb.Error as e:
        print(f"⚠️ Database connection error: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Could not check DB modification time: {e}")
        return None


def main():
    """Main function to run the auto export service."""
    
    print("🚀 Auto DB Export started. Watching for changes...")
    print(f"   Database : {DB_NAME}")
    print(f"   Host     : {DB_HOST}:{DB_PORT}")
    print(f"   Output   : {OUTPUT_FILE}")
    print(f"   Checking every {CHECK_EVERY} seconds")
    print("   Press Ctrl+C to stop\n")

    # Initial export
    export_database()
    last_known_time = get_db_last_modified()

    try:
        while True:
            time.sleep(CHECK_EVERY)
            current_time = get_db_last_modified()

            if current_time != last_known_time:
                print(f"🔄 Change detected! Exporting...")
                if export_database():
                    last_known_time = current_time
    except KeyboardInterrupt:
        print("\n\n⛔ Auto DB Export stopped by user")


if __name__ == '__main__':
    main()
