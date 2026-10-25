"""Check that info_de.yaml is in sync with info.yaml.

Run after editing info.yaml:  python check_translations.py

Reports entries missing from either file, links/photos/dates/numbers that
differ, and English text that changed since info_de.yaml was last committed.
Nothing is modified.
"""
import re
import subprocess
import sys
import yaml

EN_FILE = "static/data/info.yaml"
DE_FILE = "static/data/info_de.yaml"

# Fields that must be identical in both languages
SAME_VALUE_FIELDS = {"filename", "link", "companylink", "details_link", "email", "phone", "linkedin"}
# Fields whose numbers must match, while the wording may differ ("present" / "heute")
SAME_NUMBER_FIELDS = {"duration", "dates", "date", "final_grade", "proficiency"}
# Fields used to name list entries in the report
LABEL_FIELDS = ["title", "job_title", "role", "degree", "name"]


def read_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def git_show_yaml(rev, path):
    result = subprocess.run(["git", "show", f"{rev}:{path}"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        return None
    return yaml.safe_load(result.stdout.decode("utf-8")) or {}


def last_commit_of(path):
    result = subprocess.run(["git", "log", "-1", "--format=%H", "--", path], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return result.stdout.decode().strip() or None


def numbers(value):
    return re.findall(r"\d+", str(value))


def item_path(path, index, item):
    label = ""
    if isinstance(item, dict):
        for field in LABEL_FIELDS:
            if item.get(field):
                label = f' ("{item[field]}")'
                break
    return f"{path}[{index + 1}]{label}"


def compare_structure(en, de, path, problems):
    if isinstance(en, dict) and isinstance(de, dict):
        for key in en:
            key_path = f"{path}.{key}" if path else key
            if key not in de:
                problems.append(f"{key_path}: missing in German file")
            elif path == "ui":
                # Interface labels are all translated text, so only check that they exist
                continue
            elif key in SAME_VALUE_FIELDS and en[key] != de[key]:
                problems.append(f"{key_path}: differs (EN: {en[key]} | DE: {de[key]})")
            elif key in SAME_NUMBER_FIELDS and numbers(en[key]) != numbers(de[key]):
                problems.append(f"{key_path}: numbers differ (EN: {en[key]} | DE: {de[key]})")
            elif key not in SAME_VALUE_FIELDS | SAME_NUMBER_FIELDS:
                compare_structure(en[key], de[key], key_path, problems)
        for key in de:
            if key not in en:
                problems.append(f"{path}.{key}: only in German file" if path else f"{key}: only in German file")
    elif isinstance(en, list) and isinstance(de, list):
        if len(en) != len(de):
            problems.append(f"{path}: {len(en)} entries in English, {len(de)} in German")
        for i, (en_item, de_item) in enumerate(zip(en, de)):
            compare_structure(en_item, de_item, item_path(path, i, en_item), problems)
    elif isinstance(en, (dict, list)) != isinstance(de, (dict, list)):
        problems.append(f"{path}: different structure in the two files")


def find_changed_text(old_en, en, old_de, de, path, changed):
    # English text that changed since the baseline while the German text stayed the same
    if isinstance(en, dict):
        for key in en:
            if key in SAME_VALUE_FIELDS | SAME_NUMBER_FIELDS:
                continue
            key_path = f"{path}.{key}" if path else key
            find_changed_text(
                old_en.get(key) if isinstance(old_en, dict) else None, en[key],
                old_de.get(key) if isinstance(old_de, dict) else None,
                de.get(key) if isinstance(de, dict) else None,
                key_path, changed)
    elif isinstance(en, list):
        for i, en_item in enumerate(en):
            def at(seq):
                return seq[i] if isinstance(seq, list) and i < len(seq) else None
            find_changed_text(at(old_en), en_item, at(old_de), at(de), item_path(path, i, en_item), changed)
    elif isinstance(en, str) and old_en is not None and de is not None:
        if en != old_en and de == old_de:
            changed.append(path)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    en = read_yaml(EN_FILE)
    de = read_yaml(DE_FILE)

    problems = []
    compare_structure(en, de, "", problems)

    changed = []
    baseline = last_commit_of(DE_FILE)
    if baseline:
        old_en = git_show_yaml(baseline, EN_FILE)
        old_de = git_show_yaml(baseline, DE_FILE)
        if old_en is not None and old_de is not None:
            find_changed_text(old_en, en, old_de, de, "", changed)
    else:
        print(f"Note: {DE_FILE} has not been committed yet, so changed English text can't be detected until it is.\n")

    if problems:
        print("Out of sync:")
        for problem in problems:
            print(f"  - {problem}")
        print()
    if changed:
        print(f"English text changed since {DE_FILE} was last committed (update the German):")
        for path in changed:
            print(f"  - {path}")
        print()

    if problems or changed:
        sys.exit(1)
    print("info.yaml and info_de.yaml are in sync.")


if __name__ == "__main__":
    main()
