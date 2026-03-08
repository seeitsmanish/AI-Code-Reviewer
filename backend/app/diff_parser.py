from typing import List


def parse_patch(patch: str):
    lines: List[str] = patch.splitlines()
    current_line = 0
    parsed_patch = []

    for line in lines:
        if line.startswith('@@'):
            parsed_patch.append({
                "type": "hunk_header",
                "content": line,
                "line_number": None
            })
            current_line = int(line.split('+')[1].split(',')[0])

        elif line.startswith(' '):
            parsed_patch.append({
                "type": "context",
                "content": line[1:],
                "line_number": current_line,
            })
            current_line += 1

        elif line.startswith('+') and not line.startswith('+++'):
            parsed_patch.append({
                "type": "added",
                "content": line[1:],
                "line_number": current_line
            })
            current_line += 1

        elif line.startswith('-') and not line.startswith('---'):
            parsed_patch.append({
                "type": "removed",
                "content": line[1:],
                "line_number": None
            })

    return parsed_patch
