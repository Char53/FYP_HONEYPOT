
from flask import Flask, request
from honeypot.logger import log_access

app = Flask(__name__)

@app.route('/cloud/<filename>')
def access_file(filename):
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    log_access(ip, filename, ua)
    return f"Accessing {filename}... (This is a honeypot file!)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
