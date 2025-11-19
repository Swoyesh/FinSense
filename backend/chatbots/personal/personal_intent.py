import re

class PersonalIntentClassifier:
    """
    Rule-based classifier to distinguish between:
      - personal_sql → data retrieval or calculation queries
      - personal_rag → analytical, reasoning, or advice queries
    """
    def __init__(self):
        self.sql_keywords = [
            "how much", "total", "sum", "list", "show", "display", "average", 
            "spent", "spend", "paid", "pay", "transactions", "balance", 
            "bill", "expense", "purchases", "income", "deposit", "withdrawal", 
            "earned", "budget left", "remaining budget", "breakdown", "break down",
            "detail", "details", "further", "more information", "itemize"
        ]
        
        self.rag_keywords = [
            "should", "am i", "is my", "compare", "trend", "analyze", "why", 
            "how can", "suggest", "recommend", "improve", "optimize", "better", 
            "advise", "help me", "forecast", "predict", "future", "enough",
            "normal", "good", "okay", "healthy", "overspending", "saving rate"
        ]
        
        self.followup_keywords = [
            "break", "breakdown", "detail", "more", "further", "also",
            "what about", "show me", "list", "can you", "elaborate",
            "expand", "tell me more"
        ]

    def classify(self, query: str, context: str = ""):
        """
        Classify the query based on keywords and context.
        
        Args:
            query: The user's current question
            context: Previous conversation history (optional)
        
        Returns:
            Tuple of (intent, confidence)
        """
        q = query.lower().strip()
        ctx = context.lower().strip() if context else ""
        
        is_followup = any(keyword in q for keyword in self.followup_keywords)
        
        context_has_data = any(indicator in ctx for indicator in [
            'npr', 'spent', 'total', 'rupees', 'rs', 'expense', 
            'income', 'per day', 'per week', 'per month'
        ])
        
        if is_followup and context_has_data:
            return ("personal_sql", 0.95)
        

        sql_hits = sum(1 for word in self.sql_keywords if re.search(rf"\b{word}\b", q))
        rag_hits = sum(1 for word in self.rag_keywords if re.search(rf"\b{word}\b", q))
        
        if sql_hits > rag_hits and sql_hits > 0:
            return ("personal_sql", 0.9)
        elif rag_hits > sql_hits and rag_hits > 0:
            return ("personal_rag", 0.9)
        
        elif re.search(r"\b(how|what|when|show|list|calculate|breakdown|detail)\b", q):
            return ("personal_sql", 0.7)
        elif re.search(r"\b(should|am i|is my|compare|why|how can)\b", q):
            return ("personal_rag", 0.7)
        
        return ("personal_sql", 0.5)