"""Guardrails for Clinical Question Copilot to ensure questions stay within clinical scope."""

import re
from typing import List, Tuple, Dict, Any
from config import settings


class ClinicalGuardrails:
    """Implements guardrails to ensure questions are within ICU/hospital clinical scope."""
    
    def __init__(self):
        """Initialize the guardrails system."""
        self.clinical_keywords = settings.clinical_keywords
        self.non_clinical_keywords = [
            "cooking", "recipe", "food", "restaurant", "travel", "vacation",
            "entertainment", "movie", "music", "sports", "gaming", "technology",
            "programming", "business", "finance", "investment", "legal", "law",
            "education", "school", "university", "personal", "relationship",
            "weather", "politics", "news", "social media", "shopping"
        ]
        
        # Clinical question patterns
        self.clinical_patterns = [
            r"what.*(?:treatment|therapy|medication|drug|dose|protocol|guideline)",
            r"how.*(?:treat|manage|diagnose|monitor|assess)",
            r"when.*(?:start|stop|change|adjust)",
            r"what.*(?:criteria|threshold|normal|abnormal|range)",
            r"what.*(?:ventilator|respirator|oxygen|breathing)",
            r"what.*(?:blood|lab|test|result|value)",
            r"what.*(?:pressure|heart|cardiac|pulse|rhythm)",
            r"what.*(?:pain|sedation|analgesia|comfort)",
            r"what.*(?:infection|sepsis|antibiotic|fever)",
            r"what.*(?:nutrition|feeding|calorie|protein)",
            r"what.*(?:shock|vasopressor|pressors|vasopressin|inotrope|dobutamine|norepinephrine)",
            r"what.*(?:icu|intensive care|hospital|clinical|medical)",
            r"what.*(?:patient|case|scenario|situation)"
        ]
        
    
    def is_clinical_question(self, question: str) -> Tuple[bool, str, float]:
        """
        Determine if a question is within clinical scope.
        
        Returns:
            Tuple of (is_clinical, reason, confidence_score)
        """
        question_lower = question.lower()
        
        # Check for explicit non-clinical content
        non_clinical_score = self._calculate_non_clinical_score(question_lower)
        if non_clinical_score > 0.7:
            return False, f"Question appears to be about non-clinical topics: {self._get_non_clinical_keywords(question_lower)}", non_clinical_score
        
        

        # Check for clinical keywords
        clinical_score = self._calculate_clinical_score(question_lower)
        
        # Check for clinical question patterns
        pattern_score = self._calculate_pattern_score(question_lower)
        
        # Combined score (weighted)
        combined_score = (clinical_score * 0.6) + (pattern_score * 0.4)
        
        if combined_score >= 0.1:
            return True, f"Question contains clinical content (score: {combined_score:.2f})", combined_score
        else:
            return False, f"Question does not appear to be clinical in nature (score: {combined_score:.2f})", combined_score
    
    def _calculate_clinical_score(self, question: str) -> float:
        """Calculate how clinical a question is based on keywords."""
        clinical_matches = 0
        total_keywords = len(self.clinical_keywords)
        
        for keyword in self.clinical_keywords:
            if keyword in question:
                clinical_matches += 1
        
        # Normalize by the number of words in the question to avoid very long questions getting high scores
        question_words = len(question.split())
        if question_words > 0:
            return min(clinical_matches / question_words * 10, 1.0)  # Scale up and cap at 1.0
        return 0
    
    def _calculate_non_clinical_score(self, question: str) -> float:
        """Calculate how non-clinical a question is based on keywords."""
        non_clinical_matches = 0
        total_non_clinical = len(self.non_clinical_keywords)
        
        for keyword in self.non_clinical_keywords:
            if keyword in question:
                non_clinical_matches += 1
        
        return non_clinical_matches / total_non_clinical if total_non_clinical > 0 else 0
    
    def _calculate_pattern_score(self, question: str) -> float:
        """Calculate score based on clinical question patterns."""
        pattern_matches = 0
        
        for pattern in self.clinical_patterns:
            if re.search(pattern, question, re.IGNORECASE):
                pattern_matches += 1
        
        return min(pattern_matches / len(self.clinical_patterns), 1.0)

    
    
    def _get_non_clinical_keywords(self, question: str) -> List[str]:
        """Get non-clinical keywords found in the question."""
        found_keywords = []
        for keyword in self.non_clinical_keywords:
            if keyword in question:
                found_keywords.append(keyword)
        return found_keywords
    
    def get_scope_guidance(self) -> str:
        """Get guidance on what types of questions are appropriate."""
        return """
        I can help with clinical questions related to:
        
        • ICU and hospital medicine protocols
        • Critical care management (ventilators, hemodynamics, sedation)
        • Clinical diagnosis and treatment guidelines
        • Laboratory values and thresholds
        • Medication dosing and management
        • Patient monitoring and assessment
        • Infection control and prevention
        • Nutrition support in critical care
        • Emergency and acute care protocols
        
        Please ask questions about patient care, clinical protocols, or medical management within the ICU/hospital setting.
        """
    
    def suggest_clinical_questions(self) -> List[str]:
        """Suggest example clinical questions."""
        return [
            "What are the standard ventilator settings for ARDS?",
            "What is the blood gas threshold for acidosis management?",
            "How do you manage septic shock in the ICU?",
            "What are the criteria for sepsis diagnosis?",
            "How do you titrate vasopressors in cardiogenic shock?",
            "What is the protocol for daily sedation interruption?",
            "How do you assess fluid responsiveness in ICU patients?",
            "What are the guidelines for central line insertion?",
            "How do you manage acute respiratory failure?",
            "What are the nutrition requirements for ICU patients?"
        ]
