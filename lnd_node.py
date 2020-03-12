import base64, codecs, json, requests
#imma just use console
import subprocess


def withdraw(pay_req=""):

	sendpayment = subprocess.call(["lncli", "sendpayment", "--pay_req="+pay_req, "--force"]) # force so it doesn't ask for confirmation
	
	if sendpayment == 1:
		return True, "none"
	else:
		return False, "check invoice"

