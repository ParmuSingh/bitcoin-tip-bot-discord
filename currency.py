import json
import pickle

#####################
# balance = {       #
#   'tag' : 'bal'   #
# }                 #
#####################
class Currency:
	def __init__(self):
		self.balances = {}
		self.members_list = []
		self.sat_reserve = 100

		try:
			with open("./balances.json", "r+") as balances_file:
				self.balances = json.load(balances_file)
		except:
			print("balance file is empty..")
			self.update_balance_file()

		self.members_list = list(self.balances.keys())
		print(f"members = {self.members_list}")

	def show_balance(self, id):
		return self.balances[id]

	def do_transaction(self, sender_name, sender_id, reciever_name, reciever_id, amount):
		amount = int(amount)
		print(f"initiating tx: {sender_name} -> {reciever_name} | amount = {amount}")
		
		if sender_id not in self.members_list:
			print('sender not in members_list')
			add_user_to_json(sender_id)
		if reciever_id not in self.members_list:
			print('recv not in members_list')
			add_user_to_json(reciever_id)


		valid, err = self.is_tx_valid(sender_id, reciever_id, amount)

		if valid:
			self.balances[reciever_id]  += amount
			self.balances[sender_id]    -= amount
			self.update_balance_file()
			return True, "none"
		else:
			return False, err
	def is_tx_valid(self, sender_id, receiver_id, amt):
		if self.balances[sender_id] < int(amt):
			return False, "not enough funds"
		
		return True, "none"
	def update_balance_file(self):
		with open("./balances.json", "w") as balances_file:
			json.dump(self.balances, balances_file)
	def add_user_to_json(self, userid):
		if userid not in self.members_list:
			print(f'{userid} not in member_list')
			self.balances[userid] = 0
			self.members_list.append(userid)
			self.update_balance_file()
	def close_file(self):
		pass
