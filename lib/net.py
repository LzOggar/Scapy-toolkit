import re
import threading

try:
	from scapy.all import *
except ImportError as err:
	print(err)

def is_valid_target(target):
	"""
	"""
	
	regex = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/(3[0-2]|[1-2][0-9]|[0-9]))?$")
	if regex.match(target) == None:
		return False
	else:
		return True

class ICMPThread(threading.Thread):

	def __init__(self, target, result):
		threading.Thread.__init__(self)
		self.target = target
		self.result = result

	def run(self):
		"""
		"""

		pkt = IP(dst=self.target)/ICMP(type=8)
		ans = sr1(pkt, timeout=0.5, verbose=0)

		if ans["ICMP"].type == 0:
			self.result[self.target] = "up"
		else:
			self.result[self.target] = "down"

