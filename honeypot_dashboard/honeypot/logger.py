import pymysql
import logging

def log_access(ip, filename, ua):
    try:
        conn = pymysql.connect(host="localhost", user="amir", password="88226464", database="honeypot")
        cur = conn.cursor()
        cur.execute("INSERT INTO access_logs (ip_address, file_accessed, user_agent) VALUES (%s, %s, %s)", (ip, filename, ua))
        conn.commit()
        logging.info(f"Access logged: {ip} accessed {filename} with {ua}")
    except Exception as e:
        logging.error(f"Error logging access: {e}")
    finally:
        cur.close()
        conn.close()
