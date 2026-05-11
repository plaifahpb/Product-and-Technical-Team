import os
from waitress import serve
from app import app

port = int(os.environ.get('PORT', 5000))
host = os.environ.get('HOST', '0.0.0.0')

if __name__ == '__main__':
    print(f'Starting Task Tracker Team Server on http://{host}:{port}')
    serve(app, host=host, port=port, threads=8, connection_limit=200, channel_timeout=120)
