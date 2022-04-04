from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine, select, MetaData, Table
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

#These decorators allow you to use g.session to access the database inside the request code
@app.before_request
def create_session():
    g.session = scoped_session(DBSession) #g is an "application global" https://flask.palletsprojects.com/en/1.1.x/api/#application-globals

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    g.session.commit()
    g.session.remove()

"""
-------- Helper methods (feel free to add your own!) -------
"""

def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    g.session.add(Log(message=json.dumps(d)))
    g.session.commit()
    #pass

"""
---------------- Endpoints ----------------
"""
    
@app.route('/trade', methods=['POST'])
def trade():
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]
        error = False
        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
        
        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                error = True
        if error:
            print( json.dumps(content) )
            log_message(content)
            return jsonify( False )
            
        #Your code here
        #Note that you can access the database session using g.session
        payload = content.get('payload')
        payload_str = json.dumps(payload)
        sig = content.get('sig')
        sender_pk = payload.get('sender_pk')
        platform = payload.get('platform')

        if platform == 'Ethereum':
            eth_encoded_msg = eth_account.messages.encode_defunct(text=payload_str)
            result = eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == sender_pk
        elif platform == 'Algorand':
            result = algosdk.util.verify_bytes(payload_str.encode('utf-8'), sig, sender_pk)

        if result:
            g.session.add(Order(sender_pk = sender_pk,
                                receiver_pk = payload.get('receiver_pk'),
                                buy_currency = payload.get('buy_currency'),
                                sell_currency = payload.get('sell_currency'),
                                buy_amount = payload.get('buy_amount'),
                                sell_amount = payload.get('sell_amount'),
                                signature = sig))
            g.session.commit()
        else:
            log_message(payload)
            
        return jsonify(result)        

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    orders = g.session.query(Order)
    orders_array = []
    
    for order in orders:
        orders_array.append({'sender_pk': order.sender_pk,
                            'receiver_pk': order.receiver_pk,
                            'buy_currency': order.buy_currency,
                            'sell_currency': order.sell_currency,
                            'buy_amount': order.buy_amount,
                            'sell_amount': order.sell_amount,
                            'signature': order.signature})
    
    return json.dumps({'data':orders_array})
    #return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')
