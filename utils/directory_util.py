def normalize_directory_name(directory: str) -> str:
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

    # 문자열 처리
    result = directory.strip().lower()  # 공백 제거 및 소문자 변환

    # 금지 문자 제거
    for char in invalid_chars:
        result = result.replace(char, '')

    return result