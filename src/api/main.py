#!/usr/bin/env python3
"""
FastAPI REST Service for Dynamic Sports Performance Analytics Engine
Production-ready API with endpoints for player data, rankings, similarity, and predictions
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uvicorn
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.data_structures import PerformanceDataStructures, Player
from core.algorithms import PerformanceScoreAlgorithm, PlayerSimilarityAlgorithm, PredictiveAlgorithm

# Pydantic models for API requests/responses
class PlayerStats(BaseModel):
    goals: float = 0
    assists: float = 0
    pass_accuracy: float = 0
    shots_total: float = 0
    tackles_won: float = 0
    interceptions: float = 0
    key_passes: float = 0
    minutes_played: float = 0
    average_rating: float = 0

class PlayerCreate(BaseModel):
    player_id: int
    name: str
    position: str
    team_id: int
    age: int
    stats: PlayerStats

class PlayerResponse(BaseModel):
    player_id: int
    name: str
    position: str
    team_id: int
    age: int
    performance_score: float
    stats: Dict[str, float]
    last_updated: float

class RankingResponse(BaseModel):
    rank: int
    player: PlayerResponse
    score: float

class SimilarPlayerResponse(BaseModel):
    player_id: int
    similarity_score: float
    player_details: Optional[PlayerResponse] = None

class PredictionResponse(BaseModel):
    player_id: int
    prediction: float
    confidence: float
    model_used: str
    prediction_date: str

class SystemStatsResponse(BaseModel):
    total_players: int
    hash_table_load_factor: float
    heap_size: int
    graph_nodes: int
    graph_edges: int
    last_update: float
    api_version: str

# Initialize FastAPI app
app = FastAPI(
    title="Dynamic Sports Performance Analytics API",
    description="High-performance API for soccer player analytics with optimized data structures and algorithms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
data_structures = PerformanceDataStructures(hash_table_capacity=2000, heap_size=200)
performance_algorithm = PerformanceScoreAlgorithm()
similarity_algorithm = PlayerSimilarityAlgorithm()
prediction_algorithm = PredictiveAlgorithm()

# Global state
is_similarity_fitted = False
is_prediction_fitted = False

@app.on_event("startup")
async def startup_event():
    """Initialize the API with sample data."""
    # Load sample data or initialize from database
    await load_initial_data()

async def load_initial_data():
    """Load initial player data into the system."""
    # This would typically load from a database
    # For demo purposes, we'll create some sample players
    sample_players = [
        {
            "player_id": 1,
            "name": "Erling Haaland",
            "position": "Attacker",
            "team_id": 9,
            "age": 23,
            "stats": {
                "goals": 36,
                "assists": 8,
                "shots_total": 116,
                "shots_on_target": 68,
                "key_passes": 23,
                "dribbles_successful": 45,
                "minutes_played": 2769,
                "average_rating": 8.2
            }
        },
        {
            "player_id": 2,
            "name": "Kevin De Bruyne",
            "position": "Midfielder",
            "team_id": 9,
            "age": 32,
            "stats": {
                "goals": 7,
                "assists": 16,
                "pass_accuracy": 87.5,
                "key_passes": 89,
                "tackles_won": 34,
                "minutes_played": 2156,
                "average_rating": 8.0
            }
        }
    ]
    
    for player_data in sample_players:
        stats_dict = player_data["stats"]
        score = performance_algorithm.calculate_performance_score(stats_dict, player_data["position"])
        
        player = Player(
            player_id=player_data["player_id"],
            name=player_data["name"],
            position=player_data["position"],
            team_id=player_data["team_id"],
            age=player_data["age"],
            performance_score=score,
            stats=stats_dict,
            last_updated=datetime.now().timestamp()
        )
        
        data_structures.add_player(player)

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Dynamic Sports Performance Analytics API",
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "operational"
    }

@app.post("/players", response_model=PlayerResponse)
async def create_player(player_data: PlayerCreate):
    """Create a new player with O(1) insertion."""
    # Calculate performance score
    stats_dict = player_data.stats.dict()
    score = performance_algorithm.calculate_performance_score(stats_dict, player_data.position)
    
    # Create player object
    player = Player(
        player_id=player_data.player_id,
        name=player_data.name,
        position=player_data.position,
        team_id=player_data.team_id,
        age=player_data.age,
        performance_score=score,
        stats=stats_dict,
        last_updated=datetime.now().timestamp()
    )
    
    # Add to data structures
    data_structures.add_player(player)
    
    return PlayerResponse(
        player_id=player.player_id,
        name=player.name,
        position=player.position,
        team_id=player.team_id,
        age=player.age,
        performance_score=player.performance_score,
        stats=player.stats,
        last_updated=player.last_updated
    )

@app.get("/players/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int = Path(..., description="Player ID")):
    """Get player data with O(1) hash table lookup."""
    player = data_structures.get_player(player_id)
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return PlayerResponse(
        player_id=player.player_id,
        name=player.name,
        position=player.position,
        team_id=player.team_id,
        age=player.age,
        performance_score=player.performance_score,
        stats=player.stats,
        last_updated=player.last_updated
    )

@app.put("/players/{player_id}/score")
async def update_player_score(
    player_id: int = Path(..., description="Player ID"),
    new_score: float = Query(..., description="New performance score")
):
    """Update player's performance score with O(log n) heap update."""
    player = data_structures.get_player(player_id)
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    data_structures.update_player_score(player_id, new_score)
    
    return {"message": f"Player {player_id} score updated to {new_score}"}

