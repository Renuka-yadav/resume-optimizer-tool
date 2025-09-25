from sentence_transformers import SentenceTransformer, util

# Load a pre-trained model for semantic search.
model = SentenceTransformer('all-MiniLM-L6-v2')

def match_resume_to_jd(resume_text, jd_text):
    """
    Calculates the semantic similarity between a resume and a job description
    using a pre-trained Sentence Transformer model.
    """
    # Create embeddings for the resume and job description
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)
    
    # Compute cosine similarity
    similarity_score = util.pytorch_cos_sim(resume_embedding, jd_embedding)
    
    # Return the similarity score as a percentage, rounded to 2 decimal places
    return round(float(similarity_score) * 100, 2)