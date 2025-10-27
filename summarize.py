"""
Reads workflows.jsonl, groups similar events and produces simple JSON workflow suggestions.
"""
import os
import json
from collections import Counter, defaultdict

# =============================================================================
# 1. CONFIGURATION
# =============================================================================
DATA_DIR = os.path.join(os.getcwd(), "data")
INPUT_FILE = os.path.join(DATA_DIR, "workflows.jsonl")
OUTPUT_SUMMARY = os.path.join(DATA_DIR, "workflow_summaries.json")

# Mapping of detected event keywords to a human-readable workflow suggestion
KEYWORDS_TO_WORKFLOW = {
    "open_excel": "Open Excel and edit spreadsheet",
    "save_detected": "Save file or document",
    "download": "Download something from browser",
}

# =============================================================================
# 2. DATA LOADING
# =============================================================================
def load_events(path=INPUT_FILE):
    """Loads a list of event dictionaries from a JSONL file."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        # Load each non-empty line as a JSON object
        return [json.loads(line) for line in f if line.strip()]

# =============================================================================
# 3. ANALYSIS AND SUMMARIZATION LOGIC (Indentation Corrected)
# =============================================================================
def summarize(events):
    """
    Groups events based on inferred event types and counts their occurrences.
    Collects up to 3 examples for each type.
    """
    counter = Counter()
    examples = defaultdict(list)
    
    for e in events:
        # Type check for robustness (must be inside the loop)
        if not isinstance(e, dict):
            continue
            
        inferred = e.get("inferred_events", [])
        
        # Type check for robustness (must be inside the loop)
        if not isinstance(inferred, list):
            continue
            
        # Iterate over the list of inferred events within the record 'e'
        for ie in inferred:
            # Type check for robustness (must be inside the inner loop)
            if not isinstance(ie, dict):
                continue
                
            event_type = ie.get("type")
                
            if event_type: # Only process if 'type' is present
                counter[event_type] += 1
                    
                # Collect a few examples
                if len(examples[event_type]) < 3:
                    examples[event_type].append({
                        "ts": e.get("ts"), 
                        "path": e.get("path"), 
                        "ocr": e.get("ocr_text", "")[:200]
                    })
                        
    # Format the final list of workflow suggestions (outside the loop)
    workflows = []
    for k, cnt in counter.most_common():
        workflows.append({
            "workflow_type": KEYWORDS_TO_WORKFLOW.get(k, k),
            "detected_keyword": k,
            "occurrences": cnt,
            "examples": examples[k]
        })
    return workflows

# =============================================================================
# 4. DATA SAVING
# =============================================================================
def save_summary(summaries, path=OUTPUT_SUMMARY):
    """Writes the list of workflow summaries to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

# =============================================================================
# 5. MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":
    # Load events from the JSONL file
    events = load_events()
    
    # Generate the workflow summaries
    s = summarize(events)
    
    # Save the results to a JSON file
    save_summary(s)
    
    print(f"Loaded {len(events)} total events.")
    print(f"Saved {len(s)} unique workflow summaries to {OUTPUT_SUMMARY}")