from smaz import compress, decompress
from alphacodings import base26_encode, base26_decode

class Expanded_Euclydian:
    @staticmethod
    def encode(phrase):
        """Compress Text and return a base26 string"""
        compressed = compress(phrase)
        print("Compressed to",compressed)
        encoded = base26_encode(compressed)
        return encoded
    
    @staticmethod
    def decode(codephrase):
        """Decodes and decompresses a base26 encoded string."""
        decoded = base26_decode(codephrase)
        decompressed = decompress(decoded)
        return decompressed