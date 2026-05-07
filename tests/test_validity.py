from app.ml.validity.predict import predict_validity


def test_predict_validity_rejects_noise():
    result = predict_validity("Muhammad chemistry physics")
    assert result["label"] != "Valid Requirement"
    assert result["confidence"] >= 0.6
    assert result["reason"] in {
        "Too few meaningful words",
        "Mostly personal names",
        "No recognized actor",
        "No action verbs, mostly nouns",
        "Non-requirement Sentence",
        "Domain Keywords Only",
    }


def test_predict_validity_accepts_valid_requirement():
    text = "The user shall be able to login to the system using email and password."
    result = predict_validity(text)
    assert result["label"] == "Valid Requirement"
    assert result["confidence"] >= 0.7
    assert "Passes validity checks" in result["reason"]
