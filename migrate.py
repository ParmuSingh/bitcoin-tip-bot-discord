####################################################################################################################
# Migration from one wallet system to each user having their own lnpay wallet system.
####################################################################################################################
from pymongo import MongoClient
import lnpay_py
from lnpay_py.wallet import LNPayWallet
lnpay_central_wallet_admin_key = open('./private_data/lnpay_wallet_key_admin.txt', 'r').read().split('\n')[0]
lnpay_api_key = open('./private_data/lnpay_api_key.txt', 'r').read().split('\n')[0]
lnpay_py.initialize(lnpay_api_key)

def create_wallet(name):
	wallet_params = {
	    'user_label': name
	}
	new_wallet = lnpay_py.create_wallet(wallet_params)
	return new_wallet


# get all users
client = MongoClient("mongodb://localhost:27017")
db = client['btc-discord-bot']

users = db['users'].find()

for user in users:
    user_id = user['user_id']

    # create their lnpay wallet
    new_wallet = create_wallet("discord-bot-user-"+user_id)
    print("new wallet created:")
    print(new_wallet)
    print("\n")

    # save keys to database
    user = db['users'].find_one({'user_id': user_id})
    user['wallet'] = new_wallet

    db['users'].update_one({'user_id': user_id}, {"$set": user})

    # transfer their balance from central wallet to this new wallet
    balance = user['balance']
    sender_wallet = LNPayWallet(lnpay_central_wallet_admin_key)
    receiver_wallet_id = new_wallet["id"]

    transfer_params = {
        'dest_wallet_id': receiver_wallet_id,
        'num_satoshis': balance,
        'memo': 'migration transaction'
    }
    transfer_result = sender_wallet.internal_transfer(transfer_params)
