import re

class PersonalIntentClassifier:
    """
    Rule-based classifier to distinguish between:
      - personal_sql → data retrieval or calculation queries
      - personal_rag → analytical, reasoning, or advice queries
    """

    def __init__(self):
        # Keywords that indicate SQL-like (factual) queries
        self.sql_keywords = [
            "how much", "total", "sum", "list", "show", "display", "average", 
            "spent", "spend", "paid", "pay", "transactions", "balance", 
            "bill", "expense", "purchases", "income", "deposit", "withdrawal", 
            "earned", "budget left", "remaining budget"
        ]

        # Keywords that indicate reasoning or analytical (RAG) queries
        self.rag_keywords = [
            "should", "am i", "is my", "compare", "trend", "analyze", "why", 
            "how can", "suggest", "recommend", "improve", "optimize", "better", 
            "advise", "help me", "forecast", "predict", "future", "enough",
            "normal", "good", "okay", "healthy", "overspending", "saving rate"
        ]

    def classify(self, query: str):
        q = query.lower().strip()

        # Check keyword presence
        sql_hits = sum(1 for word in self.sql_keywords if re.search(rf"\b{word}\b", q))
        rag_hits = sum(1 for word in self.rag_keywords if re.search(rf"\b{word}\b", q))

        # Heuristics for SQL-like queries (factual)
        if sql_hits > rag_hits and sql_hits > 0:
            return "personal_sql", 0.9

        # Heuristics for analytical/advisory queries (reasoning)
        elif rag_hits > sql_hits and rag_hits > 0:
            return "personal_rag", 0.9

        # If ambiguous: fallback rule based on structure
        elif re.search(r"\b(how|what|when|show|list|calculate)\b", q):
            return "personal_sql", 0.7
        elif re.search(r"\b(should|am i|is my|compare|why|how can)\b", q):
            return "personal_rag", 0.7

        # Default fallback
        return "personal_sql", 0.5