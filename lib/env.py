"""
    Environment file.
"""

import os

root_path = os.path.dirname(os.path.abspath("Scapy-toolkit"))
history_logs_path = os.path.join(root_path, "logs", "history.logs")
shell_logs_path = os.path.join(root_path, "logs", "shell.logs")
shell_settings_path = os.path.join(root_path, "settings", "shell.json")

var_sets = { 
			"scan_type": {
							"icmp":"icmp",
			  				"tcp-syn":"tcp-syn",
			  				"default":"icmp" 
			  			}
		}