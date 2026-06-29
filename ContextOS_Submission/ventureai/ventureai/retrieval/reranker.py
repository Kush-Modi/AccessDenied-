import os
import sys
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def rerank_items(items: List[Dict[str, Any]], query_text: str = None) -> List[Dict[str, Any]]:
    """
    Reranks items by calculating additional lexical matching / word overlap
    between query_text and document contents, boosting final scores of items
    with high query term density.
    """
    if not query_text or not items:
        return items
        
    query_words = set(query_text.lower().replace(",", " ").replace("|", " ").split())
    # Filter short common words
    stopwords = {"and", "the", "for", "with", "a", "an", "in", "on", "at", "to", "of", "is", "are"}
    query_words = {w for w in query_words if w not in stopwords and len(w) > 1}
    
    if not query_words:
        return items
        
    reranked = []
    for item in items:
        content_text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}".lower()
        
        # Calculate overlap ratio
        matched_words = sum(1 for w in query_words if w in content_text)
        overlap_score = matched_words / len(query_words)
        
        # Add a small boost to final_score (e.g. up to +0.05) based on lexical overlap
        item_copy = item.copy()
        scores = item_copy.get("scores", {}).copy()
        
        original_score = scores.get("final_score", 0.5)
        # Apply up to +0.10 lexical overlap boost
        boost = overlap_score * 0.10
        new_score = min(1.0, original_score + boost)
        
        scores["lexical_boost"] = boost
        scores["final_score"] = new_score
        item_copy["scores"] = scores
        reranked.append(item_copy)
        
    # Re-sort by updated final score
    reranked.sort(key=lambda x: x["scores"]["final_score"], reverse=True)
    return reranked
