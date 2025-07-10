#!/usr/bin/env python3
"""
Streamlit Dashboard for Dynamic Sports Performance Analytics Engine
Interactive dashboard consuming the FastAPI for real-time analytics visualization
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from typing import Dict, List, Optional
import json

# Page configuration
st.set_page_config(
    page_title="Sports Performance Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

class APIClient:
    """Client for interacting with the FastAPI backend."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def get_player(self, player_id: int) -> Optional[Dict]:
        """Get player data by ID."""
        try:
            response = requests.get(f"{self.base_url}/players/{player_id}")
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def get_top_rankings(self, k: int = 20) -> List[Dict]:
        """Get top K player rankings."""
        try:
            response = requests.get(f"{self.base_url}/rankings/top/{k}")
            return response.json() if response.status_code == 200 else []
        except:
            return []
    
    def get_similar_players(self, player_id: int, method: str = "cosine", top_k: int = 10) -> List[Dict]:
        """Get similar players."""
        try:
            response = requests.get(
                f"{self.base_url}/players/{player_id}/similar",
                params={"method": method, "top_k": top_k}
            )
            return response.json() if response.status_code == 200 else []
        except:
            return []
    
    def predict_performance(self, player_id: int, model: str = "random_forest") -> Optional[Dict]:
        """Get performance prediction."""
        try:
            response = requests.get(
                f"{self.base_url}/players/{player_id}/predict",
                params={"model": model}
            )
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def get_system_stats(self) -> Optional[Dict]:
        """Get system statistics."""
        try:
            response = requests.get(f"{self.base_url}/system/stats")
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def create_player(self, player_data: Dict) -> Optional[Dict]:
        """Create a new player."""
        try:
            response = requests.post(f"{self.base_url}/players", json=player_data)
            return response.json() if response.status_code == 200 else None
        except:
            return None

# Initialize API client
api_client = APIClient(API_BASE_URL)

def main():
    """Main dashboard application."""
    st.title("Dynamic Sports Performance Analytics Dashboard")
    st.markdown("Real-time soccer player analytics with optimized data structures and algorithms")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Overview", "Player Rankings", "Player Search", "Similarity Analysis", "Performance Prediction", "System Monitoring", "Add Player"]
    )
    
    # Check API connection
    system_stats = api_client.get_system_stats()
    if system_stats:
        st.sidebar.success("API Connected")
        st.sidebar.metric("Total Players", system_stats.get("total_players", 0))
        st.sidebar.metric("Load Factor", f"{system_stats.get('hash_table_load_factor', 0):.3f}")
    else:
        st.sidebar.error("API Disconnected")
        st.error("Cannot connect to the API. Please ensure the FastAPI server is running on http://localhost:8000")
        return
    
    # Route to appropriate page
    if page == "Overview":
        show_overview_page(system_stats)
    elif page == "Player Rankings":
        show_rankings_page()
    elif page == "Player Search":
        show_player_search_page()
    elif page == "Similarity Analysis":
        show_similarity_page()
    elif page == "Performance Prediction":
        show_prediction_page()
    elif page == "System Monitoring":
        show_system_monitoring_page(system_stats)
    elif page == "Add Player":
        show_add_player_page()

