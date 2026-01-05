# import torch #type:ignore
# from transformers import ViTFeatureExtractor, ViTForImageClassification #type:ignore
# from PIL import Image #type:ignore

# MODEL_NAME = "google/vit-base-patch16-224"

# LABELS = [
#     "pothole",
#     "garbage",
#     "water leakage",
#     "streetlight"
# ]

# feature_extractor = ViTFeatureExtractor.from_pretrained(MODEL_NAME)

# model = ViTForImageClassification.from_pretrained(
#     MODEL_NAME,
#     num_labels=len(LABELS),
#     ignore_mismatched_sizes=True
# )
# model.eval()


# def predict_issue(image_file):
#     image = Image.open(image_file).convert("RGB")

#     inputs = feature_extractor(
#         images=image,
#         return_tensors="pt"
#     )

#     with torch.no_grad():
#         outputs = model(**inputs)

#     probs = torch.softmax(outputs.logits, dim=1)
#     confidence, idx = torch.max(probs, dim=1)

#     return LABELS[idx.item()], round(confidence.item(), 2)

import torch
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from PIL import Image

MODEL_NAME = "nlpconnect/vit-gpt2-image-captioning"

device = "cuda" if torch.cuda.is_available() else "cpu"

model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME).to(device)
image_processor = ViTImageProcessor.from_pretrained(MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model.eval()

def generate_caption(image_file):
    image = Image.open(image_file).convert("RGB")

    pixel_values = image_processor(images=image, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    with torch.no_grad():
        output_ids = model.generate(
            pixel_values,
            max_length=30,
            num_beams=4
        )

    caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return caption

