# app.py
from flask import Flask, render_template,jsonify, request
from flask_socketio import SocketIO, emit
from flask_caching import Cache
from threading import Lock


import os

app = Flask(__name__)
#socketio = SocketIO(app)
socketio = SocketIO(app, engineio_logger=True, max_http_buffer_size=10*1024*1024,async_mode='threading')

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))


# Construct the file path relative to the script directory
file_name = os.path.join(script_dir, 'counts.txt')

def read_counts_from_file():
    with open(file_name, 'r') as f:
        yes_count, no_count = map(int, f.read().split())
    return yes_count, no_count

def write_counts_to_file(yes_count, no_count):
    with open(file_name, 'w') as f:
        f.write(f"{yes_count} {no_count}")

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def read_counts_from_cache():
    yes_count = cache.get('yes_count') or 0
    no_count = cache.get('no_count') or 0
    return yes_count, no_count

def write_counts_to_cache(yes_count, no_count):
    cache.set('yes_count', yes_count)
    cache.set('no_count', no_count)

cache_lock = Lock()
@socketio.on('increment')
def handle_increment(data):
    with cache_lock:  # 캐시 액세스를 동기화
        yes_count, no_count = read_counts_from_cache()

        # count value from client
        client_value = data['value'] + 1

        if data['countId'] == 'yesCount' and client_value > yes_count:
            yes_count = client_value
            write_counts_to_cache(yes_count, no_count)
            emit('update_count', {'countId': data['countId'], 'value': yes_count}, broadcast=True)
        elif data['countId'] == 'noCount' and client_value > no_count:
            no_count = client_value
            write_counts_to_cache(yes_count, no_count)
            emit('update_count', {'countId': data['countId'], 'value': no_count}, broadcast=True)



@socketio.on('reset_counts')
def handle_reset():
    # 모든 클라이언트에게 카운트를 0으로 리셋
    write_counts_to_cache(0, 0)
    emit('update_count', {'countId': 'yesCount', 'value': 0}, broadcast=True)
    emit('update_count', {'countId': 'noCount', 'value': 0}, broadcast=True)

@socketio.on('get_initial_counts')
def get_initial_counts():
    yes_count, no_count = read_counts_from_cache()
    print("initial yes count : ", yes_count)
    emit('update_count', {'countId': 'yesCount', 'value': yes_count}, broadcast=True)
    emit('update_count', {'countId': 'noCount', 'value': no_count}, broadcast=True)

# @app.route('/get_initial_counts')
# def get_initial_counts():
#     yes_count, no_count = read_counts_from_file()
#     return jsonify(yes=yes_count, no=no_count)

@app.route('/')
@app.route('/<path>')
def index(path=None):
    is_admin = path == 'aimltfcadmin'
    return render_template('index.html', is_admin=is_admin)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
