from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sensitive_keywords = {
    "high": ["mental", "genetic", "hiv", "cancer", "psychiatric", "dna", "depression"],
    "medium": ["blood", "prescription", "diagnosis", "x-ray", "mri", "scan"],
    "low": ["steps", "fitness", "sleep", "calories", "exercise"]
}

safe_purposes = ["h", "treatment", "meresearcdical study", "healthcare", "diagnosis"]
risky_purposes = ["marketing", "ads", "insurance", "third-party", "resale"]

def explain_consent(org, data_type, purpose, days):
    return f"{org} is requesting access to your {data_type} data for {purpose}. This access will last for {days} days."

def get_risk_level(text):
    text = text.lower()

    for word in sensitive_keywords["high"]:
        if word in text:
            return "High"

    for word in sensitive_keywords["medium"]:
        if word in text:
            return "Medium"

    return "Low"

def similarity_check(text1, text2):
    vect = TfidfVectorizer()
    tfidf = vect.fit_transform([text1, text2])
    return cosine_similarity(tfidf)[0][1]

def ai_recommendation(data_type, purpose):
    risk = get_risk_level(data_type)
    purpose_lower = purpose.lower()

    recommendation = ""
    reason = ""

    if risk == "High":
        recommendation = "Reject"
        reason = "This data is highly sensitive and could cause serious privacy harm if misused."

    elif risk == "Medium":
        for word in risky_purposes:
            if word in purpose_lower:
                recommendation = "Reject"
                reason = "This data is moderately sensitive and the purpose appears risky."
                break
        else:
            recommendation = "Consider Carefully"
            reason = "This data is moderately sensitive. Only allow if you trust the organization."

    else:
        recommendation = "Accept"
        reason = "This data is low sensitivity and the risk to your privacy is minimal."

    return recommendation, reason