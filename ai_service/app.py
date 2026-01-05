# from flask import Flask, request, jsonify
# from predict import predict_issue

# app = Flask(__name__)

# @app.route('/predict-issue', methods=['POST'])
# def predict():
#     image = request.files['image']
#     issue, confidence = predict_issue(image)
    
#     return jsonify({
#         "issue": issue,
#         "confidence": confidence
#     })

# if __name__ == "__main__":
#     app.run(port=5001)

from flask import Flask, request, jsonify
from predict import generate_caption

app = Flask(__name__)

@app.route("/predict-issue", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image = request.files["image"]
    caption = generate_caption(image)

    return jsonify({
        "caption": caption
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5001, debug=True)
