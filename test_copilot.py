"""Test script for Clinical Question Copilot."""

import asyncio
from copilot_engine import ClinicalQuestionCopilot


def test_clinical_questions():
    """Test the copilot with various clinical questions."""
    
    print("Testing Clinical Question Copilot")
    print("=" * 50)
    
    # Initialize copilot
    copilot = ClinicalQuestionCopilot()
    
    # Test questions
    test_questions = [
        "What was the blood gas threshold for acidosis management?",
        "What ventilator settings are standard for ARDS?",
        "What are the criteria for sepsis diagnosis?",
        "How do you manage acute respiratory failure?",
        "What are the standard sedation protocols in ICU?",
        "How do you cook pasta?",  # Non-clinical question
        "What's the weather like today?",  # Non-clinical question
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\nTest {i}: {question}")
        print("-" * 40)
        
        try:
            response = copilot.process_question(question)
            
            print(f"Clinical: {not response['guardrail_triggered']}")
            print(f"Confidence: {response['confidence']:.2f}")
            
            if response['guardrail_triggered']:
                print(f"Guardrail Reason: {response['guardrail_reason']}")
                if response.get('suggestions'):
                    print("Suggestions:")
                    for suggestion in response['suggestions'][:2]:
                        print(f"   - {suggestion}")
            else:
                print(f"Answer: {response['answer'][:200]}...")
                print(f"Sources: {len(response['sources'])} found")
                
                if response['sources']:
                    for source in response['sources'][:2]:
                        print(f"   - {source['type']}: {source.get('title', source.get('patient_id', 'Unknown'))}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    # Print system stats
    print(f"\nSystem Statistics")
    print("-" * 40)
    stats = copilot.get_system_stats()
    print(f"Knowledge Base: {stats['knowledge_base']['total_documents']} documents")
    print(f"Total Interactions: {stats['total_interactions']}")
    print(f"Clinical Questions: {stats['clinical_questions']}")
    print(f"Guardrail Triggers: {stats['guardrail_triggers']}")


if __name__ == "__main__":
    test_clinical_questions()
