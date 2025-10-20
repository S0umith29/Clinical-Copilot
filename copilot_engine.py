"""Main Clinical Question Copilot engine with RAG capabilities."""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from knowledge_base import ClinicalKnowledgeBase
from guardrails import ClinicalGuardrails
from config import settings


class ClinicalQuestionCopilot:
    """Main engine for the Clinical Question Copilot."""
    
    def __init__(self):
        """Initialize the copilot engine."""
        self.knowledge_base = ClinicalKnowledgeBase()
        self.guardrails = ClinicalGuardrails()
        self.conversation_history = []
    
    def process_question(self, question: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a clinical question and return a response.
        
        Args:
            question: The clinical question to process
            user_id: Optional user identifier for conversation tracking
            
        Returns:
            Dictionary containing the response and metadata
        """
        timestamp = datetime.now().isoformat()
        
        # Step 1: Apply guardrails
        is_clinical, guardrail_reason, guardrail_confidence = self.guardrails.is_clinical_question(question)
        
        if not is_clinical:
            response = {
                "answer": "I only answer clinical questions grounded in ICU protocols. " + 
                         "Please ask about patient care, clinical protocols, or medical management within the ICU/hospital setting.",
                "sources": [],
                "confidence": guardrail_confidence,
                "guardrail_triggered": True,
                "guardrail_reason": guardrail_reason,
                "suggestions": self.guardrails.suggest_clinical_questions()[:3]
            }
        else:
            # Step 2: Search knowledge base
            context = self.knowledge_base.get_context_for_question(question)
            # Pull more candidates to improve coverage
            search_results = self.knowledge_base.search(question)
            
            # Step 3: Generate response
            if context and context != "No relevant clinical information found in the knowledge base.":
                answer = self._generate_clinical_response(question, context, search_results)
                sources = self._format_sources(search_results)
            else:
                answer = ("I don't have specific information about this in my current knowledge base. "
                         "This question may be outside my scope or the information may not be available "
                         "in the MIMIC-IV demo data. Please consult current clinical guidelines and protocols.")
                sources = []
            
            # Step 3b: Confidence fusion (guardrails + retrieval)
            retrieval_similarity = 0.0
            if search_results:
                # Use max similarity as retrieval signal
                retrieval_similarity = max(r.get("similarity", 0.0) for r in search_results)
            has_sources = 1.0 if sources else 0.0
            # Weighted fusion
            confidence = (
                0.5 * guardrail_confidence +
                0.4 * retrieval_similarity +
                0.1 * has_sources
            )
            # Clamp to [0,1]
            confidence = max(0.0, min(1.0, confidence))

            response = {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "guardrail_triggered": False,
                "context_used": len(search_results) > 0
            }
        
        # Step 4: Log interaction
        interaction = {
            "timestamp": timestamp,
            "user_id": user_id,
            "question": question,
            "response": response,
            "is_clinical": is_clinical
        }
        self.conversation_history.append(interaction)
        
        return response
    
    def _generate_clinical_response(self, question: str, context: str, search_results: List[Dict]) -> str:
        """Generate a clinical response based on the question and context."""
        
        # Extract key information from search results
        protocols_found = []
        cases_found = []
        
        for result in search_results:
            metadata = result["metadata"]
            if metadata.get("type") == "protocol":
                protocols_found.append({
                    "title": metadata.get("title", "Unknown Protocol"),
                    "content": result["document"],
                    "similarity": result["similarity"]
                })
            elif metadata.get("type") == "clinical_note":
                cases_found.append({
                    "patient_id": metadata.get("patient_id", "Unknown"),
                    "diagnosis": metadata.get("diagnosis", "Unknown"),
                    "content": result["document"],
                    "similarity": result["similarity"]
                })
        
        # Generate response based on available information
        response_parts = []
        
        if protocols_found:
            response_parts.append("Based on clinical protocols and guidelines from MIMIC-IV:")
            
            for protocol in protocols_found[:2]:  # Limit to top 2 protocols
                response_parts.append(f"\n<strong><em>{protocol['title']}:</em></strong>")
                # Extract the main content (after "Content: ")
                content = protocol['content']
                if "Content: " in content:
                    main_content = content.split("Content: ", 1)[1]
                    response_parts.append(main_content)
                else:
                    response_parts.append(content)
        
        if cases_found:
            response_parts.append("\n<strong><em>Clinical Cases from MIMIC-IV:</em></strong>")
            
            for case in cases_found[:1]:  # Limit to 1 case example
                response_parts.append(f"\nCase: {case['patient_id']} - {case['diagnosis']}")
                # Extract the main content (after "Content: ")
                content = case['content']
                if "Content: " in content:
                    main_content = content.split("Content: ", 1)[1]
                    response_parts.append(main_content)
                else:
                    response_parts.append(content)
        
        if not response_parts:
            return "I found some relevant information but couldn't generate a specific response. Please rephrase your question or ask about a more specific clinical topic."
        
        # Add disclaimer
        response_parts.append("\n\n<em>Note: This information is based on MIMIC-IV demo data and clinical protocols. Always consult current guidelines and your clinical team for patient care decisions.</em>")
        
        # Use HTML line breaks so formatting renders in the UI
        return "\n".join(response_parts).replace("\n", "<br>")
    
    def _format_sources(self, search_results: List[Dict]) -> List[Dict[str, Any]]:
        """Format search results as sources."""
        sources = []
        
        for result in search_results:
            metadata = result["metadata"]
            source = {
                "type": metadata.get("type", "unknown"),
                "similarity": result["similarity"],
                "content_preview": result["document"][:200] + "..." if len(result["document"]) > 200 else result["document"],
                "rank": result.get("rank")
            }
            
            if metadata.get("type") == "protocol":
                source.update({
                    "title": metadata.get("title", "Unknown Protocol"),
                    "category": metadata.get("category", "general"),
                    "source_name": metadata.get("source_name")
                })
            elif metadata.get("type") == "clinical_note":
                source.update({
                    "patient_id": metadata.get("patient_id", "Unknown"),
                    "diagnosis": metadata.get("diagnosis", "Unknown"),
                    "icu_unit": metadata.get("icu_unit", "Unknown"),
                    "note_type": metadata.get("note_type", "Unknown")
                })
            
            sources.append(source)
        
        return sources
    
    def get_conversation_history(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get conversation history for a user."""
        if user_id:
            return [interaction for interaction in self.conversation_history 
                   if interaction.get("user_id") == user_id]
        return self.conversation_history
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        kb_stats = self.knowledge_base.get_stats()
        
        return {
            "knowledge_base": kb_stats,
            "total_interactions": len(self.conversation_history),
            "clinical_questions": len([i for i in self.conversation_history if i.get("is_clinical")]),
            "guardrail_triggers": len([i for i in self.conversation_history 
                                     if i.get("response", {}).get("guardrail_triggered")])
        }
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def suggest_questions(self) -> List[str]:
        """Get suggested clinical questions."""
        return self.guardrails.suggest_clinical_questions()
