import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
import joblib
import re
from typing import Tuple, List, Dict
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import sys
from pathlib import Path

sys.path.append(str(Path.cwd().parents[1]))
from Modelling.preprocessing import cleanTextPipeline

class lightWeightIntentClassifier:
    def __init__(self, method = 'hybrid'):
        self.method = method
        self.model = None
        self.vectorizer = None
        self.feature_weights = {}

        try:
            self.nlp = spacy.load("en_core_web_sm") 
            self.use_spacy = True
        except:
            self.use_spacy = False
            print("Unable to use space, using simple preprocessing")

    def advancedPreprocessing(self, text: str) -> str:
        text = text.lower().strip()

        important_words = {"what", "why", "how", "when", "where", "who", "which",
                   "i", "me", "my", "mine", "we", "our", "us"}
        
        for word in important_words:
            self.nlp.vocab[word].is_stop = False

        if self.use_spacy == True:
            doc = self.nlp(text)

            tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]

            return ' '.join(tokens)    
        else:
            final_text = cleanTextPipeline(text)
            return final_text
        
    def extract_advanced_features(self, text: str) -> Dict[str, int]:
        """Extract domain-specific features for finance queries"""
        text_lower = text.lower()
        features = {}
        
        # Personal pronouns (strong indicator of personal queries)
        personal_pronouns = ['i', 'my', 'me', 'mine', 'myself']
        features['personal_pronoun_count'] = sum(1 for pronoun in personal_pronouns 
                                                if pronoun in text_lower)
        
        # Time references (common in personal queries)
        time_refs = ['month', 'week', 'year', 'today', 'yesterday', 'last', 'this']
        features['time_reference_count'] = sum(1 for ref in time_refs 
                                             if ref in text_lower)
        
        # Question words (common in general queries)
        question_words = ['what', 'how', 'why', 'when', 'where', 'explain', 'define']
        features['question_word_count'] = sum(1 for word in question_words 
                                            if word in text_lower)
        
        # Financial action words (personal queries)
        personal_actions = ['spend', 'spent', 'buy', 'bought', 'paid', 'save', 'saved']
        features['personal_action_count'] = sum(1 for action in personal_actions 
                                              if action in text_lower)
        
        # Financial concept words (general queries)
        concept_words = ['interest', 'investment', 'stock', 'bond', 'fund', 'market']
        features['concept_word_count'] = sum(1 for concept in concept_words 
                                           if concept in text_lower)
        
        # Query length (general queries tend to be shorter)
        features['query_length'] = len(text.split())
        
        # Possessive indicators
        features['has_possessive'] = 1 if any(word in text_lower for word in ['my', 'mine']) else 0
        
        return features
    
    def predictQuery(self, query: str) -> Tuple[str, float]:
        if self.method == "hybrid" and self.model and self.vectorizer:
            processed_query = self.advancedPreprocessing(query)
            query_vec = self.vectorizer.transform([processed_query])
    
            final_intent = self.model.predict(query_vec)[0]
            intent_probability = self.model.predict_proba(query_vec)[0]
    
            confidence = max(intent_probability)
        
        else:
            processed_query = self.advancedPreprocessing(query)
            # Pass as a list of strings if using pipeline
            final_intent = self.model.predict([processed_query])[0]
    
            if hasattr(self.model, "predict_proba"):
                intent_probability = self.model.predict_proba([processed_query])[0]
                confidence = max(intent_probability)
            else:
                confidence = 0.8
    
        features = self.extract_advanced_features(query)
    
        if final_intent == "personal" and features['personal_pronoun_count'] > 0:  
            confidence = min(confidence + 0.1, 1.0)
        elif final_intent == "general" and features['question_word_count'] > 0:
            confidence = min(confidence + 0.1, 1.0)
    
        return final_intent, confidence
    
    def saveModel(self, filepath = "intentClassifier.pkl"):
        model_data = {
            'model': self.model,
            'method': self.method,
            'vectorizer': self.vectorizer if hasattr(self, 'vectorizer') else None
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")

    def loadModel(self, filepath="intentClassifier.pkl"):
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.method = model_data['method']
            self.vectorizer = model_data['vectorizer'] if model_data['vectorizer'] else None
            print(f"Model loaded from {filepath}")
        except FileNotFoundError:
            print(f'{filepath} was not found!!')