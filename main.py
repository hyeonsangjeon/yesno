# app.py
from flask import Flask, render_template,jsonify, request
from flask_socketio import SocketIO, emit

import os

app = Flask(__name__)
socketio = SocketIO(app)
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the file path relative to the script directory
file_name = os.path.join(script_dir, 'counts.txt')
#print('CHCHC : ', file_name)

def read_counts_from_file():
    with open('counts.txt', 'r') as f:
        yes_count, no_count = map(int, f.read().split())
    return yes_count, no_count

def write_counts_to_file(yes_count, no_count):
    with open('counts.txt', 'w') as f:
        f.write(f"{yes_count} {no_count}")


@socketio.on('increment')
def handle_increment(data):
    yes_count, no_count = read_counts_from_file()
    print("data['countId'] : ", data['countId'])
    if data['countId'] == 'yesCount':
        yes_count += 1
        emit('update_count', {'countId': data['countId'], 'value': yes_count}, broadcast=True)
    else:
        no_count += 1
        emit('update_count', {'countId': data['countId'], 'value': no_count}, broadcast=True)
    write_counts_to_file(yes_count, no_count)


@socketio.on('reset_counts')
def handle_reset():
    # 모든 클라이언트에게 카운트를 0으로 리셋
    write_counts_to_file(0,0)
    emit('update_count', {'countId': 'yesCount', 'value': 0}, broadcast=True)
    emit('update_count', {'countId': 'noCount', 'value': 0}, broadcast=True)

@socketio.on('get_initial_counts')
def get_initial_counts():
    yes_count, no_count = read_counts_from_file()
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
