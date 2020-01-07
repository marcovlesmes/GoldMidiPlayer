import random, os, struct, tempfile
from Crypto.Cipher import AES


class SoundCoder:
    def __init__(self):
        self.key = '614E645267556B58'
        self.size_chunk = 16

    def encrypt_sound_found(self, in_file_path):
        iv = ''.join([chr(random.randint(0, 0xFF)) for i in range(16)])
        aes = AES.new(self.key, AES.MODE_CBC, iv)
        file_size = os.stat(in_file_path)[6]
        file_path = in_file_path.split('.')[0]
        temporal_file_path = 'temp.sfc'
        compress_file_path = file_path + '.csf'

        with open(in_file_path, 'rb') as in_file:
            with open(temporal_file_path, 'wb') as out_file:

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

        import zipfile

        compress_file = zipfile.ZipFile(compress_file_path, 'w')
        compress_file.write(temporal_file_path, compress_type=zipfile.ZIP_DEFLATED)
        compress_file.close()

        if os.path.exists(temporal_file_path):
            os.remove(temporal_file_path)

        return True

    def decrypt_sound_found_in_memory(self, in_file_path):
        import zipfile

        zipfile = zipfile.ZipFile(in_file_path)
        temporal_folder_path = 'C:\\temp'
        temporal_file_path = 'C:\\temp\\temp.sfc'

        zipfile.extractall(temporal_folder_path)
        zipfile.close()

        if os.path.exists(temporal_file_path):
            with open(temporal_file_path, 'rb') as in_file:
                file_size = struct.unpack('<Q', in_file.read(struct.calcsize('<Q')))[0]
                iv = in_file.read(16)
                aes = AES.new(self.key, AES.MODE_CBC, iv)
                out_file = tempfile.NamedTemporaryFile(delete=False)

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

            return out_file.name
        else:
            print('Error: File ' + temporal_file_path + ' dont was found.')
            return False
