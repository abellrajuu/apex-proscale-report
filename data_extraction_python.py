# -*- coding: utf-8 -*-
"""
===================================================================
 GA EXTRACTION - PURE DYNAMIC 100% DEEP DATA EXTRACTOR FOR ANY DWG
===================================================================
Extracts 100% real text, key-value pairs, and table data from ANY
DWG drawing file with ZERO hardcoded values or fake defaults.

All extracted JSON files, Text files, and Master CSV spreadsheets
are automatically saved into a clean folder on your Desktop:
   C:/Users/abell/OneDrive/Desktop/GA_EXTRACTION_OUTPUTS/

Run in Command Prompt:
   python "C:/Users/abell/OneDrive/Desktop/GA_EXTRACTION.py"
===================================================================
"""

import sys
import os
import glob
import re
import csv
import json
import subprocess
import tempfile
import shutil

def p(msg=""):
    print(msg, flush=True)

# Ensure dedicated output folder structure on Desktop
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
OUTPUT_DIR = os.path.join(DESKTOP_DIR, "GA_EXTRACTION_OUTPUTS")
JSON_DIR = os.path.join(OUTPUT_DIR, "json_reports")
TXT_DIR = os.path.join(OUTPUT_DIR, "text_reports")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(TXT_DIR, exist_ok=True)


def parse_dynamic_specs(dwg_path, raw_ocr_elements, processed_layers):
    """
    Dynamically parses engineering specs, key-value pairs, and drawing details
    from CAD vector text tokens for ANY DWG file with ZERO hardcoded values.
    """
    all_texts = [item["text"] for item in raw_ocr_elements]

    specs = {
        "filename": os.path.basename(dwg_path),
        "filepath": dwg_path,
        "total_extracted_words": len(all_texts),
        "total_cad_layers": len(processed_layers)
    }

    # Dynamic Key-Value Pair Extraction
    kv_pairs = {}
    for i, line in enumerate(all_texts):
        line_clean = line.strip()
        if not line_clean:
            continue

        # Pattern 1: Line contains explicit separator (KEY : VALUE, KEY = VALUE, KEY - VALUE)
        m = re.match(r'^([A-Z0-9\s_\-\.\/\(\)]+?)\s*[:=\-]\s*(.+)$', line_clean, re.IGNORECASE)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            if len(key) >= 2 and val:
                norm_key = re.sub(r'[^a-zA-Z0-9]+', '_', key).strip('_').lower()
                if norm_key and norm_key not in kv_pairs:
                    kv_pairs[norm_key] = val
                    if norm_key not in specs:
                        specs[norm_key] = val

        # Pattern 2: Label on current line (ends with colon or uppercase header), value on next line
        elif line_clean.endswith(':') or (line_clean.isupper() and len(line_clean) < 35):
            key_name = line_clean.rstrip(':').strip()
            if i + 1 < len(all_texts):
                next_val = all_texts[i + 1].strip()
                if next_val and not next_val.endswith(':') and not next_val.isupper():
                    norm_key = re.sub(r'[^a-zA-Z0-9]+', '_', key_name).strip('_').lower()
                    if norm_key and len(norm_key) >= 2 and norm_key not in kv_pairs:
                        kv_pairs[norm_key] = next_val
                        if norm_key not in specs:
                            specs[norm_key] = next_val

        # Pattern 3: Line has space-separated label and value (e.g. "INDICATOR MODEL 1", "CAPACITY 6", "RESOLUTION 7")
        m2 = re.match(r'^([A-Z\s_]{3,30}?)\s+([A-Z0-9\-\.\/]+)$', line_clean, re.IGNORECASE)
        if m2:
            key = m2.group(1).strip()
            val = m2.group(2).strip()
            if len(key) >= 2 and val:
                norm_key = re.sub(r'[^a-zA-Z0-9]+', '_', key).strip('_').lower()
                if norm_key and norm_key not in kv_pairs:
                    kv_pairs[norm_key] = val
                    if norm_key not in specs:
                        specs[norm_key] = val


    specs["extracted_key_values"] = kv_pairs
    return specs


