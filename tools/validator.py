
import os
import re
import glob
import logging
import shutil
from typing import Any, TypedDict

from packer import EastwardPacker

class InvalidLine(TypedDict):
    reason: str
    line: int

class InvalidFileExeception(Exception):
    def __init__(self, invalid_lines: list[InvalidLine]):
        super().__init__("Invalid lines found")
        self.invalid_lines = invalid_lines


def load_key_and_values(file_path: str) -> dict[str, Any]:
    invalid_lines: list[InvalidLine] = []
    
    with open(file_path) as f:
        content = f.readlines()
        groups = {}

        group_name = None

        for i in range(0, len(content)):
            line = content[i]
            clean_line = line.strip()

            if line.startswith("return {") or clean_line in ("}", "};"):
                continue
            
            if line.strip() == "":
                invalid_lines.append({"reason": "Empty line", "line": i+1})
            
            match_group = re.match(r"\[\"([\S\.\s\(\))]+)\"\]={", clean_line)
            if match_group:
                group_name = match_group.group(1)
                continue
            
            group = groups.setdefault(group_name, {})
            
            if group is None:
                invalid_lines.append({"reason": "Group not found - pattern issue", "line": i+1})
            
            match_line = re.match(r"\[\"([\S\s]+)\"\]\s+=\s+\"(.*)\";", clean_line)

            if match_line:
                key = match_line.group(1)
                value = match_line.group(2)

                group[key] = {"text": value, "line": i+1}
            elif not clean_line.endswith(";"):
                invalid_lines.append({"reason": f"Missing semicolon: {line}", "line": i+1})
            else:
                invalid_lines.append({"reason": f"Pattern not matched: {line}", "line": i+1})

        if invalid_lines:
            raise InvalidFileExeception(invalid_lines)
        
        return groups

def detect_tags(line: str) -> list[str]:
    tag_content = ""
    is_open = False
    tags = []
    for c in line:
        if c == "{":
            is_open = True
        
        if is_open:
            tag_content += c

        if c == "}":
            is_open = False
            tags.append(tag_content)
            tag_content = ""

    return tags

def get_all_tags(root_path: str) -> set[str]:
    all_tags = set()

    for name in glob.iglob(f"**/*en", root_dir=root_path, recursive=True):
        file_path = os.path.abspath(os.path.join(root_path, name))
        r = load_key_and_values(file_path)

        for items in r.values():
            for value in items.values():
                c_tags = detect_tags(value["text"])
                for tag in c_tags:
                    all_tags.add(tag)

    return all_tags

def check_keys(original_file_content: dict[str, Any], raw_file_content: dict[str, Any]):
    original_keyset = set()
    invalid_lines: list[InvalidLine] = []
    
    for group, data in original_file_content.items():
        for key in data:
            original_keyset.add(f"{group}_{key}")

    for group, data in raw_file_content.items():
        for key, value in data.items():
            index = f"{group}_{key}"
            if index not in original_keyset:
                invalid_lines.append({"reason": f"The key {index} does not exist", "line": value["line"]})
                
    
    if invalid_lines:
        raise InvalidFileExeception(invalid_lines)

def check_tags(raw_file: dict[str, Any], allowed_tags: set[str]):
    invalid_lines: list[InvalidLine] = []

    for items in raw_file.values():
        for value in items.values():
            c_tags = detect_tags(value["text"])
            for tag in c_tags:
                if tag not in allowed_tags:
                    line = value["line"]
                    reason = f"Invalid tag {{{tag}}}"
                    invalid_lines.append({"reason": reason, "line": line})

    if invalid_lines:

        raise InvalidFileExeception(invalid_lines)

def check_errors(original_file_path: str, raw_files_path: str) -> list[InvalidLine]:
    language_name = "en"
    packer = EastwardPacker()
    temp_dir = "./temp"

    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        logging.info("Unpacking original file")
        packer.unpack_file(original_file_path, temp_dir)
        
        errors: dict[str, list[InvalidLine]] = {}
        logging.info(f"Retrieving all origninal tags for {language_name}")
        allowed_tags = get_all_tags(temp_dir)
        
        logging.info("Checking raw files")

        for file_path in glob.iglob(f"**/{language_name}", root_dir=raw_files_path, recursive=True):
            file_path = os.path.join(raw_files_path, file_path)
            original_file_path = os.path.join(temp_dir, file_path.replace(f"{raw_files_path}/", ""))
            
            logging.info(f"Checking file {file_path}")

            original_file = load_key_and_values(original_file_path)

            try:
                raw_file = load_key_and_values(file_path)
            except InvalidFileExeception as e:
                errors.setdefault(file_path, []).extend(e.invalid_lines)

            try:
                check_keys(original_file, raw_file)
            except InvalidFileExeception as e:
                errors.setdefault(file_path, []).extend(e.invalid_lines)

            try:
                check_tags(raw_file, allowed_tags)
            except InvalidFileExeception as e:
                errors.setdefault(file_path, []).extend(e.invalid_lines)

        return errors
    finally:
        shutil.rmtree(temp_dir)
        
if __name__ == "__main__":
    check_errors("./tools/files/original.g", "./raw")

