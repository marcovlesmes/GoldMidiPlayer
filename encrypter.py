import random, os, struct
from Crypto.Cipher import AES


class SoundCoder:
    def __init__(self):
        self.key = '614E645267556B58'
        self.size_chunk = 16

    def encrypt_sound_found(self, in_file_path, out_file_path):
        iv = ''.join([chr(random.randint(0, 0xFF)) for i in range(16)])
        aes = AES.new(self.key, AES.MODE_CBC, iv)
        file_size = os.stat(in_file_path)[6]

        with open(in_file_path, 'rb') as in_file:
            with open(out_file_path, 'wb') as out_file:

                out_file.write(struct.pack('<Q', file_size))
                out_file.write(iv)

                while True:
                    data = in_file.read(self.size_chunk)
                    n = len(data)
                    if n == 0:
                        break
                    elif n % 16 != 0:
                        data += ' ' * (16 - n % 16)  # <- padded with spaces
                    encoded = aes.encrypt(data)
                    out_file.write(encoded)

    def decrypt_sound_found(self, in_file_path, out_file_path):
        with open(in_file_path, 'rb') as in_file:
            file_size = struct.unpack('<Q', in_file.read(struct.calcsize('<Q')))[0]
            iv = in_file.read(16)
            aes = AES.new(self.key, AES.MODE_CBC, iv)
            with open(out_file_path, 'wb') as out_file:
                while True:
                    data = in_file.read(self.size_chunk)
                    n = len(data)
                    if n == 0:
                        break
                    decode = aes.decrypt(data)
                    n = len(decode)
                    if file_size > n:
                        out_file.write(decode)
                    else:
                        out_file.write(decode[:file_size])  # <- remove padding on last block
                    file_size -= n

    def decrypt_sound_found_in_memory(self, in_file_path):
        with open(in_file_path, 'rb') as in_file:
            file_size = struct.unpack('<Q', in_file.read(struct.calcsize('<Q')))[0]
            iv = in_file.read(16)
            aes = AES.new(self.key, AES.MODE_CBC, iv)
            temporal_name = 'temp/' + str(random.randrange(10*10)) + '.sf2'
            with open(temporal_name, 'wb') as out_file:
                while True:
                    data = in_file.read(self.size_chunk)
                    n = len(data)
                    if n == 0:
                        break
                    decode = aes.decrypt(data)
                    n = len(decode)
                    if file_size > n:
                        out_file.write(decode)
                    else:
                        out_file.write(decode[:file_size])  # <- remove padding on last block
                    file_size -= n

        return temporal_name
