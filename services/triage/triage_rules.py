def highest_priority(flags):
    if any(f["severity"]=="URGENT" for f in flags): return "URGENT"
    if any(f["severity"]=="HIGH" for f in flags): return "HIGH"
    if flags: return "HIGH"
    return "NORMAL"
