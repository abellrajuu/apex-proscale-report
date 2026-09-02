def replace_in_paragraph(p, field_map):
    for key, val in field_map.items():
        placeholder = f"{{{{{key}}}}}"
        
        # We need to replace placeholder while preserving runs (formatting & tabs)
        # 1. Gather all runs
        runs = p.runs
        if not runs:
            continue
            
        # 2. Extract full text and check if placeholder exists
        full_text = "".join(r.text for r in runs)
        if placeholder not in full_text:
            continue
            
        # 3. We will do a character-by-character mapping to runs
        run_mapping = []
        for run_idx, run in enumerate(runs):
            for char_idx in range(len(run.text)):
                run_mapping.append((run_idx, char_idx))
                
        # 4. Find all occurrences
        import re
        matches = [m.start() for m in re.finditer(re.escape(placeholder), full_text)]
        
        # 5. Replace backwards so indices don't shift
        for start_idx in reversed(matches):
            end_idx = start_idx + len(placeholder) - 1
            
            start_run_idx, start_char_idx = run_mapping[start_idx]
            end_run_idx, end_char_idx = run_mapping[end_idx]
            
            # Delete text in all intermediate runs
            for i in range(start_run_idx + 1, end_run_idx):
                runs[i].text = ""
                
            # If it's in the same run
            if start_run_idx == end_run_idx:
                r_text = runs[start_run_idx].text
                runs[start_run_idx].text = r_text[:start_char_idx] + str(val) + r_text[end_char_idx + 1:]
            else:
                # Different runs
                r_start = runs[start_run_idx].text
                runs[start_run_idx].text = r_start[:start_char_idx] + str(val)
                
                r_end = runs[end_run_idx].text
                runs[end_run_idx].text = r_end[end_char_idx + 1:]
        
        # Re-build run mapping for next placeholders since lengths changed