def show_overview_page(system_stats: Dict):
    """Show overview dashboard."""
    st.header("System Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", system_stats.get("total_players", 0))
    
    with col2:
        st.metric("Hash Table Load", f"{system_stats.get('hash_table_load_factor', 0):.1%}")
    
    with col3:
        st.metric("Heap Size", system_stats.get("heap_size", 0))
    
    with col4:
        st.metric("Graph Nodes", system_stats.get("graph_nodes", 0))
    
    # Top performers preview
    st.subheader("Top 10 Performers")
    top_players = api_client.get_top_rankings(10)
    
    if top_players:
        df = pd.DataFrame([
            {
                "Rank": player["rank"],
                "Name": player["player"]["name"],
                "Position": player["player"]["position"],
                "Score": round(player["score"], 2),
                "Age": player["player"]["age"]
            }
            for player in top_players
        ])
        
        st.dataframe(df, use_container_width=True)
        
        # Performance distribution chart
        fig = px.bar(
            df, 
            x="Name", 
            y="Score", 
            color="Position",
            title="Top 10 Player Performance Scores"
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No player data available")

def show_rankings_page():
    """Show player rankings page."""
    st.header("Player Rankings")
    
    # Controls
    col1, col2 = st.columns([1, 3])
    
    with col1:
        num_players = st.slider("Number of players", 5, 50, 20)
        position_filter = st.selectbox("Filter by position", ["All", "Goalkeeper", "Defender", "Midfielder", "Attacker"])
    
    # Get rankings
    rankings = api_client.get_top_rankings(num_players)
    
    if rankings:
        # Filter by position if selected
        if position_filter != "All":
            rankings = [r for r in rankings if r["player"]["position"] == position_filter]
        
        # Create DataFrame
        df = pd.DataFrame([
            {
                "Rank": player["rank"],
                "Name": player["player"]["name"],
                "Position": player["player"]["position"],
                "Team ID": player["player"]["team_id"],
                "Age": player["player"]["age"],
                "Performance Score": round(player["score"], 2),
                "Goals": player["player"]["stats"].get("goals", 0),
                "Assists": player["player"]["stats"].get("assists", 0),
                "Pass Accuracy": round(player["player"]["stats"].get("pass_accuracy", 0), 1),
                "Average Rating": round(player["player"]["stats"].get("average_rating", 0), 1)
            }
            for player in rankings
        ])
        
        # Display table
        st.dataframe(df, use_container_width=True)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution by position
            fig = px.box(
                df, 
                x="Position", 
                y="Performance Score",
                title="Performance Score Distribution by Position"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Age vs Performance
            fig = px.scatter(
                df, 
                x="Age", 
                y="Performance Score",
                color="Position",
                size="Goals",
                hover_data=["Name"],
                title="Age vs Performance Score"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No ranking data available")

def show_player_search_page():
    """Show player search and details page."""
    st.header("Player Search")
    
    # Get all players for search
    rankings = api_client.get_top_rankings(100)  # Get more players for search
    
    if rankings:
        player_options = {f"{p['player']['name']} (ID: {p['player']['player_id']})": p['player']['player_id'] 
                         for p in rankings}
        
        selected_player = st.selectbox("Select a player", list(player_options.keys()))
        
        if selected_player:
            player_id = player_options[selected_player]
            player_data = api_client.get_player(player_id)
            
            if player_data:
                # Player info
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Name", player_data["name"])
                    st.metric("Position", player_data["position"])
                
                with col2:
                    st.metric("Age", player_data["age"])
                    st.metric("Team ID", player_data["team_id"])
                
                with col3:
                    st.metric("Performance Score", round(player_data["performance_score"], 2))
                    st.metric("Last Updated", time.strftime('%Y-%m-%d %H:%M', time.localtime(player_data["last_updated"])))
                
                # Detailed stats
                st.subheader("Detailed Statistics")
                stats_df = pd.DataFrame([
                    {"Statistic": k.replace("_", " ").title(), "Value": v}
                    for k, v in player_data["stats"].items()
                ])
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.dataframe(stats_df, use_container_width=True)
                
                with col2:
                    # Radar chart of key stats
                    key_stats = ["goals", "assists", "pass_accuracy", "average_rating"]
                    values = [player_data["stats"].get(stat, 0) for stat in key_stats]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=[stat.replace("_", " ").title() for stat in key_stats],
                        fill='toself',
                        name=player_data["name"]
                    ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, max(values) * 1.1])
                        ),
                        title="Player Performance Radar"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)

def show_similarity_page():
    """Show player similarity analysis page."""
    st.header("Player Similarity Analysis")
    
    # Get players for selection
    rankings = api_client.get_top_rankings(50)
    
    if rankings:
        player_options = {f"{p['player']['name']} (ID: {p['player']['player_id']})": p['player']['player_id'] 
                         for p in rankings}
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_player = st.selectbox("Select a player to find similar players", list(player_options.keys()))
        
        with col2:
            similarity_method = st.selectbox("Similarity method", ["cosine", "euclidean", "cluster"])
            num_similar = st.slider("Number of similar players", 3, 20, 10)
        
        if selected_player:
            player_id = player_options[selected_player]
            similar_players = api_client.get_similar_players(player_id, similarity_method, num_similar)
            
            if similar_players:
                st.subheader(f"Players similar to {selected_player.split(' (')[0]}")
                
                # Create DataFrame
                df = pd.DataFrame([
                    {
                        "Rank": i + 1,
                        "Name": sp["player_details"]["name"] if sp["player_details"] else "Unknown",
                        "Position": sp["player_details"]["position"] if sp["player_details"] else "Unknown",
                        "Similarity Score": round(sp["similarity_score"], 3),
                        "Performance Score": round(sp["player_details"]["performance_score"], 2) if sp["player_details"] else 0
                    }
                    for i, sp in enumerate(similar_players)
                ])
                
                st.dataframe(df, use_container_width=True)
                
                # Similarity score visualization
                fig = px.bar(
                    df, 
                    x="Name", 
                    y="Similarity Score",
                    color="Position",
                    title=f"Similarity Scores ({similarity_method} method)"
                )
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No similar players found or insufficient data for similarity analysis")

