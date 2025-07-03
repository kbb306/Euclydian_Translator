from eu_compressed import Expanded_Euclydian
Alex = Expanded_Euclydian()
phrase = input("Enter a string (preferably <100 chars): ")
Encoded = Alex.encode(phrase)
Decoded = Alex.decode(Encoded)
print("You entered:",phrase)
print("Which encodes to:",Encoded)
print("Which decodes to:",Decoded)
if phrase == Decoded:
    print("Test successful!")
else:
    print("Test failed!")