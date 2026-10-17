from flask import *
import os
app = Flask(__name__)
commandList = []
@app.route('/Command/send', methods=['POST'])
def send_command(command):
    commandList.append(command)

    return 200
@app.route('/Command/get', methods=['GET'])
def get_commands():
    return str(commandList[0]) if commandList else ""
@app.route('/Command/finish', methods=['GET'])
def finish_command():
    if commandList:
        commandList.pop(0)
    return 200
app.run(debug=False, host=os.sys.argv[1] if len(os.sys.argv) > 1 else '127.0.0.1', port=os.sys.argv[2] if len(os.sys.argv) > 2 else 11111)