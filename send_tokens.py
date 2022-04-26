#!/usr/bin/python3

from algosdk.v2client import algod
from algosdk.v2client import indexer
from algosdk import account
from algosdk.future import transaction

def connect_to_algo(connection_type=''):
    #Connect to Algorand node maintained by PureStake
    algod_token = "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab"
    
    if connection_type == "indexer":
        # TODO: return an instance of the v2client indexer. This is used for checking payments for tx_id's
        algod_address = "https://testnet-algorand.api.purestake.io/idx2"
        token = {'X-Api-key':algod_token}
        client = indexer.IndexerClient(algod_token, algod_address, headers=token)
    else:
        # TODO: return an instance of the client for sending transactions
        # Tutorial Link: https://developer.algorand.org/tutorials/creating-python-transaction-purestake-api/
        algod_address = "https://testnet-algorand.api.purestake.io/ps2"
        token = {'X-Api-key':algod_token}
        client = algod.AlgodClient(algod_token, algod_address, headers=token)

    return client

def send_tokens_algo( acl, sender_sk, txes):
    params = acl.suggested_params
    
    # TODO: You might want to adjust the first/last valid rounds in the suggested_params
    #       See guide for details

    # TODO: For each transaction, do the following:
    #       - Create the Payment transaction 
    #       - Sign the transaction
    
    # TODO: Return a list of transaction id's

    sender_pk = account.address_from_private_key(sender_sk)

    tx_ids = []
    for i,tx in enumerate(txes):
        
        params.first += i
        receiver_pk = tx['receiver_pk']
        sell_amount = tx['order'].sell_amount
        unsigned_tx = transaction.PaymentTxn(sender_pk, params, receiver_pk, sell_amount)        
                
        #unsigned_tx = "Replace me with a transaction object"

        # TODO: Sign the transaction
        #signed_tx = "Replace me with a SignedTransaction object"
        signed_tx = unsigned_tx.sign(sender_sk)
        
        try:
            print(f"Sending {tx['amount']} microalgo from {sender_pk} to {tx['receiver_pk']}" )
            acl.send_transaction(signed_tx)
            # TODO: Send the transaction to the testnet
            
            #tx_id = "Replace me with the tx_id"
            tx_id = acl.send_transaction(signed_tx)
            
            txinfo = wait_for_confirmation_algo(acl, txid=tx_id )
            print(f"Sent {tx['amount']} microalgo in transaction: {tx_id}\n" )
            tx_ids.append(tx_id)
        except Exception as e:
            print(e)
        
    return tx_ids

# Function from Algorand Inc.
def wait_for_confirmation_algo(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo

##################################

from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.exceptions import TransactionNotFound
import json
import progressbar


def connect_to_eth():
    IP_ADDR='3.23.118.2' #Private Ethereum
    PORT='8545'

    w3 = Web3(Web3.HTTPProvider('http://' + IP_ADDR + ':' + PORT))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0) #Required to work on a PoA chain (like our private network)
    w3.eth.account.enable_unaudited_hdwallet_features()
    if w3.isConnected():
        return w3
    else:
        print( "Failed to connect to Eth" )
        return None

def wait_for_confirmation_eth(w3, tx_hash):
    print( "Waiting for confirmation" )
    widgets = [progressbar.BouncingBar(marker=progressbar.RotatingMarker(), fill_left=False)]
    i = 0
    with progressbar.ProgressBar(widgets=widgets, term_width=1) as progress:
        while True:
            i += 1
            progress.update(i)
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
            except TransactionNotFound:
                continue
            break 
    return receipt


####################
def send_tokens_eth(w3,sender_sk,txes):
    sender_account = w3.eth.account.privateKeyToAccount(sender_sk)
    sender_pk = sender_account._address

    # TODO: For each of the txes, sign and send them to the testnet
    # Make sure you track the nonce -locally-
    nonce0 = w3.eth_get_transaction_count(sender_pk, "pending")
    
    tx_ids = []
    for i,tx in enumerate(txes):
        receiver_pk = tx.receiver_pk
        tx_amount = tx.order.amount.sell_amount
        tx_dict = {'nonce': nonce0 + i,
                   'gasPrice': w3.eth_gas_price,
                   'gas': w3.eth.estimate_gas({'form': sender_pk, 'to': receiver_pk, 'data': b'', 'amount': tx_amount}),
                   'to': receiver_pk,
                   'value': tx_amount,
                   'data':b''}
        signed = w3.eth_account.sign_transaction(tx_dict, sender_sk)
        tx_id = w3.eth.send_raw_transactions(signed.rawTransaction)
        tx_ids.append(tx_id)
                   

    return tx_ids

# # #!/usr/bin/python3

# from algosdk.v2client import algod
# from algosdk import mnemonic
# from algosdk import transaction

# #Connect to Algorand node maintained by PureStake
# algod_address = "https://testnet-algorand.api.purestake.io/ps2"
# algod_token = "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab"
# #algod_token = 'IwMysN3FSZ8zGVaQnoUIJ9RXolbQ5nRY62JRqF2H'
# headers = {
#    "X-API-Key": algod_token,
# }

# acl = algod.AlgodClient(algod_token, algod_address, headers)
# min_balance = 100000 #https://developer.algorand.org/docs/features/accounts/#minimum-balance

# def send_tokens( receiver_pk, tx_amount ):
#     params = acl.suggested_params()
#     gen_hash = params.gh
#     first_valid_round = params.first
#     tx_fee = params.min_fee
#     last_valid_round = params.last

#     #Your code here
#     mnemonic_secret = "monkey seed matter social panther soda amazing often honey fall denial bring combine donor concert step law among write bronze jazz smile stage ability cross"
#     sender_sk = mnemonic.to_private_key(mnemonic_secret)
#     sender_pk = mnemonic.to_public_key(mnemonic_secret)

#     tx = transaction.PaymentTxn(sender_pk, tx_fee, first_valid_round, last_valid_round, gen_hash, receiver_pk, tx_amount)
#     signed_tx = tx.sign(sender_sk)
#     tx_confirm = acl.send_transaction(signed_tx)
#     txid = signed_tx.transaction.get_txid()

#     return sender_pk, txid

# # Function from Algorand Inc.
# def wait_for_confirmation(client, txid):
#     """
#     Utility function to wait until the transaction is
#     confirmed before proceeding.
#     """
#     last_round = client.status().get('last-round')
#     txinfo = client.pending_transaction_info(txid)
#     while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
#         print("Waiting for confirmation")
#         last_round += 1
#         client.status_after_block(last_round)
#         txinfo = client.pending_transaction_info(txid)
#     print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
#     return txinfo

# # from algosdk import account
# # my_pk, account_1 = account.generate_account()
# # mnemonic_secret = mnemonic.from_private_key(my_pk)
# # sender_pk = mnemonic.to_public_key(mnemonic_secret)

# # print("my_pk: " + my_pk)
# # print("account_1: " + account_1)
# # print("mnemonic_secret: " + mnemonic_secret)
# # print("sender_pk: " + sender_pk)
