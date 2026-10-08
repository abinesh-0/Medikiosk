def score(text, structured):
    return 0.95 if text and structured else 0.65 if structured else 0.25
