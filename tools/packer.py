from glob import glob
import os
import struct
from typing import Optional
import zstandard as zstd

class EastwardPacker():
    def __init__(self):
        ...

    def unpack_all(self, source: str, target_path: str, extension: str = ".g"):
         for file in glob(source + f'/*{extension}'):
            name = os.path.basename(file).replace(".", "_")
            self.unpack_file(file, os.path.join(target_path, name))

    def pack_all(self, source: str , target: str):
        
        for directory in glob(f"{source}/*"):
            dir_name = os.path.basename(directory)
            target_path = os.path.join(target, dir_name.replace("_", "."))
            self.pack_file(target_path, directory)

        

    def unpack_file(self, file_path: str, target_path: str):
        files = []

        with open(file_path, "rb") as file:
            # Read and ignore the dummy value
            file.read(4)

            # Read the number of files
            files_count = struct.unpack("<I", file.read(4))[0]

            for _ in range(files_count):
                # Read the file name
                name = ""
                while True:
                    char = file.read(1).decode("ascii", "ignore")
                    if char == "\0":
                        break
                    name += char

                # Read other metadata
                offset = struct.unpack("<I", file.read(4))[0]
                zip_flag = struct.unpack("<I", file.read(4))[0]
                size = struct.unpack("<I", file.read(4))[0]
                zsize = struct.unpack("<I", file.read(4))[0]

                if zip_flag != 2:
                    print(f"Error: unsupported ZIP {zip_flag}, contact me")
                    break

                files.append((name, offset, zip_flag, size, zsize))

            for filedata in files:
                name, offset, zip_flag, size, zsize = filedata
                # Extract the file
                file.seek(offset)
                compressed_data = file.read(zsize)
                decompressor = zstd.ZstdDecompressor()
                decompressed_data = decompressor.decompress(compressed_data, size)

                target_file_path = os.path.join(target_path, name)
                try:
                    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                except:
                    continue
                # Save the decompressed data

                with open(target_file_path, "wb") as output_file:
                    output_file.write(decompressed_data)

    def pack_file(self, file_path: str, source_path: Optional[str] = None):
        files = []

        for root, dirs, filenames in os.walk(source_path):
            for filename in filenames:
                file_full_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_full_path, source_path)
                file_size = os.path.getsize(file_full_path)

                files.append((relative_path, file_size, 2))

        with open(file_path, "wb") as file:
            # Write the dummy value (assuming it's the same as in the original file)
            file.write(struct.pack("<I", 0x6A37))

            # Write the number of files
            file.write(struct.pack("<I", len(files)))
            init_offset = file.tell()

            header_information_size = sum(
                [
                    1,  # Nullbyte
                    4,  # Offset 4bytes
                    4,  # Zip Flag 4bytes
                    4,  # Size 4bytes
                    4,  # ZSize 4bytes
                ]
            )

            names_size = sum(
                [
                    len(filename.encode("ascii"))
                    for filename, original_size, zip_flag in files
                ]
            )

            header_size = (header_information_size * len(files)) + names_size
            init_offset += header_size

            current_offset = 0

            for filename, original_size, zip_flag in files:
                # Compress the file
                with open(os.path.join(source_path, filename), "rb") as f:
                    file_data = f.read()
                    compressor = zstd.ZstdCompressor()
                    compressed_data = compressor.compress(file_data)
                    compressed_size = len(compressed_data)

                # Write metadata
                file.write(filename.encode("ascii") + b"\0")
                file.write(struct.pack("<I", init_offset + current_offset))
                file.write(struct.pack("<I", zip_flag))
                file.write(struct.pack("<I", original_size))
                file.write(struct.pack("<I", compressed_size))

                current_offset += compressed_size

            # Write the file data
            file.seek(init_offset)
            for filename, original_size, zip_flag in files:
                if zip_flag == 2:
                    with open(os.path.join(source_path, filename), "rb") as f:
                        file_data = f.read()
                        compressor = zstd.ZstdCompressor()
                        compressed_data = compressor.compress(file_data)
                        file.write(compressed_data)

