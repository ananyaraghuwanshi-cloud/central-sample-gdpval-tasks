import sys, json, re

TYPE_VALUES = {"Critical", "Nice-to-have", "Nice To Have", "Subjective", "Style / Formatting"}
GRADING_TARGET_RE = re.compile(
    r'^(?=.*\()(Word Documents.*|Spreadsheets.*|Presentations.*|Text [Dd]ocuments?.*|All output.*|PDFs?( [Dd]ocuments?)?.*|Audio/Video.*|Images?.*|Python Files.*|Code Files.*)$'
)
STRUCTURED_SCHEMAS = {
    "Content length": ["contentSource", "targetFile", "metric", "comparison", "expectedValue", "tolerance", "aggregationMode"],
    "Page count": ["filePattern", "fileName", "minimumCount", "maximumCount", "countMode"],
}
BLOCK_MARKERS = {"Balboa Rubric"} | set(STRUCTURED_SCHEMAS)

def load_text(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return data[0]['text']

def extract_rubric_block(text):
    start_marker = "Task Rubric\n"
    start = text.find(start_marker)
    if start == -1:
        raise Exception("Task Rubric marker not found")
    end = text.find("Add rubric item", start)
    if end == -1:
        end = len(text)
    return text[start:end]

def parse_rows(block):
    lines = block.split("\n")
    row_starts = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        if re.fullmatch(r'\d+', line):
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            if j < n and lines[j].strip() in BLOCK_MARKERS:
                row_starts.append((int(line), i))
        i += 1
    rows = []
    for idx, (row_num, start_i) in enumerate(row_starts):
        end_i = row_starts[idx + 1][1] if idx + 1 < len(row_starts) else n
        rows.append((row_num, lines[start_i:end_i]))
    return rows

def parse_structured_row(row_num, row_lines, marker, i, n):
    vals = [row_lines[k].strip() for k in range(i, n) if row_lines[k].strip() != ""]
    skip_idx = 0
    while skip_idx < len(vals) and vals[skip_idx] == "—":
        skip_idx += 1

    is_between = (
        marker == "Content length"
        and skip_idx + 3 < len(vals)
        and "between" in vals[skip_idx + 3].lower()
    )
    if is_between:
        field_names = ["contentSource", "targetFile", "metric", "comparison",
                        "minimumValue", "maximumValue", "unusedTolerance", "aggregationMode"]
    else:
        field_names = STRUCTURED_SCHEMAS[marker]
    nfields = len(field_names)
    fields = dict(zip(field_names, vals[skip_idx:skip_idx + nfields]))
    rest = vals[skip_idx + nfields:]
    last_dash_idx = -1
    for k, val in enumerate(rest):
        if val == "—":
            last_dash_idx = k
    weight_idx = last_dash_idx + 1
    weight = rest[weight_idx] if weight_idx < len(rest) else "—"

    if marker == "Content length" and is_between:
        description = (
            f'Programmatic content length check: {fields.get("metric", "")} of '
            f'"{fields.get("targetFile", "")}" is between {fields.get("minimumValue", "")} and '
            f'{fields.get("maximumValue", "")} (inclusive) '
            f'(aggregation: {fields.get("aggregationMode", "")}).'
        )
    elif marker == "Content length":
        description = (
            f'Programmatic content length check: {fields.get("metric", "")} of '
            f'"{fields.get("targetFile", "")}" is {fields.get("comparison", "").lower()} '
            f'{fields.get("expectedValue", "")} (tolerance ±{fields.get("tolerance", "0")}, '
            f'aggregation: {fields.get("aggregationMode", "")}).'
        )
    elif marker == "Page count":
        description = (
            f'Programmatic page count check: "{fields.get("fileName", "")}" '
            f'(pattern {fields.get("filePattern", "")}) must have between '
            f'{fields.get("minimumCount", "")} and {fields.get("maximumCount", "")} pages '
            f'({fields.get("countMode", "")}).'
        )
    else:
        description = f'Programmatic {marker.lower()} check: {fields}.'

    return {
        "num": row_num,
        "description": description,
        "rationale": "",
        "type": "Programmatic",
        "tags": [],
        "gradingTarget": "",
        "weight": weight,
    }

def parse_row(row_num, row_lines):
    i = 0
    n = len(row_lines)
    while row_lines[i].strip() != str(row_num):
        i += 1
    i += 1
    while row_lines[i].strip() == "":
        i += 1
    marker = row_lines[i].strip()
    assert marker in BLOCK_MARKERS, row_lines[i]
    i += 1
    while i < n and row_lines[i].strip() == "":
        i += 1
    if i < n and row_lines[i].strip() in {"LLM judge", "Programmatic"}:
        i += 1
    while i < n and row_lines[i].strip() == "":
        i += 1

    if marker != "Balboa Rubric":
        return parse_structured_row(row_num, row_lines, marker, i, n)

    SEP_RE = re.compile(r'^\t+$')
    uses_tab_separators = any(SEP_RE.fullmatch(l) for l in row_lines)

    desc_lines = []
    if uses_tab_separators:
        while i < n and not SEP_RE.fullmatch(row_lines[i]):
            desc_lines.append(row_lines[i])
            i += 1
        while desc_lines and desc_lines[-1].strip() == "":
            desc_lines.pop()
        if i < n:
            i += 1
        while i < n and row_lines[i] == "":
            i += 1
    else:
        while i < n and row_lines[i].strip() != "":
            desc_lines.append(row_lines[i])
            i += 1
        while i < n and row_lines[i].strip() == "":
            i += 1

    type_idx = None
    for k in range(i, n):
        if row_lines[k].strip() in TYPE_VALUES:
            type_idx = k
            break
    if type_idx is None:
        raise Exception(f"Row {row_num}: TYPE anchor not found")

    rationale_lines = row_lines[i:type_idx]
    while rationale_lines and rationale_lines[-1].strip() == "":
        rationale_lines.pop()

    row_type = row_lines[type_idx].strip()
    if row_type == "Nice To Have":
        row_type = "Nice-to-have"
    j = type_idx + 1
    while j < n and row_lines[j].strip() == "":
        j += 1

    tags = []
    while j < n and row_lines[j].strip() != "" and not GRADING_TARGET_RE.match(row_lines[j].strip()):
        tags.extend(t.strip() for t in row_lines[j].strip().split(", "))
        j += 1
    while j < n and row_lines[j].strip() == "":
        j += 1

    remaining = [row_lines[k].strip() for k in range(j, n) if row_lines[k].strip() != ""]

    grading_idx = None
    for k, val in enumerate(remaining):
        if GRADING_TARGET_RE.match(val):
            grading_idx = k
            break

    if grading_idx is None:
        grading_target = ""
        rest = remaining
    else:
        grading_target = remaining[grading_idx]
        rest = remaining[grading_idx + 1:]
    weight = None
    if rest:
        last_dash_idx = -1
        for k, val in enumerate(rest):
            if val == "—":
                last_dash_idx = k
        weight_idx = last_dash_idx + 1
        if weight_idx < len(rest):
            weight = rest[weight_idx]

    explicit_weight_match = re.search(r'Weight\s*\((-?[\d.]+)\)', "\n".join(rest))
    if explicit_weight_match:
        weight = explicit_weight_match.group(1)

    return {
        "num": row_num,
        "description": "\n".join(desc_lines).strip(),
        "rationale": "\n".join(rationale_lines).strip(),
        "type": row_type,
        "tags": tags,
        "gradingTarget": grading_target,
        "weight": weight,
    }

if __name__ == '__main__':
    text = load_text(sys.argv[1])
    block = extract_rubric_block(text)
    rows = parse_rows(block)
    parsed = [parse_row(num, lines) for num, lines in rows]
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
