"""
RAG (Retrieval-Augmented Generation) engine for soccer intelligence queries.
"""

import openai
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import json

from ..utils.config import Config
from .vector_store import VectorStore
from .query_processor import QueryProcessor


class RAGEngine:
    """Main RAG engine for soccer intelligence queries."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the RAG engine.
        
        Args:
            api_key: OpenAI API key. If None, loads from config.
        """
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # OpenAI configuration
        self.api_key = api_key or self.config.get('openai.api_key')
        if self.api_key:
            openai.api_key = self.api_key
        
        self.model = self.config.get('openai.model', 'gpt-4')
        self.temperature = self.config.get('openai.temperature', 0.7)
        self.max_tokens = self.config.get('openai.max_tokens', 1000)
        
        # RAG configuration
        self.top_k = self.config.get('rag_system.retrieval.top_k', 5)
        self.similarity_threshold = self.config.get('rag_system.retrieval.similarity_threshold', 0.7)
        self.context_window = self.config.get('rag_system.generation.context_window', 4000)
        
        # Initialize components
        self.vector_store = VectorStore()
        self.query_processor = QueryProcessor()
        
        # Knowledge base
        self.knowledge_base = {}
        self.is_initialized = False
    
    def initialize(self, player_data: pd.DataFrame, team_data: pd.DataFrame, 
                  match_data: pd.DataFrame, shapley_data: Optional[pd.DataFrame] = None) -> None:
        """
        Initialize the RAG engine with soccer data.
        
        Args:
            player_data: Player statistics DataFrame
            team_data: Team data DataFrame
            match_data: Match data DataFrame
            shapley_data: Optional Shapley analysis results
        """
        self.logger.info("Initializing RAG engine with soccer data")
        
        try:
            # Store data
            self.knowledge_base = {
                'players': player_data,
                'teams': team_data,
                'matches': match_data,
                'shapley': shapley_data if shapley_data is not None else pd.DataFrame()
            }
            
            # Create embeddings and populate vector store
            self._create_knowledge_embeddings()
            
            self.is_initialized = True
            self.logger.info("RAG engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG engine: {e}")
            raise
    
    def query(self, question: str, context_type: str = 'general') -> Dict[str, Any]:
        """
        Process a query and generate a response.
        
        Args:
            question: User question
            context_type: Type of context ('general', 'formation', 'player', 'team')
            
        Returns:
            Response with answer and metadata
        """
        if not self.is_initialized:
            return {
                'answer': 'RAG engine not initialized. Please initialize with data first.',
                'error': 'Not initialized'
            }
        
        self.logger.info(f"Processing query: {question[:100]}...")
        
        try:
            # Process the query
            processed_query = self.query_processor.process_query(question, context_type)
            
            # Retrieve relevant context
            relevant_context = self._retrieve_context(processed_query)
            
            # Generate response
            response = self._generate_response(question, relevant_context, context_type)
            
            return {
                'answer': response['answer'],
                'confidence': response.get('confidence', 0.8),
                'sources': relevant_context.get('sources', []),
                'context_type': context_type,
                'processed_query': processed_query,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return {
                'answer': 'I apologize, but I encountered an error processing your question. Please try rephrasing it.',
                'error': str(e)
            }
    
    def _create_knowledge_embeddings(self) -> None:
        """Create embeddings for the knowledge base."""
        self.logger.info("Creating knowledge embeddings")
        
        documents = []
        
        # Create player documents
        if not self.knowledge_base['players'].empty:
            for _, player in self.knowledge_base['players'].iterrows():
                doc = self._create_player_document(player)
                documents.append(doc)
        
        # Create team documents
        if not self.knowledge_base['teams'].empty:
            for _, team in self.knowledge_base['teams'].iterrows():
                doc = self._create_team_document(team)
                documents.append(doc)
        
        # Create match documents (sample for performance)
        if not self.knowledge_base['matches'].empty:
            sample_matches = self.knowledge_base['matches'].sample(
                min(100, len(self.knowledge_base['matches']))
            )
            for _, match in sample_matches.iterrows():
                doc = self._create_match_document(match)
                documents.append(doc)
        
        # Create Shapley analysis documents
        if not self.knowledge_base['shapley'].empty:
            for _, analysis in self.knowledge_base['shapley'].iterrows():
                doc = self._create_shapley_document(analysis)
                documents.append(doc)
        
        # Add to vector store
        self.vector_store.add_documents(documents)
        
        self.logger.info(f"Created embeddings for {len(documents)} documents")
    
    def _create_player_document(self, player: pd.Series) -> Dict[str, Any]:
        """Create a document for a player."""
        content = f"""
        Player: {player.get('player_name', 'Unknown')}
        Age: {player.get('age', 'Unknown')}
        Position: {player.get('games_position', 'Unknown')}
        Team: {player.get('team_name', 'Unknown')}
        Nationality: {player.get('nationality', 'Unknown')}
        
        Performance Statistics:
        - Games Played: {player.get('games_appearances', 0)}
        - Goals: {player.get('goals_total', 0)}
        - Assists: {player.get('goals_assists', 0)}
        - Minutes Played: {player.get('games_minutes', 0)}
        - Rating: {player.get('games_rating', 'N/A')}
        
        Advanced Metrics:
        - Goals per Game: {player.get('goals_per_game', 0):.2f}
        - Assists per Game: {player.get('assists_per_game', 0):.2f}
        - Pass Accuracy: {player.get('passes_accuracy', 0)}%
        - Tackles: {player.get('tackles_total', 0)}
        - Interceptions: {player.get('tackles_interceptions', 0)}
        """
        
        return {
            'id': f"player_{player.get('player_id', 'unknown')}",
            'content': content.strip(),
            'type': 'player',
            'metadata': {
                'player_id': player.get('player_id'),
                'player_name': player.get('player_name'),
                'team_id': player.get('team_id'),
                'position': player.get('games_position')
            }
        }
    
    def _create_team_document(self, team: pd.Series) -> Dict[str, Any]:
        """Create a document for a team."""
        content = f"""
        Team: {team.get('team_name', 'Unknown')}
        Country: {team.get('team_country', 'Unknown')}
        Founded: {team.get('team_founded', 'Unknown')}
        Stadium: {team.get('venue_name', 'Unknown')}
        Stadium Capacity: {team.get('venue_capacity', 'Unknown')}
        
        Performance Statistics:
        - Total Matches: {team.get('total_matches', 0)}
        - Wins: {team.get('wins', 0)}
        - Draws: {team.get('draws', 0)}
        - Losses: {team.get('losses', 0)}
        - Win Percentage: {team.get('win_percentage', 0):.1f}%
        - Goals Scored: {team.get('goals_scored', 0)}
        - Goals Conceded: {team.get('goals_conceded', 0)}
        - Goal Difference: {team.get('goal_difference', 0)}
        - Points: {team.get('points', 0)}
        """
        
        return {
            'id': f"team_{team.get('team_id', 'unknown')}",
            'content': content.strip(),
            'type': 'team',
            'metadata': {
                'team_id': team.get('team_id'),
                'team_name': team.get('team_name'),
                'country': team.get('team_country')
            }
        }
    
    def _create_match_document(self, match: pd.Series) -> Dict[str, Any]:
        """Create a document for a match."""
        content = f"""
        Match: {match.get('home_team_name', 'Unknown')} vs {match.get('away_team_name', 'Unknown')}
        Date: {match.get('date', 'Unknown')}
        Venue: {match.get('venue', 'Unknown')}
        Result: {match.get('home_goals', 0)} - {match.get('away_goals', 0)}
        Status: {match.get('status', 'Unknown')}
        
        Match Details:
        - Total Goals: {match.get('total_goals', 0)}
        - Goal Difference: {match.get('goal_difference', 0)}
        - Result: {match.get('result', 'Unknown')}
        - High Scoring: {'Yes' if match.get('high_scoring', 0) else 'No'}
        - Both Teams Scored: {'Yes' if match.get('both_teams_scored', 0) else 'No'}
        """
        
        return {
            'id': f"match_{match.get('match_id', 'unknown')}",
            'content': content.strip(),
            'type': 'match',
            'metadata': {
                'match_id': match.get('match_id'),
                'home_team': match.get('home_team_name'),
                'away_team': match.get('away_team_name'),
                'date': match.get('date')
            }
        }
    
    def _create_shapley_document(self, analysis: pd.Series) -> Dict[str, Any]:
        """Create a document for Shapley analysis."""
        content = f"""
        Shapley Value Analysis for {analysis.get('player_name', 'Unknown')}
        Team: {analysis.get('team_id', 'Unknown')}
        
        Contribution Analysis:
        - Combined Contribution: {analysis.get('combined_contribution', 0):.2f}%
        - Marginal Contribution: {analysis.get('marginal_contribution', 0):.2f}%
        - SHAP Contribution: {analysis.get('shap_contribution', 0):.2f}%
        - Contribution Rank: {analysis.get('contribution_rank', 'Unknown')}
        - Contribution Category: {analysis.get('contribution_category', 'Unknown')}
        - Contribution Percentile: {analysis.get('contribution_percentile', 0):.1f}%
        
        This analysis shows how much this player contributes to their team's overall performance
        using Shapley value methodology from game theory.
        """
        
        return {
            'id': f"shapley_{analysis.get('player_id', 'unknown')}",
            'content': content.strip(),
            'type': 'shapley',
            'metadata': {
                'player_id': analysis.get('player_id'),
                'player_name': analysis.get('player_name'),
                'team_id': analysis.get('team_id'),
                'contribution_category': analysis.get('contribution_category')
            }
        }
    
    def _retrieve_context(self, processed_query: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant context for the query."""
        query_text = processed_query['processed_text']
        query_type = processed_query['query_type']
        entities = processed_query['entities']
        
        # Search vector store
        search_results = self.vector_store.search(
            query_text, 
            top_k=self.top_k,
            filter_type=query_type if query_type != 'general' else None
        )
        
        # Filter by similarity threshold
        relevant_results = [
            result for result in search_results 
            if result['similarity'] >= self.similarity_threshold
        ]
        
        # If no results above threshold, take top results anyway
        if not relevant_results and search_results:
            relevant_results = search_results[:3]
        
        # Compile context
        context_text = ""
        sources = []
        
        for result in relevant_results:
            context_text += f"\n\n{result['content']}"
            sources.append({
                'id': result['id'],
                'type': result['type'],
                'similarity': result['similarity'],
                'metadata': result.get('metadata', {})
            })
        
        return {
            'context_text': context_text.strip(),
            'sources': sources,
            'entities_found': entities
        }
    
    def _generate_response(self, question: str, context: Dict[str, Any], 
                         context_type: str) -> Dict[str, Any]:
        """Generate response using OpenAI."""
        if not self.api_key:
            return {
                'answer': 'OpenAI API key not configured. Please set up your API key to use the RAG system.',
                'confidence': 0.0
            }
        
        # Prepare prompt
        system_prompt = self._get_system_prompt(context_type)
        user_prompt = self._create_user_prompt(question, context['context_text'])
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                'answer': answer,
                'confidence': 0.9,  # High confidence for GPT-4 responses
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return {
                'answer': 'I apologize, but I encountered an error generating a response. Please try again.',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _get_system_prompt(self, context_type: str) -> str:
        """Get system prompt based on context type."""
        base_prompt = """You are a soccer intelligence assistant with expertise in player analysis, 
        team tactics, and performance metrics. You have access to comprehensive soccer data including 
        player statistics, team performance, match results, and advanced analytics like Shapley values.
        
        Provide accurate, insightful responses based on the provided context. When discussing player 
        contributions, reference Shapley value analysis when available. Be specific with statistics 
        and provide tactical insights when relevant."""
        
        context_specific = {
            'formation': " Focus on tactical formations, player positioning, and strategic recommendations.",
            'player': " Focus on individual player analysis, performance metrics, and comparisons.",
            'team': " Focus on team performance, tactics, and collective analysis.",
            'general': " Provide comprehensive analysis covering all aspects of soccer intelligence."
        }
        
        return base_prompt + context_specific.get(context_type, context_specific['general'])
    
    def _create_user_prompt(self, question: str, context: str) -> str:
        """Create user prompt with question and context."""
        return f"""Based on the following soccer data and analysis:

{context}

Please answer this question: {question}

Provide a comprehensive answer that includes relevant statistics, insights, and tactical analysis where appropriate."""
