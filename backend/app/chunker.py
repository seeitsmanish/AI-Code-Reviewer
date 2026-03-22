import json
from app.utils import count_tokens
from app.constants import MAX_TOKEN_LIMIT_PER_CHUNK


def merge_file_with_diffs(
        file_content: list[dict],
        parsed_diff: list[dict],
):
    diff_map = {}

    for line in parsed_diff:
        line_number = line.get("line_number")
        type = line.get("type")
        content = line.get("content")
        if (type == "added" and line_number):
            diff_map.update({line_number: type})
    file_with_diffs = []
    for line in file_content:
        line_number = line.get("line_number")
        line_type = diff_map.get(line_number, "context")
        content = line.get("content")
        file_with_diffs.append({
            "content": content,
            "line_number": line_number,
            "line_type": line_type
        })

    return file_with_diffs


def truncate_to_limit(filename: str, added_lines: list[dict], chunk_index: int) -> dict:
    current_tokens = 0
    truncated_lines = []

    for line in added_lines:
        line_tokens = count_tokens(json.dumps(line))

        if (line_tokens + current_tokens > MAX_TOKEN_LIMIT_PER_CHUNK):
            truncated_lines.append({
                "line_number": None,
                "type": "truncated",
                "content": "[... truncated, content exceeded token limit ...]"
            })
            break
        else:
            truncated_lines.append(line)
            current_tokens += line_tokens

    return {
        "chunk_index": chunk_index,
        "lines": truncated_lines,
        "filename": filename,
    }


def split_by_added_lines(filename: str, hunk_item: list[dict], chunk_index: int) -> dict:

    added_lines = []
    for line in hunk_item:
        if (line.get("type") == "added"):
            added_lines.append(line)
    added_text = json.dumps(added_lines)
    if (count_tokens(added_text) <= MAX_TOKEN_LIMIT_PER_CHUNK):
        return {
            "chunk_index": chunk_index,
            "lines": added_text,
            "filename": filename,
        }
    else:
        return truncate_to_limit(filename, added_lines, chunk_index)


def split_by_hunks(filename: str, parsed_diffs: list[dict]) -> list[dict]:
    chunks = []
    current_chunk = []
    chunk_index = 0
    for line in parsed_diffs:
        if (line.get(type) == "hunk_header"):
            if (len(current_chunk) > 0):
                hunk_text = json.dumps(current_chunk)
                if (count_tokens(hunk_text) <= MAX_TOKEN_LIMIT_PER_CHUNK):
                    chunks.append({
                        "filename": filename,
                        "lines": hunk_text,
                        "chunk_index": chunk_index
                    })
                else:
                    chunks.append(split_by_added_lines(
                        filename, current_chunk, chunk_index))
            chunk_index += 1
            current_chunk = []
        else:
            current_chunk.append(line)

    if (len(current_chunk) > 0):
        hunk_text = json.dumps(current_chunk)
        if (count_tokens(hunk_text) <= MAX_TOKEN_LIMIT_PER_CHUNK):
            chunks.append({
                "filename": filename,
                "lines": hunk_text,
                "chunk_index": chunk_index
            })
        else:
            chunks.append(split_by_added_lines(
                filename, current_chunk, chunk_index))
            chunk_index += 1
            current_chunk = []

    return chunks


def build_chunks(filename: str, file_with_diffs: list[dict], parsed_diffs: list[dict]) -> list[dict]:
    print(json.dumps({
        "filename": filename,
        "file_with_diffs": len(file_with_diffs),
        "parsed_diffs": len(parsed_diffs)
    }, indent=2))
    full_file = merge_file_with_diffs(file_with_diffs, parsed_diffs)
    file_text = json.dumps(full_file)
    if (count_tokens(file_text) < MAX_TOKEN_LIMIT_PER_CHUNK):
        return [
            {
                "filename": filename,
                "lines": file_text,
                "chunk_index": 0,
            }
        ]

    return split_by_hunks(filename, parsed_diffs)
