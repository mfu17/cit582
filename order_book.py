from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def match_order(new_order, old_order):
    con_1 = new_order.filled == None
    con_2 = new_order.sell_currency == old_order.buy_currency
    con_3 = new_order.buy_currency == old_order.sell_currency
    con_4 = ((new_order.sell_amount * old_order.sell_amount) >= (new_order.buy_amount * old_order.buy_amount))
    return (con_1 & con_2 & con_3 & con_4) 

def process_order(order):
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
        
    session.add(new_order)
    session.commit()
    
    unfilled = session.query(Order).filter(Order.filled == None).all()
    
    for old_order in unfilled:
        if match_order(new_order, old_order):
            
            old_order.filled = datetime.now()
            new_order.filled = datetime.now()
            old_order.counterparty_id = new_order.id
            new_order.counterparty_id = old_order.id
            session.commit()
            
            if new_order.buy_amount == old_order.sell_amount:
                return
            else:
                child_order = {}
                if new_order.buy_amount > old_order.sell_amount:
                    child_order['buy_currency'] = new_order.buy_currency
                    child_order['sell_currency'] = new_order.sell_currency
                    child_order['buy_amount'] = new_order.buy_amount - old_order.sell_amount
                    child_order['sell_amount'] = child_order['buy_amount'] * (new_order.sell_amount / new_order.buy_amount)*1.01
                    child_order['sender_pk'] = new_order.sender_pk
                    child_order['receiver_pk'] = new_order.receiver_pk
                    child_order['creator_id'] = new_order.id
                    
                elif new_order.buy_amount < old_order.sell_amount:
                    child_order['buy_currency'] = old_order.buy_currency
                    child_order['sell_currency'] = old_order.sell_currency
                    child_order['sell_amount'] = old_order.sell_amount - new_order.buy_amount
                    child_order['buy_amount'] = child_order['sell_amount'] * (old_order.buy_amount / old_order.sell_amount)*0.99
                    child_order['sender_pk'] = old_order.sender_pk
                    child_order['receiver_pk'] = old_order.receiver_pk
                    child_order['creator_id'] = old_order.id
                    
                process_order(child_order)
    
    #pass
