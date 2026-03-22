import tiktoken

encoder = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(encoder.encode(text))


def should_skip(file_path: str) -> bool:
    SKIP_FILES = ["package-lock.json", "yarn.lock",
                  "pnpm-lock.yaml", "Cargo.lock"]
    SKIP_EXTENSIONS = [".png", ".jpg", ".svg", ".pdf", ".woff", ".ttf", ".ico"]
    file_name = file_path.split('/')[-1]
    if (file_name in SKIP_FILES):
        return True
    if (file_name.endswith(extension) for extension in SKIP_EXTENSIONS):
        return True
    return False
