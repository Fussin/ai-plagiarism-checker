from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np

# Load a pre-trained sentence transformer model
# Using a relatively small but effective model.
# The first time this runs, it will download the model.
try:
    model_name = 'all-MiniLM-L6-v2'
    model = SentenceTransformer(model_name)
    print(f"SentenceTransformer model '{model_name}' loaded successfully.")
except Exception as e:
    print(f"Error loading SentenceTransformer model '{model_name}': {e}")
    model = None

def split_into_sentences(text: str) -> list[str]:
    """
    Simple sentence splitter. Can be improved with more sophisticated NLP libraries
    like spaCy or NLTK for better accuracy on complex texts.
    """
    import re
    # Basic splitting by common punctuation followed by space or end of string.
    # This is a simplification; robust sentence tokenization is complex.
    sentences = re.split(r'(?<=[.!?])\s+', text.replace('\n', ' ').strip())
    return [s.strip() for s in sentences if s.strip()]


def check_text_similarity_self(text: str, similarity_threshold: float = 0.85) -> dict:
    """
    Checks for self-plagiarism within a given text by comparing sentence embeddings.
    Returns a dictionary with an overall originality score and a list of similar sentence pairs.
    """
    if not model:
        return {
            "originality_score": 1.0, # Default if model isn't loaded
            "similar_pairs": [],
            "message": "NLP model not available. Skipping advanced similarity check."
        }

    sentences = split_into_sentences(text)
    if len(sentences) < 2:
        return {
            "originality_score": 1.0, # Not enough sentences to compare
            "similar_pairs": [],
            "message": "Not enough sentences for self-similarity check."
        }

    try:
        embeddings = model.encode(sentences, convert_to_tensor=True)

        # Calculate cosine similarity between all pairs of sentences
        # We are interested in the upper triangle of the similarity matrix (excluding diagonal)
        similar_pairs = []
        num_sentences = len(sentences)
        total_comparisons = 0
        highly_similar_comparisons = 0

        # Compute cosine similarity using util.cos_sim
        # This returns a full similarity matrix
        cosine_scores = util.cos_sim(embeddings, embeddings)

        for i in range(num_sentences):
            for j in range(i + 1, num_sentences): # Avoid self-comparison and redundant pairs
                similarity = cosine_scores[i][j].item() # .item() to get Python number from tensor
                total_comparisons +=1
                if similarity >= similarity_threshold:
                    highly_similar_comparisons +=1
                    similar_pairs.append({
                        "sentence1_index": i,
                        "sentence1_text": sentences[i],
                        "sentence2_index": j,
                        "sentence2_text": sentences[j],
                        "similarity": round(similarity, 3)
                    })

        # Calculate an originality score based on the proportion of non-highly-similar pairs
        # This is a simplistic score for demonstration.
        originality_score = 1.0
        if total_comparisons > 0 :
            originality_score = 1.0 - (highly_similar_comparisons / total_comparisons)

        # If many sentences are similar, the score will be lower.
        # Cap at a minimum score if there are any similar pairs found.
        if highly_similar_comparisons > 0 and originality_score == 1.0: # Should not happen with current logic
             originality_score = 0.9
        elif highly_similar_comparisons == 0:
            originality_score = 1.0


        return {
            "originality_score": round(originality_score, 3),
            "similar_pairs": similar_pairs,
            "message": f"Found {len(similar_pairs)} highly similar sentence pairs (threshold: {similarity_threshold})."
        }

    except Exception as e:
        print(f"Error during text similarity check: {e}")
        return {
            "originality_score": 1.0, # Default on error
            "similar_pairs": [],
            "message": f"Error during similarity analysis: {str(e)}"
        }

if __name__ == '__main__':
    # Test the functions
    sample_text_unique = "This is the first sentence. This is a second, quite different sentence. A third one follows."
    sample_text_similar = "This is the first sentence. It is a beautiful day. This is the first sentence. What a lovely day it is. It is a beautiful day."

    print("--- Unique Text Check ---")
    if model:
        result_unique = check_text_similarity_self(sample_text_unique)
        print(f"Originality: {result_unique['originality_score']}")
        print(f"Message: {result_unique['message']}")
        for pair in result_unique['similar_pairs']:
            print(f"  Pair: '{pair['sentence1_text']}' <-> '{pair['sentence2_text']}' (Similarity: {pair['similarity']})")
    else:
        print("NLP model not loaded, skipping unique text check.")

    print("\n--- Similar Text Check ---")
    if model:
        result_similar = check_text_similarity_self(sample_text_similar)
        print(f"Originality: {result_similar['originality_score']}")
        print(f"Message: {result_similar['message']}")
        for pair in result_similar['similar_pairs']:
            print(f"  Pair: '{pair['sentence1_text']}' <-> '{pair['sentence2_text']}' (Similarity: {pair['similarity']})")
    else:
        print("NLP model not loaded, skipping similar text check.")

    test_sentences = split_into_sentences(sample_text_similar)
    print("\nSentences from similar text:")
    for i, s in enumerate(test_sentences):
        print(f"{i}: {s}")

    test_sentences_2 = split_into_sentences("Hello world. This is a test.\nAnother line here. Is it working? Yes!")
    print("\nSentences from another text:")
    for i, s in enumerate(test_sentences_2):
        print(f"{i}: {s}")
