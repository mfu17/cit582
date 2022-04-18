from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import sys

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

@app.before_request
def create_session():
    g.session = scoped_session(DBSession)

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


""" Suggested helper methods """

def check_sig(payload,sig):
    payload_str = json.dumps(payload)
    sender_pk = payload.get('sender_pk')
    platform = payload.get('platform')
    
    if platform == 'Algorand':
        result = algosdk.util.verify_bytes(payload_str.encode('utf-8'),sig, sender_pk)
    elif platform == 'Ethereum':
        eth_encoded_msg = eth_account.messages.encode_defunct(text=payload_str)
        result = eth_account.Account.recover_message(eth_encoded_msg,signature=sig) == sender_pk
    return result

# def fill_order(order,txes=[]):
#     pass
  
def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    # Hint: use json.dumps or str() to get it in a nice string form
    g.session.add(Log(message=json.dumps(d)))
    g.session.commit()

""" End of helper methods """

def match_order(new_order, old_order):
    con_1 = new_order.filled == None
    con_2 = new_order.sell_currency == old_order.buy_currency
    con_3 = new_order.buy_currency == old_order.sell_currency
    con_4 = ((new_order.sell_amount * old_order.sell_amount) >= (new_order.buy_amount * old_order.buy_amount))
    return (con_1 & con_2 & con_3 & con_4) 

def process_order(order,txes=[]):
    #Your code here
    buy_currency = order['buy_currency']
    sell_currency = order['sell_currency']
    buy_amount = order['buy_amount']
    sell_amount = order['sell_amount']
    sender_pk = order['sender_pk']
    receiver_pk = order['receiver_pk']
    
    if order.get('creator_id') == None:
        new_order = Order(buy_currency = buy_currency,
                            sell_currency = sell_currency,
                            buy_amount = buy_amount,
                            sell_amount = sell_amount,
                            sender_pk = sender_pk,
                            receiver_pk = receiver_pk)
    else: 
        new_order = Order(buy_currency = buy_currency,
                            sell_currency = sell_currency,
                            buy_amount = buy_amount,
                            sell_amount = sell_amount,
                            sender_pk = sender_pk,
                            receiver_pk = receiver_pk,
                            creator_id = order.get('creator_id'))
        
    g.session.add(new_order)
    g.session.commit()
    
    unfilled = g.session.query(Order).filter(Order.filled == None).all()
    
    for old_order in unfilled:
        if match_order(new_order, old_order):
            
            old_order.filled = datetime.now()
            new_order.filled = datetime.now()
            old_order.counterparty_id = new_order.id
            new_order.counterparty_id = old_order.id
            g.session.commit()
            
            if new_order.buy_amount == old_order.sell_amount:
                pass
            else:
                child_order = {}
                if new_order.buy_amount > old_order.sell_amount:
                    child_order['buy_currency'] = new_order.buy_currency
                    child_order['sell_currency'] = new_order.sell_currency
                    child_order['buy_amount'] = new_order.buy_amount - old_order.sell_amount
                    child_order['sell_amount'] = child_order['buy_amount'] * (new_order.sell_amount / new_order.buy_amount) * 1.05
                    child_order['sender_pk'] = new_order.sender_pk
                    child_order['receiver_pk'] = new_order.receiver_pk
                    child_order['creator_id'] = new_order.id
                    
                elif new_order.buy_amount < old_order.sell_amount:
                    child_order['buy_currency'] = old_order.buy_currency
                    child_order['sell_currency'] = old_order.sell_currency
                    child_order['sell_amount'] = old_order.sell_amount - new_order.buy_amount
                    child_order['buy_amount'] = child_order['sell_amount'] * (old_order.buy_amount / old_order.sell_amount) * 0.95
                    child_order['sender_pk'] = old_order.sender_pk
                    child_order['receiver_pk'] = old_order.receiver_pk
                    child_order['creator_id'] = old_order.id
                    
                process_order(child_order)

@app.route('/trade', methods=['POST'])
def trade():
    print("In trade endpoint")
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]

        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
        
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
            
        #Your code here
        #Note that you can access the database session using g.session

        # TODO: Check the signature
        sig = content.get('sig')
        payload = content.get('payload')   
      
        # TODO: Add the order to the database
        if check_sig(payload, sig):
            order = {'sender_pk': payload.get('sender_pk'),
                     'receiver_pk': payload.get('receiver_pk'),
                     'buy_currency':payload.get('buy_currency'),
                     'sell_currency':payload.get('sell_currency'),
                     'buy_amount':payload.get('buy_amount'),
                     'sell_amount':payload.get('sell_amount')}      
  
            process_order(order)
            return jsonify(True)   
        else:
            log_message(payload)
            return jsonify(False)   
        # TODO: Fill the order
        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    #return jsonify(result)
    orders = g.session.query(Order).all()
    orders_list = []
    
    for order in orders:
        orders_list.append({'sender_pk': order.sender_pk,
                            'receiver_pk':order.receiver_pk,
                            'buy_currency':order.buy_currency,
                            'sell_currency':order.sell_currency,
                            'buy_amount':order.buy_amount,
                            'sell_amount':order.sell_amount,
                            'signature':order.signature})
    
    return json.dumps({'data':orders_list})

if __name__ == '__main__':
    app.run(port='5002')