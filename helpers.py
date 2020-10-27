import logging
def log(msg, type='info'):
	print(msg)
	if type=='info':
		logging.info(msg)
	elif type=='error':
		logging.error(msg)
	elif type=='debug':
		logging.debug(msg)
	elif type=='critical':
		logging.critical(msg)
