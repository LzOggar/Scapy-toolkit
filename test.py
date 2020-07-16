try:
	from lib import shell
except ImportError as err:
	print(err)

s = shell.Shell()
s.run()