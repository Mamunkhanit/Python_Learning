import json
import math
import sys


def main():
	checks = {
		"arithmetic": 2 + 2 == 4,
		"math module": math.isclose(math.sqrt(81), 9),
		"JSON round-trip": json.loads(json.dumps({"python": True})) == {"python": True},
	}

	print(f"Python {sys.version.split()[0]}")
	print(f"Interpreter: {sys.executable}")

	failed = []
	for name, passed in checks.items():
		print(f"{'PASS' if passed else 'FAIL'}: {name}")
		if not passed:
			failed.append(name)

	if failed:
		raise SystemExit(f"Python smoke test failed: {', '.join(failed)}")

	print("Python environment is working.")

def typewriter_effect(text, delay=0.05):
	import sys
	import time

	for char in text:
		sys.stdout.write(char)
		sys.stdout.flush()
		time.sleep(delay)
	 # Move to the next line after finishing

text= "Python environment is working. typewriter effect test. VS code is working"

typewriter_effect(text, delay=0.05)

#if __name__ == "__main__":
#	main()
