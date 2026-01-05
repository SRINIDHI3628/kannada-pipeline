def infer_category_from_caption(caption: str):
    caption = caption.lower()

    if any(word in caption for word in ["pothole", "crack", "broken road"]):
        return "pothole"

    if any(word in caption for word in ["garbage", "trash", "waste", "dump"]):
        return "garbage"

    if any(word in caption for word in ["water", "leak", "pipe"]):
        return "water leakage"

    if any(word in caption for word in ["streetlight", "lamp", "light pole"]):
        return "streetlight"

    return "unknown"
