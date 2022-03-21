from flask import Flask, request, jsonify
from flask_restful import Api
import json
import eth_account
import algosdk

app = Flask(__name__)
api = Api(app)
app.url_map.strict_slashes = False

@app.route('/verify', methods=['GET','POST'])
def verify():
    content = request.get_json(silent=True)

    payload = content.get('payload')
    payload_str = json.dumps(payload)
    sig = content.get('sig')
    pk = payload.get('pk')
    platform = payload.get('platform')

    if platform == 'Algorand':
        result = algosdk.util.verify_bytes(payload_str.encode('utf-8'), sig, pk)
    elif platform == 'Ethereum':
        eth_encoded_msg = eth_account.messages.encode_defunct(text=payload_str)
        result = eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == pk

    #Check if signature is valid
    #result = True #Should only be true if signature validates
    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')
