import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document

# Paths
FAISS_FOLDER = os.path.join("rag_store", "faiss_index")
FAISS_PATH = os.path.join(FAISS_FOLDER, "index.faiss")
PICKLE_PATH = os.path.join(FAISS_FOLDER, "index.pkl")  # consistent location

# Load embedding model
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Load or create FAISS store
def load_faiss():
    if os.path.exists(FAISS_FOLDER) and os.path.exists(FAISS_PATH):
        try:
            print("📂 Loading existing FAISS store...")
            return FAISS.load_local(
                folder_path=FAISS_FOLDER,
                embeddings=embedding_model,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"⚠️ Failed to load existing FAISS store: {e}")

    # First-time setup
    print("🆕 Creating new FAISS store...")
    dummy_doc = Document(
        page_content="This is a dummy description to initialize FAISS.",
        metadata={"title": "dummy_title"}
    )
    store = FAISS.from_documents([dummy_doc], embedding_model)
    store.save_local(FAISS_FOLDER)
    return store

# Save the FAISS store
def save_faiss(store: FAISS):
    try:
        print("💾 Saving FAISS store to existing directory...")
        store.save_local(FAISS_FOLDER)
        print(f"✅ Successfully saved FAISS store to {FAISS_FOLDER}")
    except Exception as e:
        print(f"❌ Failed to save FAISS store: {e}")
        print("⚠️ Continuing without saving to disk...")

# Main duplicate checker agent
async def run_duplicate_checker(state):
    try:
        original_title = state["metadata"].get("title", "").strip()
        meta_description = state["metadata"].get("meta_description", "").strip()
        title = original_title.lower()
        description = meta_description.lower()
        query = f"{title} - {description}"

        print(f"🔍 Checking for duplicate: '{title}'")

        # Load FAISS
        faiss_store = load_faiss()

        try:
            results = faiss_store.similarity_search(query, k=10)
            print(f"📊 Found {len(results)} similar documents to check")

            for i, result in enumerate(results):
                stored_title = result.metadata.get("title", "").strip().lower()
                print(f"   {i+1}. Comparing: '{stored_title}' vs '{title}'")
                if stored_title == title:
                    print(f"🔍 DUPLICATE DETECTED: '{stored_title}' matches '{title}'")
                    return {**state, "duplicate_check_result": "fail"}

            print(f"✅ No exact duplicates found for: '{title}'")
        except Exception as search_error:
            print(f"⚠️ Error during similarity search: {search_error}")

        # Clean metadata before saving
        clean_metadata = {
            "title": str(title),
            "original_title": str(original_title)
        }

        new_doc = Document(
            page_content=query,
            metadata=clean_metadata
        )
        faiss_store.add_documents([new_doc])
        save_faiss(faiss_store)
        print(f"✅ New entry added: '{title}'")

        return {**state, "duplicate_check_result": "pass"}

    except Exception as e:
        print(f"❌ Error in duplicate checker: {e}")
        return {**state, "duplicate_check_result": "pass"}

# ClearingFAISS store for dev resets
def clear_faiss_store():
    try:
        if os.path.exists(FAISS_PATH):
            os.remove(FAISS_PATH)
        if os.path.exists(PICKLE_PATH):
            os.remove(PICKLE_PATH)
        print("🗑️ FAISS store cleared")
    except Exception as e:
        print(f"❌ Error clearing FAISS store: {e}")

# Debug function to inspect stored titles
def debug_faiss_contents():
    try:
        store = load_faiss()
        all_docs = store.similarity_search("", k=100)
        print(f"📋 FAISS store contains {len(all_docs)} documents:")
        for i, doc in enumerate(all_docs):
            title = doc.metadata.get("title", "No title")
            print(f"   {i+1}. {title}")
    except Exception as e:
        print(f"❌ Error debugging FAISS contents: {e}")
