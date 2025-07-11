from PIL import Image
import imagehash
import os

# --- Perceptual Hashing ---
def calculate_image_hash(image_path: str, hash_size: int = 8) -> str | None:
    """
    Calculates a perceptual hash (average hash) of an image.
    Returns the hash as a hex string, or None if an error occurs.
    """
    try:
        img = Image.open(image_path)
        # Convert to grayscale and resize for more consistent hashing
        # img = img.convert("L").resize((hash_size * 2, hash_size * 2))
        # imagehash library handles conversions appropriately for its hash types.
        hash_value = imagehash.average_hash(img, hash_size=hash_size)
        return str(hash_value)
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except Exception as e:
        print(f"Error hashing image {image_path}: {e}")
        return None

# --- Mock Reverse Image Search ---
# This is a mock database of known image hashes and their supposed sources.
# In a real application, this would involve API calls to services like TinEye, Google Images, etc.
MOCK_IMAGE_DB = {
    "dummyhash123456789": [
        {"url": "https://www.example.com/plagiarized-image1.jpg", "similarity": "High"},
        {"url": "https://www.anotherdomain.net/original-source-maybe.png", "similarity": "Medium"}
    ],
    "anotherhashabcdef0": [
        {"url": "https://www.examplesource.com/image-abc.png", "similarity": "High"}
    ],
    # Add more mock hashes and sources as needed for testing
    # e.g. hash of a known test image
}

# Predefined hashes for specific test files (if you have them)
# To get these, you'd run calculate_image_hash on your test images first.
# For example, if you have 'test_image_duplicate.jpg' and its hash is 'ff818181818181ff'
# MOCK_IMAGE_DB["ff818181818181ff"] = [{"url": "https://www.knownsource.com/test_image_duplicate.jpg", "similarity": "Exact"}]


def mock_reverse_image_search(image_hash: str | None) -> list:
    """
    Simulates a reverse image search by checking a given hash against a mock database.
    Returns a list of mock 'found' sources.
    """
    if not image_hash:
        return []

    return MOCK_IMAGE_DB.get(image_hash, [])


# --- Advanced Similarity (Placeholder for CLIP/ResNet) ---
# def calculate_image_embedding(image_path: str):
#     """ Placeholder for calculating deep learning embeddings (e.g., CLIP, ResNet). """
#     # try:
#     #     from transformers import CLIPProcessor, CLIPModel # Example
#     #     model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
#     #     processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
#     #     image = Image.open(image_path)
#     #     inputs = processor(images=image, return_tensors="pt")
#     #     image_features = model.get_image_features(**inputs)
#     #     return image_features.detach().numpy()
#     # except Exception as e:
#     #     print(f"Error calculating CLIP embedding: {e}")
#     #     return None
#     print(f"Placeholder: Advanced embedding for {image_path} would be calculated here.")
#     return None

if __name__ == '__main__':
    # Create a dummy image file for testing calculate_image_hash
    # Note: This requires Pillow to be installed to create and save an image.
    # In a real test scenario, you'd use actual image files.
    dummy_image_path = "dummy_test_image.png"
    try:
        img = Image.new('RGB', (60, 30), color = 'red')
        img.save(dummy_image_path)

        # Test calculate_image_hash
        hash1 = calculate_image_hash(dummy_image_path)
        print(f"Hash for {dummy_image_path}: {hash1}")

        # Add its hash to MOCK_IMAGE_DB for testing mock_reverse_image_search
        if hash1:
            MOCK_IMAGE_DB[hash1] = [{"url": "https://www.test.com/dummy_image_source.png", "similarity": "Exact Match (Mocked)"}]

        # Test mock_reverse_image_search
        sources = mock_reverse_image_search(hash1)
        print(f"Mock sources for hash {hash1}: {sources}")

        sources_known = mock_reverse_image_search("dummyhash123456789")
        print(f"Mock sources for 'dummyhash123456789': {sources_known}")

        sources_unknown = mock_reverse_image_search("unknownhash000000")
        print(f"Mock sources for 'unknownhash000000': {sources_unknown}")

    except ImportError:
        print("Pillow is not installed. Skipping image creation for test.")
    except Exception as e:
        print(f"An error occurred during testing: {e}")
    finally:
        if os.path.exists(dummy_image_path):
            os.remove(dummy_image_path)