@app.get("/rankings/top/{k}", response_model=List[RankingResponse])
async def get_top_rankings(k: int = Path(..., description="Number of top players to return", ge=1, le=100)):
    """Get top K players from max-heap with O(k log n) complexity."""
    top_performers = data_structures.get_top_performers(k)
    
    rankings = []
    for rank, (player, score) in enumerate(top_performers, 1):
        rankings.append(RankingResponse(
            rank=rank,
            player=PlayerResponse(
                player_id=player.player_id,
                name=player.name,
                position=player.position,
                team_id=player.team_id,
                age=player.age,
                performance_score=player.performance_score,
                stats=player.stats,
                last_updated=player.last_updated
            ),
            score=score
        ))
    
    return rankings

@app.get("/players/{player_id}/similar", response_model=List[SimilarPlayerResponse])
async def get_similar_players(
    player_id: int = Path(..., description="Player ID"),
    method: str = Query("cosine", description="Similarity method: cosine, euclidean, or cluster"),
    top_k: int = Query(10, description="Number of similar players to return", ge=1, le=50)
):
    """Find similar players using clustering algorithms."""
    global is_similarity_fitted
    
    # Fit similarity algorithm if not already done
    if not is_similarity_fitted:
        all_players = data_structures.player_hash_table.get_all_players()
        players_data = []
        
        for player in all_players:
            players_data.append({
                'player_id': player.player_id,
                'position': player.position,
                'stats': player.stats
            })
        
        if len(players_data) >= 3:  # Minimum required for clustering
            similarity_algorithm.fit(players_data)
            is_similarity_fitted = True
        else:
            raise HTTPException(status_code=400, detail="Insufficient data for similarity analysis")
    
    # Check if target player exists
    target_player = data_structures.get_player(player_id)
    if not target_player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Find similar players
    similar_players = similarity_algorithm.find_similar_players(player_id, method, top_k)
    
    result = []
    for similar_player_id, similarity_score in similar_players:
        similar_player = data_structures.get_player(similar_player_id)
        
        player_details = None
        if similar_player:
            player_details = PlayerResponse(
                player_id=similar_player.player_id,
                name=similar_player.name,
                position=similar_player.position,
                team_id=similar_player.team_id,
                age=similar_player.age,
                performance_score=similar_player.performance_score,
                stats=similar_player.stats,
                last_updated=similar_player.last_updated
            )
        
        result.append(SimilarPlayerResponse(
            player_id=similar_player_id,
            similarity_score=similarity_score,
            player_details=player_details
        ))
    
    return result

@app.get("/players/{player_id}/predict", response_model=PredictionResponse)
async def predict_player_performance(
    player_id: int = Path(..., description="Player ID"),
    model: str = Query("random_forest", description="Prediction model: linear_regression or random_forest")
):
    """Predict future performance using time-series algorithms."""
    global is_prediction_fitted
    
    player = data_structures.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # For demo purposes, use current stats as historical data
    # In production, this would use actual historical data
    if not is_prediction_fitted:
        # Create mock historical data for training
        all_players = data_structures.player_hash_table.get_all_players()
        training_data = {}
        
        for p in all_players:
            # Create mock historical seasons
            training_data[p.player_id] = [
                {**p.stats, 'age': p.age - 1, 'performance_score': p.performance_score * 0.9},
                {**p.stats, 'age': p.age, 'performance_score': p.performance_score}
            ]
        
        prediction_algorithm.fit_prediction_models(training_data)
        is_prediction_fitted = True
    
    # Make prediction
    current_stats = {**player.stats, 'age': player.age}
    prediction_result = prediction_algorithm.predict_performance(current_stats, model)
    
    return PredictionResponse(
        player_id=player_id,
        prediction=prediction_result['prediction'],
        confidence=prediction_result['confidence'],
        model_used=prediction_result['model_used'],
        prediction_date=datetime.now().isoformat()
    )

@app.get("/system/stats", response_model=SystemStatsResponse)
async def get_system_stats():
    """Get comprehensive system performance statistics."""
    stats = data_structures.get_system_stats()
    
    return SystemStatsResponse(
        total_players=stats['hash_table_stats']['size'],
        hash_table_load_factor=stats['hash_table_stats']['load_factor'],
        heap_size=stats['heap_size'],
        graph_nodes=stats['graph_nodes'],
        graph_edges=stats['graph_edges'],
        last_update=stats['last_update'],
        api_version="1.0.0"
    )

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "hash_table": "operational",
            "heap": "operational",
            "graph": "operational",
            "algorithms": "operational"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
