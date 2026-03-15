import os
import re

# Scans the folder where this script is located.
# If you want a different folder, replace "." with a full path string.
FOLDER = "."

def pad2(n: str) -> str:
    return f"{int(n):02d}"

def normalize_test(raw: str) -> str:
    """Convert 'Reassessment' -> 'Reassess', keep 'Placement' as 'Placement'."""
    return "Reassess" if "reassess" in raw.lower() else "Placement"

for filename in os.listdir(FOLDER):
    # Skip files already renamed
    if filename.startswith(("L_", "T_")):
        continue

    lower = filename.lower()

    # -------------------
    # LOG FILES (.xlsx)
    # -------------------
    # Examples:
    # 3-4-26_ISAZ_AZELLA_STL-GR4-12-SPR26-Reassessment.xlsx
    # 3-5-26_AZELLA_STL-GR2-3-SPR25-Reassessment.xlsx  (no school -> default AZVA)
    log_match = re.search(
        r"(?P<m>\d{1,2})-(?P<d>\d{1,2})-(?P<y>\d{2}).*?"
        r"(?P<school>azva|isaz)?"
        r".*?gr(?P<grade>\d{1,2}(?:-\d{1,2})?).*?"
        r"(?P<test>reassessment|placement)",
        lower,
    )

    if log_match and lower.endswith(".xlsx"):
        m = pad2(log_match.group("m"))
        d = pad2(log_match.group("d"))
        y = log_match.group("y")
        grade = log_match.group("grade")
        test = normalize_test(log_match.group("test"))

        # Default school to AZVA if not found
        school = (log_match.group("school") or "azva").upper()

        new_name = f"L_{m}-{d}-{y}_{school}_G{grade}_{test}.xlsx"

        # If a file with the new name already exists, add _2, _3, etc.
        base, ext = os.path.splitext(new_name)
        counter = 2
        while os.path.exists(os.path.join(FOLDER, new_name)):
            new_name = f"{base}_{counter}{ext}"
            counter += 1

        print(f"{filename} -> {new_name}")
        os.rename(os.path.join(FOLDER, filename), os.path.join(FOLDER, new_name))
        continue

    # -------------------
    # TEMPLATE FILES (.xltx)
    # -------------------
    # Templates are school-neutral since both schools use the same template.
    if lower.endswith(".xltx"):
        # KPT template
        if "kpt" in lower:
            new_name = "T_KPT_TEMPLATE.xltx"
            if filename != new_name:
                print(f"{filename} -> {new_name}")
                os.rename(os.path.join(FOLDER, filename), os.path.join(FOLDER, new_name))
            continue

        # Detect grade band + test type
        # Handles: GR1, GR2-3, GR4-12, GRK-1
        tm = re.search(
            r"gr(?P<grade>(?:k-1)|\d{1,2}(?:-\d{1,2})?).*?(?P<test>reassessment|placement)",
            lower,
        )

        if tm:
            grade = tm.group("grade").upper()  # "K-1" or "4-12" etc.
            test = normalize_test(tm.group("test"))

            new_name = f"T_G{grade}_{test}_TEMPLATE.xltx"

            # Handle duplicates safely
            base, ext = os.path.splitext(new_name)
            counter = 2
            while os.path.exists(os.path.join(FOLDER, new_name)):
                new_name = f"{base}_{counter}{ext}"
                counter += 1

            print(f"{filename} -> {new_name}")
            os.rename(os.path.join(FOLDER, filename), os.path.join(FOLDER, new_name))
            continue
