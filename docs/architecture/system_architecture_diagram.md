# System Architecture Diagram

This document contains the visual representation of the ADS599 Capstone Soccer Intelligence System architecture.

## Architecture Overview

The system is built with a layered architecture approach, consisting of 5 main layers that work together to provide a comprehensive soccer intelligence platform.

## Visual Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI["Command Line Interface<br/>./run_sql_with_logs.sh<br/>./show_database_structure.sh"]
        DIRECT["Direct SQL Access<br/>docker exec -it postgres psql"]
    end
    
    subgraph "Application Layer"
        LOGGER["SQL Logger<br/>scripts/sql_logging/sql_logger.py<br/>- Query execution<br/>- Result formatting<br/>- Automatic logging"]
        
        QUERIES["Pre-built Queries<br/>common_queries_with_logging.py<br/>- Player analysis<br/>- Team analysis<br/>- Match analysis"]
        
        LOADER["Data Loaders<br/>scripts/data_loading/<br/>- JSON to PostgreSQL<br/>- Batch processing<br/>- Error handling"]
    end
    
    subgraph "Infrastructure Layer"
        DOCKER["Docker Compose<br/>Multi-service orchestration<br/>- PostgreSQL database<br/>- Redis cache<br/>- Application containers"]
        
        POSTGRES["PostgreSQL Database<br/>Performance optimized<br/>- 9 tables with relationships<br/>- Strategic indexes<br/>- Foreign key constraints"]
        
        REDIS["Redis Cache<br/>High-speed caching<br/>- Query result cache<br/>- Session management"]
    end
    
    subgraph "Data Layer"
        JSON["JSON Data Files<br/>data/focused/<br/>- 67 Champions League teams<br/>- 3,980 players<br/>- 8,080 player statistics"]
        
        LOGS["SQL Logs<br/>logs/sql_logs/<br/>- Query history<br/>- Formatted results<br/>- INSERT statements"]
    end
    
    subgraph "Configuration Layer"
        SCHEMA["Database Schema<br/>docker/postgres/init.sql<br/>- Table definitions<br/>- Indexes<br/>- Constraints"]
        
        CONFIG["Docker Config<br/>docker-compose.yml<br/>- Service definitions<br/>- Resource allocation<br/>- Network configuration"]
    end
    
    CLI --> LOGGER
    CLI --> QUERIES
    DIRECT --> POSTGRES
    
    LOGGER --> POSTGRES
    QUERIES --> LOGGER
    LOADER --> POSTGRES
    
    DOCKER --> POSTGRES
    DOCKER --> REDIS
    
    POSTGRES --> LOGS
    JSON --> LOADER
    
    SCHEMA --> POSTGRES
    CONFIG --> DOCKER
    
    style CLI fill:#e1f5fe
    style LOGGER fill:#f3e5f5
    style POSTGRES fill:#e8f5e8
    style JSON fill:#fff3e0
```

## Layer Descriptions

### User Interface Layer
- **CLI Tools**: Command-line interfaces for easy system interaction
- **Direct Access**: Direct PostgreSQL connection for advanced database operations

### Application Layer
- **SQL Logger**: Automatic query logging with result formatting
- **Pre-built Queries**: Common analysis templates for quick insights
- **Data Loaders**: Efficient JSON to PostgreSQL data pipeline

### Infrastructure Layer
- **Docker Compose**: Multi-service orchestration and management
- **PostgreSQL**: High-performance database with optimized configuration
- **Redis**: High-speed caching layer for improved performance

### Data Layer
- **JSON Files**: Source data containing teams, players, and statistics
- **SQL Logs**: Query history and formatted results for analysis tracking

### Configuration Layer
- **Database Schema**: Table definitions, indexes, and constraints
- **Docker Config**: Service definitions and resource allocation

## Data Flow

1. **User Input** → CLI Tools → Application Layer
2. **JSON Data** → Data Loaders → PostgreSQL Database
3. **SQL Queries** → Logger → Database → Results → Log Files
4. **Configuration** → Infrastructure → Application Services

## Key Features

- **Performance Optimization**: Strategic indexing, caching, and resource allocation
- **Data Integrity**: Foreign key relationships and transaction safety
- **Developer Experience**: Automatic logging and pre-built analysis tools
- **Scalability**: Container-based architecture for easy scaling

## Related Files

- **Raw Mermaid File**: `system_architecture_diagram.mmd`
- **System Methodology**: `../../SYSTEM_ARCHITECTURE_METHODOLOGY.md`
- **SQL Guide**: `../../SQL_PLAYGROUND_GUIDE.md`
- **Docker Configuration**: `../../docker-compose.yml`
