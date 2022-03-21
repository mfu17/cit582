#!/usr/bin/python3

from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk import transaction

#Connect to Algorand node maintained by PureStake
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab"
#algod_token = 'IwMysN3FSZ8zGVaQnoUIJ9RXolbQ5nRY62JRqF2H'
headers = {
   "X-API-Key": algod_token,
}

acl = algod.AlgodClient(algod_token, algod_address, headers)
min_balance = 100000 #https://developer.algorand.org/docs/features/accounts/#minimum-balance

def send_tokens( receiver_pk, tx_amount ):
    params = acl.suggested_params()
    gen_hash = params.gh
    first_valid_round = params.first
    tx_fee = params.min_fee
    last_valid_round = params.last

    #Your code here
    mnemonic_secret = "monkey seed matter social panther soda amazing often honey fall denial bring combine donor concert step law among write bronze jazz smile stage ability cross"
    sender_sk = mnemonic.to_private_key(mnemonic_secret)
    sender_pk = mnemonic.to_public_key(mnemonic_secret)

    tx = transaction.PaymentTxn(sender_pk, tx_fee, first_valid_round, last_valid_round, gen_hash, receiver_pk, tx_amount)
    signed_tx = tx.sign(sender_pk)
    tx_confirm = acl.send_transaction(signed_tx)
    txid = signed_tx.transaction.get_txid()

    return sender_pk, txid

# Function from Algorand Inc.
def wait_for_confirmation(client, txid):
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

# from algosdk import account
# my_pk, account_1 = account.generate_account()
# mnemonic_secret = mnemonic.from_private_key(my_pk)
# sender_pk = mnemonic.to_private_key(mnemonic_secret)

# print("my_pk: " + my_pk)
# print("account_1: " + account_1)
# print("mnemonic_secret: " + mnemonic_secret)
# print("sender_pk: " + sender_pk)

