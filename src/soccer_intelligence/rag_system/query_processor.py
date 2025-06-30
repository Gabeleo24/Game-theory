"""
Query processor for understanding and categorizing user queries.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
import logging

from ..utils.config import Config


class QueryProcessor:
    """Processes and categorizes user queries for the RAG system."""
    
    def __init__(self):
        """Initialize the query processor."""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Define query patterns and keywords
        self.query_patterns = {
            'player': [
                r'\b(?:player|striker|midfielder|defender|goalkeeper|forward)\b',
                r'\b(?:goals?|assists?|performance|statistics|stats)\b',
                r'\b(?:who is|tell me about|analyze|compare)\b.*\b(?:player|striker|midfielder)\b'
            ],
            'team': [
                r'\b(?:team|club|squad)\b',
                r'\b(?:formation|tactics|strategy|style)\b',
                r'\b(?:wins?|losses?|draws?|points|standings)\b'
            ],
            'formation': [
                r'\b(?:formation|4-4-2|4-3-3|3-5-2|4-5-1|3-4-3)\b',
                r'\b(?:tactical|tactics|positioning|lineup)\b',
                r'\b(?:best formation|recommend|formation for)\b'
            ],
            'match': [
                r'\b(?:match|game|fixture|result)\b',
                r'\b(?:vs|versus|against)\b',
                r'\b(?:score|result|outcome)\b'
            ],
            'shapley': [
                r'\b(?:contribution|shapley|impact|value)\b',
                r'\b(?:most important|key player|valuable)\b',
                r'\b(?:game theory|marginal)\b'
            ]
        }
        
        # Entity extraction patterns
        self.entity_patterns = {
            'player_name': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Simple name pattern
            'team_name': r'\b(?:Real Madrid|Barcelona|Manchester United|Liverpool|Arsenal|Chelsea|Bayern Munich|PSG|Juventus|AC Milan|Inter Milan|Atletico Madrid|Valencia|Sevilla)\b',
            'formation': r'\b(?:4-4-2|4-3-3|3-5-2|4-5-1|3-4-3|5-3-2|4-2-3-1|3-4-1-2)\b',
            'position': r'\b(?:striker|midfielder|defender|goalkeeper|forward|winger|center-back|full-back)\b'
        }
    
    def process_query(self, query: str, context_type: str = 'general') -> Dict[str, Any]:
        """
        Process a user query and extract relevant information.
        
        Args:
            query: User query string
            context_type: Context type hint
            
        Returns:
            Processed query information
        """
        self.logger.debug(f"Processing query: {query}")
        
        # Clean and normalize query
        cleaned_query = self._clean_query(query)
        
        # Determine query type
        query_type = self._classify_query(cleaned_query, context_type)
        
        # Extract entities
        entities = self._extract_entities(cleaned_query)
        
        # Generate search keywords
        keywords = self._extract_keywords(cleaned_query, query_type)
        
        # Create processed query
        processed_query = {
            'original_query': query,
            'processed_text': cleaned_query,
            'query_type': query_type,
            'entities': entities,
            'keywords': keywords,
            'context_type': context_type,
            'intent': self._determine_intent(cleaned_query, query_type)
        }
        
        self.logger.debug(f"Processed query type: {query_type}, entities: {len(entities)}")
        return processed_query
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize the query."""
        # Convert to lowercase
        cleaned = query.lower().strip()
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove special characters but keep important punctuation
        cleaned = re.sub(r'[^\w\s\-\?]', '', cleaned)
        
        return cleaned
    
    def _classify_query(self, query: str, context_hint: str) -> str:
        """Classify the query type based on patterns."""
        # If context hint is specific, use it
        if context_hint in ['player', 'team', 'formation', 'match']:
            return context_hint
        
        # Score each query type
        type_scores = {}
        
        for query_type, patterns in self.query_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches
            type_scores[query_type] = score
        
        # Return the type with highest score, or 'general' if no clear winner
        if max(type_scores.values()) > 0:
            return max(type_scores, key=type_scores.get)
        else:
            return 'general'
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract named entities from the query."""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates
        
        return entities
    
    def _extract_keywords(self, query: str, query_type: str) -> List[str]:
        """Extract relevant keywords for search."""
        # Remove stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'what', 'who', 'where', 'when', 'why',
            'how', 'which', 'that', 'this', 'these', 'those', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Split into words and filter
        words = query.split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add query-type specific keywords
        type_keywords = {
            'player': ['performance', 'statistics', 'goals', 'assists'],
            'team': ['tactics', 'formation', 'results', 'performance'],
            'formation': ['tactical', 'positioning', 'strategy'],
            'match': ['result', 'score', 'performance'],
            'shapley': ['contribution', 'impact', 'value', 'importance']
        }
        
        if query_type in type_keywords:
            keywords.extend(type_keywords[query_type])
        
        return list(set(keywords))  # Remove duplicates
    
    def _determine_intent(self, query: str, query_type: str) -> str:
        """Determine the user's intent."""
        intent_patterns = {
            'comparison': r'\b(?:compare|vs|versus|better|best|worse|worst|difference)\b',
            'recommendation': r'\b(?:recommend|suggest|should|best|optimal|ideal)\b',
            'analysis': r'\b(?:analyze|analysis|explain|why|how|performance)\b',
            'information': r'\b(?:who|what|when|where|tell me|information|about)\b',
            'prediction': r'\b(?:predict|forecast|will|future|next|expect)\b'
        }
        
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return intent
        
        return 'information'  # Default intent
    
    def suggest_query_improvements(self, query: str) -> List[str]:
        """Suggest improvements to make the query more specific."""
        suggestions = []
        
        # Check if query is too short
        if len(query.split()) < 3:
            suggestions.append("Try to be more specific with your question")
        
        # Check for entity mentions
        entities = self._extract_entities(query.lower())
        
        if not entities.get('player_name') and 'player' in query.lower():
            suggestions.append("Mention specific player names for better results")
        
        if not entities.get('team_name') and 'team' in query.lower():
            suggestions.append("Mention specific team names for better results")
        
        if not entities.get('formation') and 'formation' in query.lower():
            suggestions.append("Specify the formation you're interested in (e.g., 4-3-3, 4-4-2)")
        
        return suggestions
    
    def get_query_examples(self, query_type: str) -> List[str]:
        """Get example queries for a specific type."""
        examples = {
            'player': [
                "What are Lionel Messi's performance statistics this season?",
                "Compare Cristiano Ronaldo and Kylian Mbappe's goal scoring",
                "Who is the best midfielder in La Liga?"
            ],
            'team': [
                "How has Real Madrid performed this season?",
                "What is Barcelona's preferred formation?",
                "Compare Manchester United and Liverpool's tactics"
            ],
            'formation': [
                "What is the best formation for counter-attacking?",
                "Explain the 4-3-3 formation advantages",
                "Recommend a formation for a team with strong wingers"
            ],
            'match': [
                "What was the result of Real Madrid vs Barcelona?",
                "Analyze the El Clasico match performance",
                "Show me recent match results for Liverpool"
            ],
            'shapley': [
                "Which player contributes most to their team's success?",
                "Show me Shapley value analysis for Manchester City",
                "Who are the most valuable players based on contribution?"
            ]
        }
        
        return examples.get(query_type, [
            "Ask me about player statistics, team performance, formations, or match analysis",
            "I can help with tactical analysis and player comparisons",
            "Try asking about specific players, teams, or formations"
        ])
