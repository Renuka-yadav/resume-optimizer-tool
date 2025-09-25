def generate_score(similarity, missing_keywords):
    base_score = similarity
    penalty = len(missing_keywords) * 1.5  # weight of missing keywords
    final_score = max(base_score - penalty, 0)
    return round(final_score, 2)
