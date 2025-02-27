# config.py
DB_CONFIG = {
    'host': '15.168.145.74',
    'user': 'lab05',
    'password': 'Itmomdan0227!!',  # 실제 비밀번호로 변경
    'database': 'saltyitmomdan_db',
    'port': 3306
}

# HDFS 기본 경로 설정
HDFS_BASE_PATH = "hdfs://localhost:9000/shared_data"

# HDFS 기본 경로
HDFS_CONFIG = {
    "defaultFS": "hdfs://localhost:9000" 
}

# MySQL JDBC 드라이버 경로
MYSQL_JDBC = "/home/ubuntu/mysql-connector-j-9.2.0/mysql-connector-j-9.2.0.jar"