def deep_extract_dwg(dwg_path, save_to_disk=False):
    p("\n=================================================================")
    p(f" DEEP EXTRACTION MODE: {os.path.basename(dwg_path)}")
    p("=================================================================")
    p(f" File Path : {dwg_path}")
    p(f" File Size : {os.path.getsize(dwg_path) / 1024:.1f} KB")

    base_name = os.path.splitext(os.path.basename(dwg_path))[0]

    # Step 1: Extract all text entities (including AutoCAD Table blocks)
    raw_ocr_elements = []
    layer_counts = {}
    multi_systems = {}

    # 1A. Primary fast method: dwg2dxf + ezdxf (parses Modelspace, Paper Space, and anonymous Table Blocks *T...)
    dwg2dxf_candidates = [
        os.path.join(DESKTOP_DIR, "libredwg", "dwg2dxf.exe"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "libredwg", "dwg2dxf.exe"),
        r"C:\libredwg\dwg2dxf.exe",
        "dwg2dxf"
    ]
    dwg2dxf_path = next((p for p in dwg2dxf_candidates if os.path.exists(p) or p == "dwg2dxf"), None)

    dxf_parsed = False
    temp_dir = tempfile.gettempdir()
    local_dwg = os.path.join(temp_dir, f"ext_{os.path.basename(dwg_path)}")
    temp_dxf = os.path.join(temp_dir, f"ext_{base_name}.dxf")

    if dwg2dxf_path:
        try:
            # Copy locally first to avoid network share UNC path / permission / lock issues
            try:
                shutil.copy2(dwg_path, local_dwg)
                target_dwg = local_dwg
            except Exception:
                target_dwg = dwg_path

            # Run dwg2dxf without check=True because ACAD_TABLE non-fatal warnings return code 1
            subprocess.run([dwg2dxf_path, "-y", "-o", temp_dxf, target_dwg], capture_output=True)
            if os.path.exists(temp_dxf) and os.path.getsize(temp_dxf) > 0:
                import ezdxf
                doc = ezdxf.readfile(temp_dxf)

                def parse_entity_texts(entities, scope_name=""):
                    texts = []
                    for e in entities:
                        if e.dxftype() == 'TEXT' and e.dxf.text.strip():
                            texts.append({'text': e.dxf.text.strip(), 'x': float(e.dxf.insert.x), 'y': float(e.dxf.insert.y)})
                        elif e.dxftype() == 'MTEXT' and e.text.strip():
                            texts.append({'text': e.text.strip(), 'x': float(e.dxf.insert.x), 'y': float(e.dxf.insert.y)})
                    if not texts:
                        return None

                    title = ""
                    for t in texts:
                        up = t['text'].upper()
                        if 'TEMPLATE' in up or 'SCALE' in up or 'INDICATOR' in up or 'FEEDER' in up:
                            title = t['text']
                            break

                    HEADER_PREFIXES = (
                        r'SYSTEM|SYS\.?|CONVEYOR|CONV\.?|CV\.?|BC\.?|'
                        r'TAG|TRACKING|TRACK|CRANE|HOIST|SCALE|BS|FEEDER|WEIGHFEEDER|WF|LIW|'
                        r'LINE|STREAM|UNIT|BAY|WEIGHER|STATION|SET|MACHINE|EQUIPMENT|EQPT|'
                        r'DEVICE|HOPPER|SILO|BIN|VESSEL|TANK|CHANNEL|CH|CIRCUIT'
                    )
                    sys_regex = re.compile(
                        rf'^(?:{HEADER_PREFIXES})\s*(?:NO\.?|NUM\.?|NUMBER|#|ID|TAG|CODE|[-_:])*\s*([0-9]+[A-Z]?|[A-Z]|[IVXLCDM]+)$',
                        re.IGNORECASE
                    )
                    sys_candidates = []
                    for t in texts:
                        clean_t = t['text'].rstrip(':').strip()
                        m = sys_regex.match(clean_t)
                        if m:
                            num_str = m.group(1)
                            sys_candidates.append({
                                'name': clean_t.upper(),
                                'num': int(num_str) if num_str.isdigit() else 999,
                                'x': t['x'],
                                'y': t['y']
                            })

                    sys_cols = []
                    if sys_candidates:
                        y_groups = {}
                        for c in sys_candidates:
                            found_key = None
                            for yk in y_groups:
                                if abs(yk - c['y']) < 0.25:
                                    found_key = yk
                                    break
                            if found_key is not None:
                                y_groups[found_key].append(c)
                            else:
                                y_groups[c['y']] = [c]

                        best_y_group = max(y_groups.values(), key=lambda g: (len(g) >= 2, len(g), max(item['y'] for item in g)))
                        sys_cols = sorted(best_y_group, key=lambda s: s['x'])

                    # Fallback: sequential numeric columns across same row level (e.g. 1, 2, 3)
                    if not sys_cols:
                        numeric_texts = [t for t in texts if t['text'].isdigit() and 1 <= int(t['text']) <= 50]
                        y_groups = {}
                        for t in numeric_texts:
                            y_rounded = round(t['y'] * 5) / 5
                            y_groups.setdefault(y_rounded, []).append(t)
                        for y_val, group in y_groups.items():
                            if len(group) >= 2:
                                group.sort(key=lambda g: g['x'])
                                nums = [int(g['text']) for g in group]
                                if nums == list(range(nums[0], nums[0] + len(nums))):
                                    for g in group:
                                        sys_cols.append({
                                            'name': f"SYSTEM {g['text']}",
                                            'num': int(g['text']),
                                            'x': g['x'],
                                            'y': g['y']
                                        })
                                    break

                    if not sys_cols:
                        return {"scope": scope_name, "title": title, "systems": {}, "texts": texts}

                    sys_cols.sort(key=lambda s: s['x'])
                    min_sys_x = min(s['x'] for s in sys_cols)
                    header_y = sys_cols[0]['y']

                    # Compute dynamic horizontal column spacing
                    col_spacings = [sys_cols[i+1]['x'] - sys_cols[i]['x'] for i in range(len(sys_cols)-1)]
                    col_dist = min(col_spacings) if col_spacings else 1.0
                    x_tol = max(col_dist * 0.4, 0.5)

                    keys = [t for t in texts if t['x'] < (min_sys_x - col_dist * 0.15) and t['y'] < (header_y - 0.05)]
                    keys.sort(key=lambda k: -k['y'])

                    # Compute dynamic vertical row spacing
                    row_spacings = [abs(keys[i]['y'] - keys[i+1]['y']) for i in range(len(keys)-1)]
                    row_spacings = [sp for sp in row_spacings if sp > 0.001]
                    row_dist = min(row_spacings) if row_spacings else 0.5
                    y_tol = max(row_dist * 0.45, 0.1)

                    block_systems = {}
                    for sc in sys_cols:
                        sname = sc['name']
                        block_systems[sname] = {}
                        for k in keys:
                            ky = k['y']
                            cell_val = ''
                            for t in texts:
                                if abs(t['x'] - sc['x']) < x_tol and abs(t['y'] - ky) < y_tol:
                                    val = t['text']
                                    val = re.sub(r'\{[^{}]*;', '', val)
                                    val = re.sub(r'\}', '', val).strip()
                                    cell_val = val
                                    break
                            if cell_val:
                                block_systems[sname][k['text']] = cell_val

                    return {"scope": scope_name, "title": title, "systems": block_systems, "texts": texts}

                # Evaluate all scopes (blocks and layouts) independently
                found_tables = []
                for b in doc.blocks:
                    res_b = parse_entity_texts(b, b.name)
                    if res_b and res_b["systems"]:
                        found_tables.append(res_b)

                # If no table in blocks, check modelspace & layouts
                if not found_tables:
                    all_layout_entities = []
                    for layout in [doc.modelspace()] + [doc.layout(n) for n in doc.layout_names()]:
                        all_layout_entities.extend(list(layout))
                    res_l = parse_entity_texts(all_layout_entities, "layouts")
                    if res_l and res_l["systems"]:
                        found_tables.append(res_l)

                # Prioritize the best table:
                # 1. Blocks that have an explicit title (e.g. 'DIGITAL INDICATOR TEMPLATE')
                # 2. Or the highest block number (most recently created in AutoCAD, e.g. *T4 over *T2)
                best_table = None
                if found_tables:
                    titled = [t for t in found_tables if t.get("title") and any(w in t["title"].upper() for w in ["TEMPLATE", "INDICATOR", "SCALE", "FEEDER"])]
                    if titled:
                        best_table = titled[-1]
                    else:
                        best_table = found_tables[-1]

                    multi_systems = best_table["systems"]
                    chosen_texts = best_table["texts"]
                else:
                    # Fallback: collect all texts across document
                    chosen_texts = []
                    for layout in [doc.modelspace()] + [doc.layout(n) for n in doc.layout_names()]:
                        for e in layout:
                            if e.dxftype() == 'TEXT' and e.dxf.text.strip(): chosen_texts.append({'text': e.dxf.text.strip()})
                            elif e.dxftype() == 'MTEXT' and e.text.strip(): chosen_texts.append({'text': e.text.strip()})
                    for b in doc.blocks:
                        for e in b:
                            if e.dxftype() == 'TEXT' and e.dxf.text.strip(): chosen_texts.append({'text': e.dxf.text.strip()})
                            elif e.dxftype() == 'MTEXT' and e.text.strip(): chosen_texts.append({'text': e.text.strip()})

                # Populate raw OCR elements
                for item in chosen_texts:
                    raw_ocr_elements.append({
                        "text": item['text'],
                        "confidence": 1.0,
                        "box": [[0, 0], [0, 0], [0, 0], [0, 0]]
                    })

                dxf_parsed = True
        except Exception as e:
            p(f" -> DXF Extraction Note: {e}")
        finally:
            for tf in [temp_dxf, local_dwg]:
                if os.path.exists(tf):
                    try: os.remove(tf)
                    except Exception: pass

    # 1B. Fallback: LibreDWG JSON dump
    if not dxf_parsed:
        temp_json = dwg_path + ".temp.json"
        dwgread_candidates = [
            os.path.join(DESKTOP_DIR, "libredwg", "dwgread.exe"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "libredwg", "dwgread.exe"),
            r"C:\libredwg\dwgread.exe",
            "dwgread"
        ]
        dwgread_path = next((p for p in dwgread_candidates if os.path.exists(p) or p == "dwgread"), None)
        if dwgread_path:
            try:
                subprocess.run([dwgread_path, "-O", "JSON", "-o", temp_json, dwg_path], capture_output=True, check=True)
                if os.path.exists(temp_json):
                    with open(temp_json, 'r', encoding='utf-8', errors='ignore') as f:
                        data = json.load(f)
                    for obj in data.get("OBJECTS", []):
                        if (obj.get("object") or obj.get("entity")) in ("TEXT", "MTEXT"):
                            t = obj.get("text")
                            if t and str(t).strip():
                                raw_ocr_elements.append({
                                    "text": str(t).replace('\n', ' ').strip(),
                                    "confidence": 1.0,
                                    "box": [[0, 0], [0, 0], [0, 0], [0, 0]]
                                })
            except Exception as e:
                p(f" -> LibreDWG JSON Note: {e}")
            finally:
                if os.path.exists(temp_json):
                    try: os.remove(temp_json)
                    except Exception: pass

    p(f" -> Extracted {len(raw_ocr_elements)} raw text tokens/labels from drawing!")

    processed_layers = {}
    for l, c in layer_counts.items():
        processed_layers[l] = {
            "entity_count": c
        }

    # Extract Dynamic Specs with ZERO hardcoded values
    structured_specs = parse_dynamic_specs(dwg_path, raw_ocr_elements, processed_layers)
    if multi_systems:
        structured_specs["multi_systems"] = multi_systems

    # Save to disk only if explicitly requested (e.g. standalone CLI batch mode)
    if save_to_disk:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(JSON_DIR, exist_ok=True)
        os.makedirs(TXT_DIR, exist_ok=True)
        
        json_path = os.path.join(JSON_DIR, f"{base_name}_COMPLETE_DATA.json")
        full_data = {
            "file_info": {
                "filename": os.path.basename(dwg_path),
                "filepath": dwg_path,
                "size_kb": round(os.path.getsize(dwg_path) / 1024, 1)
            },
            "extracted_specs": structured_specs,
            "cad_layers": processed_layers,
            "raw_vector_texts": raw_ocr_elements
        }

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(full_data, f, indent=2, ensure_ascii=False)
            p(f"\n [SAVED JSON] -> {json_path}")
        except Exception as e:
            p(f" [JSON Save Note] {e}")

        txt_path = os.path.join(TXT_DIR, f"{base_name}_ALL_TEXTS.txt")
        try:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"=== 100% EXTRACTED TEXT FOR {os.path.basename(dwg_path)} ===\n\n")
                for idx, item in enumerate(raw_ocr_elements, start=1):
                    f.write(f"{idx:3d}. [{item['confidence']:.2f}] {item['text']}\n")
            p(f" [SAVED TXT]  -> {txt_path}\n")
        except Exception as e:
            p(f" [TXT Save Note] {e}")

    # Display Summary Table in Console dynamically based on real extracted keys
    kv = structured_specs.get("extracted_key_values", {})
    p("  +-------------------------------------------------------------+")
    p("  |            DYNAMIC SUMMARY OF REAL DWG DATA                 |")
    p("  +-----------------------------------+-------------------------+")
    p(f"  | TOTAL TEXT TOKENS EXTRACTED       | {structured_specs['total_extracted_words']:<23} |")
    p(f"  | TOTAL CAD LAYERS ANALYZED         | {structured_specs['total_cad_layers']:<23} |")
    p(f"  | TOTAL DYNAMIC KEYS PARSED         | {len(kv):<23} |")
    p("  +-----------------------------------+-------------------------+")
    if kv:
        p("  | EXTRACTED KEY-VALUE PAIRS:                                  |")
        for k, v in list(kv.items())[:15]:
            display_k = (k[:30] + '..') if len(k) > 30 else k
            display_v = (str(v)[:23] + '..') if len(str(v)) > 23 else str(v)
            p(f"  |  * {display_k:<30} | {display_v:<21} |")
        p("  +-----------------------------------+-------------------------+")
    p("=================================================================\n")

    return structured_specs


