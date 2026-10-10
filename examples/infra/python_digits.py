import sys

# Trusted contest input only; affects conversions, not int arithmetic.
sys.set_int_max_str_digits(0)
x = int("9" * 5000)
assert len(str(x)) == 5000
assert len(str(x + 1)) == 5001
print("digits: pass")
