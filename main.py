# app.py
from flask import Flask, render_template,jsonify, request
import os

app = Flask(__name__)
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the file path relative to the script directory
file_name = os.path.join(script_dir, 'counts.txt')
print('CHCHC : ', file_name)
@app.route('/get_counts', methods=['GET'])
def get_counts():
    print('1111')
    with open(file_name, 'r+') as f:
        yes_count, no_count = map(int, f.read().split())
    return jsonify({"yes": yes_count, "no": no_count})

@app.route('/update_counts', methods=['POST'])
def update_counts():
    print("CHECK UPDATE : ",request.json.get('yes'))
    yes = request.json.get('yes')
    no = request.json.get('no')
    with open(file_name, 'w') as f:
        f.write(f"{yes} {no}")
    return jsonify({"message": "Counts updated successfully!"})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
