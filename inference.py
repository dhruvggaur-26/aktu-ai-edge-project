# ==================================================
# HINDI NLP INFERENCE MODULE
# ==================================================

# Demo mode
# Later, Member 3's actual ONNX inference code
# will be connected here.


MODEL_MODE = "DEMO"


# ==================================================
# PREDICT FUNCTION
# ==================================================

def predict(text):

    # ----------------------------------------------
    # DEMO INFERENCE
    # ----------------------------------------------

    if MODEL_MODE == "DEMO":

        result = {
            "entities": [
                {
                    "text": "राहुल",
                    "label": "PERSON"
                },
                {
                    "text": "दिल्ली",
                    "label": "LOCATION"
                }
            ],

            "sentiment": "Positive",

            "confidence": 0.92,

            "inference_time": 18
        }

        return result


    # ----------------------------------------------
    # FUTURE ONNX INFERENCE
    # ----------------------------------------------

    else:

        # Member 3's ONNX inference code
        # will be added here.

        result = {
            "entities": [],
            "sentiment": "Neutral",
            "confidence": 0.0,
            "inference_time": 0
        }

        return result