import argparse
import os
import sys
from packer import EastwardPacker
from validator import check_errors  # Você pode ajustar isso conforme a função real

def main():
    parser = argparse.ArgumentParser(description="Ferramentas de tradução Eastward.")
    
    parser.add_argument('--unpack', nargs=2, metavar=('ORIGINAL_FILE', 'DEST_FOLDER'),
                        help='Desempacota um arquivo .g original para edição.')
    
    parser.add_argument('--pack', nargs=2, metavar=('OUTPUT_FILE', 'SOURCE_FOLDER'),
                        help='Empacota os arquivos traduzidos em um .g final para o jogo.')
    
    parser.add_argument('--validate', nargs=2, metavar=('ORIGINAL_FILE', 'RAW_FOLDER'),
                        help='Valida se as traduções batem com os arquivos originais.')

    args = parser.parse_args()
    packer = EastwardPacker()

    if args.unpack:
        original_file, dest_folder = args.unpack
        print(f"[+] Unpacking: {original_file} -> {dest_folder}")
        packer.unpack_file(original_file, dest_folder)

    if args.pack:
        output_file, source_folder = args.pack
        print(f"[+] Packing: {source_folder} -> {output_file}")
        packer.pack_file(output_file, source_folder)

    if args.validate:
        original_file, raw_folder = args.validate
        print(f"[+] Validating: {raw_folder} based on {original_file} ")
        errors = check_errors(original_file, raw_folder)

        if not errors:
            print("[+] No issues found")
            sys.exit(0)
        
        for file in errors:
            invalid_lines = errors[file]
            
            for issue in invalid_lines:
                line = issue['line']
                reason = issue["reason"]
                print(f"File: {file}:{line}" )
                print(f"Reason: \n\t- {reason}")
                print("####")

        sys.exit(1)


    if not any([args.unpack, args.pack, args.validate]):
        parser.print_help()

if __name__ == "__main__":
    main()