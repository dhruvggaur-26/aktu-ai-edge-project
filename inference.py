# ==================================================
# HINDI NLP INFERENCE MODULE
# ==================================================

import time

MODEL_MODE = "DEMO"


# ==================================================
# PREDICT FUNCTION
# ==================================================

def predict(text):

    start_time = time.time()

    text_lower = text.lower()

    # ==================================================
    # DEMO SENTIMENT KEYWORDS
    # ==================================================

    positive_words = [
        "अच्छा",
        "अच्छी",
        "अच्छे",
        "खुश",
        "खुशी",
        "पसंद",
        "सुंदर",
        "शानदार",
        "बेहतरीन",
        "बहुत अच्छा",
        "बहुत अच्छी",
        "सफल",
        "सफलता",
        "love",
        "good",
        "great"
    ]

    negative_words = [
        "बुरा",
        "बुरी",
        "बुरे",
        "दुख",
        "दुखी",
        "नफरत",
        "खराब",
        "बेकार",
        "समस्या",
        "परेशान",
        "असफल",
        "असफलता",
        "bad",
        "hate",
        "worst"
    ]

    positive_count = sum(
        1 for word in positive_words
        if word in text_lower
    )

    negative_count = sum(
        1 for word in negative_words
        if word in text_lower
    )


    # ==================================================
    # SENTIMENT DECISION
    # ==================================================

    if positive_count > negative_count:

        sentiment = "Positive"
        confidence = 0.92

    elif negative_count > positive_count:

        sentiment = "Negative"
        confidence = 0.89

    else:

        sentiment = "Neutral"
        confidence = 0.75


    # ==================================================
    # DEMO ENTITY DETECTION
    # ==================================================

    known_people = [
        "राहुल",
        "अमन",
        "रोहित",
        "अमित",
        "नेहा",
        "पूजा"
    ]

    known_locations = [
        "दिल्ली",
        "मोरादाबाद",
        "कानपुर",
        "लखनऊ",
        "आगरा",
        "मुंबई",
        "भारत",
        "नोएडा"
    ]

    entities = []


    # PERSON detection

    for person in known_people:

        if person in text:

            entities.append(
                {
                    "text": person,
                    "label": "PERSON"
                }
            )


    # LOCATION detection

    for location in known_locations:

        if location in text:

            entities.append(
                {
                    "text": location,
                    "label": "LOCATION"
                }
            )


    # ==================================================
    # INFERENCE TIME
    # ==================================================

    inference_time = round(
        (time.time() - start_time) * 1000,
        2
    )


    # Avoid 0 ms in display

    if inference_time < 1:

        inference_time = 1


    # ==================================================
    # RESULT
    # ==================================================

    result = {

        "entities": entities,

        "sentiment": sentiment,

        "confidence": confidence,

        "inference_time": inference_time
    }


    return result