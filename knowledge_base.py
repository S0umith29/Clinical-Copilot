"""Knowledge base manager for Clinical Question Copilot."""

import json
import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import numpy as np
from config import settings


class ClinicalKnowledgeBase:
    """Manages the clinical knowledge base using ChromaDB and sentence transformers."""
    
    def __init__(self):
        """Initialize the knowledge base."""
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model
        )
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = None
        self._initialize_collection()
        self._load_clinical_data()
    
    def _initialize_collection(self):
        """Initialize or get the ChromaDB collection."""
        try:
            # Try to load existing with embedding function bound
            self.collection = self.chroma_client.get_collection(
                "clinical_knowledge",
                embedding_function=self.embedding_function
            )
            print("Loaded existing clinical knowledge collection")

            # Rebuild if embedding model metadata mismatches
            meta = self.collection.metadata or {}
            stored_model = meta.get("embedding_model")
            if stored_model and stored_model != settings.embedding_model:
                print(
                    f"Embedding model changed ({stored_model} -> {settings.embedding_model}), rebuilding collection..."
                )
                self._rebuild_collection()

        except ValueError:
            # Create new collection with embedding function
            self.collection = self.chroma_client.create_collection(
                name="clinical_knowledge",
                embedding_function=self.embedding_function,
                metadata={
                    "description": "Clinical protocols and notes from MIMIC-IV demo",
                    "embedding_model": settings.embedding_model,
                },
            )
            print("Created new clinical knowledge collection")

    def _rebuild_collection(self):
        """Drop and rebuild the collection to ensure embedding consistency."""
        try:
            self.chroma_client.delete_collection("clinical_knowledge")
        except Exception:
            pass
        self.collection = self.chroma_client.create_collection(
            name="clinical_knowledge",
            embedding_function=self.embedding_function,
            metadata={
                "description": "Clinical protocols and notes from MIMIC-IV demo",
                "embedding_model": settings.embedding_model,
            },
        )
        # Reload data into fresh collection
        self._load_clinical_data(force_reload=True)
    
    def _load_clinical_data(self, force_reload: bool = False):
        """Load clinical protocols and notes into the knowledge base."""
        if not force_reload and self.collection.count() > 0:
            print(f"Knowledge base already contains {self.collection.count()} documents")
            return
        
        print("Loading clinical data into knowledge base...")
        
        # Load clinical protocols
        protocols_path = os.path.join(settings.mimic_data_path, "clinical_protocols.json")
        if os.path.exists(protocols_path):
            with open(protocols_path, 'r') as f:
                protocols = json.load(f)
                self._add_protocols(protocols)
        
        # Load clinical notes
        notes_path = os.path.join(settings.mimic_data_path, "clinical_notes.json")
        if os.path.exists(notes_path):
            with open(notes_path, 'r') as f:
                notes = json.load(f)
                self._add_clinical_notes(notes)
        
        print(f"Knowledge base loaded with {self.collection.count()} documents")
    
    def _add_protocols(self, protocols: Dict[str, Any]):
        """Add clinical protocols to the knowledge base."""
        documents = []
        metadatas = []
        ids = []
        
        for protocol_id, protocol_data in protocols.items():
            content = f"Title: {protocol_data['title']}\nSource: {protocol_data['source']}\nContent: {protocol_data['content']}"
            documents.append(content)
            metadatas.append({
                "type": "protocol",
                "category": protocol_data.get("category", "general"),
                "keywords": " ".join(protocol_data.get("keywords", [])),
                "title": protocol_data["title"],
                "source_name": protocol_data.get("source")
            })
            ids.append(f"protocol_{protocol_id}")
        
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Added {len(documents)} clinical protocols")
    
    def _add_clinical_notes(self, notes: Dict[str, Any]):
        """Add clinical notes to the knowledge base."""
        documents = []
        metadatas = []
        ids = []
        
        for case_id, case_data in notes.items():
            for note in case_data["clinical_notes"]:
                content = f"Patient: {case_data['patient_id']}\nDate: {note['timestamp']}\nType: {note['note_type']}\nDiagnosis: {case_data['diagnosis']}\nContent: {note['content']}"
                documents.append(content)
                metadatas.append({
                    "type": "clinical_note",
                    "patient_id": case_data["patient_id"],
                    "icu_unit": case_data["icu_unit"],
                    "diagnosis": case_data["diagnosis"],
                    "note_type": note["note_type"],
                    "timestamp": note["timestamp"],
                    "keywords": " ".join(case_data.get("keywords", []))
                })
                ids.append(f"note_{case_id}_{note['timestamp']}")
        
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Added {len(documents)} clinical notes")
    
    def search(self, query: str, n_results: int = None) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant clinical information."""
        try:
            if n_results is None:
                n_results = getattr(settings, 'top_k_results', 8)
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                # Convert distance to similarity score (ChromaDB uses cosine distance)
                similarity = 1 - distance
                
                if similarity >= settings.similarity_threshold:
                    search_results.append({
                        "document": doc,
                        "metadata": metadata,
                        "similarity": similarity,
                        "rank": i + 1
                    })
            
            return search_results
        
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return []
    
    def get_context_for_question(self, question: str) -> str:
        """Get relevant context for a clinical question."""
        results = self.search(question, n_results=getattr(settings, 'top_k_context', 5))
        
        if not results:
            return "No relevant clinical information found in the knowledge base."
        
        context_parts = []
        for result in results:
            metadata = result["metadata"]
            doc_type = metadata.get("type", "unknown")
            
            if doc_type == "protocol":
                context_parts.append(f"Clinical Protocol: {metadata.get('title', 'Unknown')}\n{result['document']}")
            elif doc_type == "clinical_note":
                context_parts.append(f"Clinical Case: {metadata.get('patient_id', 'Unknown')} - {metadata.get('diagnosis', 'Unknown')}\n{result['document']}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        total_docs = self.collection.count()
        
        # Get sample of documents to analyze types
        sample_results = self.collection.get(limit=100)
        protocol_count = sum(1 for meta in sample_results["metadatas"] if meta.get("type") == "protocol")
        note_count = sum(1 for meta in sample_results["metadatas"] if meta.get("type") == "clinical_note")
        
        return {
            "total_documents": total_docs,
            "protocols": protocol_count,
            "clinical_notes": note_count,
            "embedding_model": settings.embedding_model
        }
