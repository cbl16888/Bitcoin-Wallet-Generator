import os
range1 = int(input("Input Starting Range :> "))
range2 = int(input("Input Ending Range   :> "))

for x in range(range1,rang2):
	print(str(x))
	os.system(r'python wallet_generator.py '+ str(x))
	x = x + 1
# Donations: bc1qykc9chxvl75g3njmz7crrjj0uw59m5sxzzdsz7