def show_prediction_page():
    """Show performance prediction page."""
    st.header("Performance Prediction")
    
    # Get players for selection
    rankings = api_client.get_top_rankings(50)
    
    if rankings:
        player_options = {f"{p['player']['name']} (ID: {p['player']['player_id']})": p['player']['player_id'] 
                         for p in rankings}
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_player = st.selectbox("Select a player for prediction", list(player_options.keys()))
        
        with col2:
            model_type = st.selectbox("Prediction model", ["random_forest", "linear_regression"])
        
        if selected_player:
            player_id = player_options[selected_player]
            prediction = api_client.predict_performance(player_id, model_type)
            
            if prediction:
                st.subheader(f"Performance Prediction for {selected_player.split(' (')[0]}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Predicted Score", round(prediction["prediction"], 2))
                
                with col2:
                    st.metric("Confidence", f"{prediction['confidence']:.1%}")
                
                with col3:
                    st.metric("Model Used", prediction["model_used"])
                
                # Get current player data for comparison
                current_data = api_client.get_player(player_id)
                if current_data:
                    current_score = current_data["performance_score"]
                    predicted_score = prediction["prediction"]
                    
                    # Comparison chart
                    comparison_df = pd.DataFrame({
                        "Period": ["Current Season", "Predicted Next Season"],
                        "Performance Score": [current_score, predicted_score]
                    })
                    
                    fig = px.bar(
                        comparison_df,
                        x="Period",
                        y="Performance Score",
                        title="Current vs Predicted Performance",
                        color="Period"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Prediction insights
                    change = predicted_score - current_score
                    if change > 0:
                        st.success(f"Predicted improvement of {change:.2f} points ({change/current_score:.1%})")
                    elif change < 0:
                        st.warning(f"Predicted decline of {abs(change):.2f} points ({abs(change)/current_score:.1%})")
                    else:
                        st.info("Predicted to maintain current performance level")
            else:
                st.error("Unable to generate prediction. Insufficient data or model not trained.")

def show_system_monitoring_page(system_stats: Dict):
    """Show system monitoring and performance page."""
    st.header("System Monitoring")
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", system_stats.get("total_players", 0))
    
    with col2:
        st.metric("Hash Table Load Factor", f"{system_stats.get('hash_table_load_factor', 0):.3f}")
    
    with col3:
        st.metric("Heap Size", system_stats.get("heap_size", 0))
    
    with col4:
        st.metric("Graph Nodes", system_stats.get("graph_nodes", 0))
    
    # Performance metrics
    st.subheader("Data Structure Performance")
    
    performance_data = {
        "Component": ["Hash Table", "Max Heap", "Graph"],
        "Time Complexity (Lookup)": ["O(1)", "O(1)", "O(V + E)"],
        "Time Complexity (Insert)": ["O(1)", "O(log n)", "O(1)"],
        "Space Complexity": ["O(n)", "O(n)", "O(V + E)"],
        "Current Load": [
            f"{system_stats.get('hash_table_load_factor', 0):.1%}",
            f"{system_stats.get('heap_size', 0)}/200",
            f"{system_stats.get('graph_nodes', 0)} nodes"
        ]
    }
    
    performance_df = pd.DataFrame(performance_data)
    st.dataframe(performance_df, use_container_width=True)
    
    # API health check
    st.subheader("API Health")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            st.success("API is healthy")
            st.json(health_data)
        else:
            st.error("API health check failed")
    except:
        st.error("Cannot reach API health endpoint")

def show_add_player_page():
    """Show add player page."""
    st.header("Add New Player")
    
    with st.form("add_player_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            player_id = st.number_input("Player ID", min_value=1, value=1000)
            name = st.text_input("Player Name")
            position = st.selectbox("Position", ["Goalkeeper", "Defender", "Midfielder", "Attacker"])
            team_id = st.number_input("Team ID", min_value=1, value=9)
            age = st.number_input("Age", min_value=16, max_value=45, value=25)
        
        with col2:
            st.subheader("Statistics")
            goals = st.number_input("Goals", min_value=0.0, value=0.0)
            assists = st.number_input("Assists", min_value=0.0, value=0.0)
            pass_accuracy = st.number_input("Pass Accuracy (%)", min_value=0.0, max_value=100.0, value=80.0)
            shots_total = st.number_input("Total Shots", min_value=0.0, value=0.0)
            tackles_won = st.number_input("Tackles Won", min_value=0.0, value=0.0)
            interceptions = st.number_input("Interceptions", min_value=0.0, value=0.0)
            key_passes = st.number_input("Key Passes", min_value=0.0, value=0.0)
            minutes_played = st.number_input("Minutes Played", min_value=0.0, value=0.0)
            average_rating = st.number_input("Average Rating", min_value=0.0, max_value=10.0, value=6.0)
        
        submitted = st.form_submit_button("Add Player")
        
        if submitted:
            player_data = {
                "player_id": player_id,
                "name": name,
                "position": position,
                "team_id": team_id,
                "age": age,
                "stats": {
                    "goals": goals,
                    "assists": assists,
                    "pass_accuracy": pass_accuracy,
                    "shots_total": shots_total,
                    "tackles_won": tackles_won,
                    "interceptions": interceptions,
                    "key_passes": key_passes,
                    "minutes_played": minutes_played,
                    "average_rating": average_rating
                }
            }
            
            result = api_client.create_player(player_data)
            
            if result:
                st.success(f"Player {name} added successfully with performance score: {result['performance_score']:.2f}")
                st.json(result)
            else:
                st.error("Failed to add player. Please check the data and try again.")

if __name__ == "__main__":
    main()
