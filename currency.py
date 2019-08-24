import json

#####################
# balance = {		#
# 	'tag' : 'bal'	#
# }					#
#####################
class Currency:
	def __init__(self, server):
		self.server = server
		self.balances_file = open(f"./balances.json", "r+")
		self.balances = {}
		self.member_list = []
		self.sat_reserve = 100
		for member in server.members:
			if not member.bot:
				self.member_list.append(str(member).split('#')[1])
		
		try:
			self.balances = json.load(self.balances_file)
			# self.member_list = [str(member).split("#")[1] for member in server.members]
		except:
			print("balance file doesn't exist, creating..")
			for member in member_list:
				self.balances[member] = 0
			self.update_balance_file()

		# print(self.member_list) # includes bots
	def show_balance(self):
		return self.balances

	def do_transaction(self, sender_name, reciever_name, amount):
		amount = int(amount)
		print(f"initiating tx: {sender_name} -> {reciever_name} | amount = {amount}")
		
		valid, err = self.is_tx_valid(sender_name, reciever_name, amount)

		if valid:
			self.balances[self.get_tag(reciever_name)]	+= amount
			self.balances[self.get_tag(sender_name)] 	-= amount
			self.update_balance_file()
			return True, "none"
		else:
			return False, err
	def is_tx_valid(self, sender, receiver, amt):
		if self.balances[self.get_tag(sender)] <= int(amt):
			return False, "not enough funds"
		
		receiver_exists = False
		# checking if name exists
		for member in self.server.members:
			if receiver.lower() == member.name.lower():
				receiver_exists = True
				break
		if not receiver_exists:
			return False, "recipeint_doesn't exist"

		if self.get_tag(receiver) not in self.member_list:
			return False, "recipeint doesn't exist"
		
		return True, "none"
	def get_tag(self, name):
		for member in self.server.members:
			if str(member).split('#')[0].lower() == name.lower():
				# print(str(member).split('#')[1])
				return str(member).split('#')[1]
	def update_balance_file(self):
		self.balances_file.seek(0)
		json.dump(self.balances, self.balances_file)
		self.balances_file.truncate()
	def close_file(self):
		self.balances_file.close()