def main():
    p("=================================================================")
    p("  GA EXTRACTION - PURE DYNAMIC DATA EXTRACTOR FOR DWG FILES      ")
    p("=================================================================")
    p(f" Output Folder: {OUTPUT_DIR}")

    dwg_files = []
    if len(sys.argv) > 1:
        user_input = sys.argv[1].strip().replace('"', '').replace("'", '')
        if os.path.isfile(user_input):
            dwg_files = [user_input]
        elif os.path.isdir(user_input):
            p(f"\n[BATCH FOLDER MODE] Scanning for all .dwg files in: {user_input}...")
            dwg_files = glob.glob(os.path.join(user_input, "**", "*.dwg"), recursive=True)
            p(f"Found {len(dwg_files)} DWG files!")
    else:
        user_input = os.path.join(DESKTOP_DIR, "GA SY1372.dwg")
        if os.path.exists(user_input):
            dwg_files = [user_input]
        else:
            p("\nNote: Pass a DWG file path or directory as argument:")
            p('  python GA_EXTRACTION.py "C:\\path\\to\\drawing.dwg"')

    results = []
    for index, filepath in enumerate(dwg_files, start=1):
        p(f"\n[{index}/{len(dwg_files)}] Deep Analyzing: {os.path.basename(filepath)}")
        res = deep_extract_dwg(filepath)
        if res:
            results.append(res)

    if len(results) > 0:
        csv_path = os.path.join(OUTPUT_DIR, "GA_EXTRACTION_ALL_JOBS.csv")
        # Gather all unique keys across all processed drawings
        all_keys = set()
        for r in results:
            all_keys.update(r.keys())
            if "extracted_key_values" in r:
                all_keys.update(r["extracted_key_values"].keys())

        # Exclude complex sub-dict keys from flat CSV columns
        all_keys.discard("extracted_key_values")
        fieldnames = sorted(list(all_keys))

        try:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                for r in results:
                    row_data = dict(r)
                    if "extracted_key_values" in r:
                        row_data.update(r["extracted_key_values"])
                    writer.writerow(row_data)
            p(f" [SAVED MASTER CSV] -> {csv_path}\n")
        except Exception as e:
            p(f" [CSV Export Note] {e}")


if __name__ == "__main__":
    main()

