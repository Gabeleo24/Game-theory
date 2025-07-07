# ADS599 Capstone Setup Scripts

This directory contains setup scripts for the ADS599 Capstone Soccer Intelligence System.

## Scripts Overview

### `codespace_installation.sh`
**Primary installation script for GitHub Codespaces**

This script performs a complete setup of the Soccer Intelligence System in a GitHub Codespace environment, including:

- ✅ Docker and Docker Compose configuration
- ✅ Python dependencies installation
- ✅ Project directory structure creation
- ✅ Environment configuration
- ✅ Database and cache services setup
- ✅ Jupyter Lab configuration
- ✅ Management scripts creation

**Usage:**
```bash
bash scripts/setup/codespace_installation.sh
```

**Requirements:**
- GitHub Codespace environment
- Internet connection for downloading dependencies

### `local_macos_installation.sh`
**Installation script for local macOS development**

This script sets up the Soccer Intelligence System on macOS for local development, including:

- ✅ Homebrew package manager setup
- ✅ Docker Desktop installation and configuration
- ✅ Python dependencies via pip
- ✅ Local project structure creation
- ✅ Local environment configuration
- ✅ Local Docker Compose overrides
- ✅ Local management scripts

**Usage:**
```bash
bash scripts/setup/local_macos_installation.sh
```

**Requirements:**
- macOS system
- Internet connection for downloading dependencies
- Admin privileges for Homebrew installation

### `verify_codespace.sh`
**Installation verification script for GitHub Codespaces**

This script verifies that the Codespace installation was successful by checking:

- ✅ Docker installation and service status
- ✅ Python and required packages
- ✅ Project directory structure
- ✅ Configuration files
- ✅ Management scripts
- ✅ API configuration

**Usage:**
```bash
bash scripts/setup/verify_codespace.sh
```

### `verify_local_macos.sh`
**Installation verification script for local macOS**

This script verifies that the local macOS installation was successful by checking:

- ✅ Homebrew installation
- ✅ Docker Desktop installation and status
- ✅ Python and required packages
- ✅ Project directory structure
- ✅ Local configuration files
- ✅ Local management scripts
- ✅ API configuration

**Usage:**
```bash
bash scripts/setup/verify_local_macos.sh
```

## Quick Start Guide

### For GitHub Codespaces

#### 1. Initial Setup
Run the main installation script in your GitHub Codespace:

```bash
bash scripts/setup/codespace_installation.sh
```

### For Local macOS Development

#### 1. Initial Setup
Run the macOS installation script on your local Mac:

```bash
bash scripts/setup/local_macos_installation.sh
```

#### 2. Start Docker Desktop
Ensure Docker Desktop is running before proceeding.

### Common Steps (Both Environments)

#### 2. Set API Key (Required)

**For GitHub Codespaces:**
1. Go to your GitHub repository settings
2. Navigate to "Secrets and variables" > "Codespaces"
3. Add a new secret:
   - Name: `SPORTMONKS_API_KEY`
   - Value: Your SportMonks API key

**For Local macOS:**
1. Edit `config/api_keys.yaml`
2. Replace `your_api_key_here` with your actual SportMonks API key

#### 3. Start Services

**For GitHub Codespaces:**
```bash
# Start all services
./start_codespace.sh

# Check service status
./status_codespace.sh

# Stop all services
./stop_codespace.sh
```

**For Local macOS:**
```bash
# Start all services
./start_local.sh

# Check service status
./status_local.sh

# Stop all services
./stop_local.sh
```

#### 4. Access Services

**GitHub Codespaces:**
- **Jupyter Lab**: `https://[CODESPACE_NAME]-8888.app.github.dev`
  - Token: `codespace_secure_token_2024`
- **pgAdmin**: `https://[CODESPACE_NAME]-8080.app.github.dev`
  - Email: `admin@admin.com`
  - Password: `admin`

**Local macOS:**
- **Jupyter Lab**: `http://localhost:8888`
  - Token: `local_secure_token_2024`
- **pgAdmin**: `http://localhost:8080`
  - Email: `admin@admin.com`
  - Password: `admin`

## Troubleshooting

### Installation Fails
1. **Docker Issues**: Ensure Docker is running in the Codespace
   ```bash
   docker info
   ```

2. **Permission Issues**: Some operations may require sudo
   ```bash
   sudo service docker start
   ```

3. **Network Issues**: Check internet connectivity for package downloads

### Services Won't Start
1. **Check Docker Compose files**:
   ```bash
   ls -la docker-compose*.yml
   ```

2. **Check logs**:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.codespace.yml logs
   ```

3. **Restart Docker**:
   ```bash
   sudo service docker restart
   ```

### Verification Fails
Run the verification script to identify issues:
```bash
bash scripts/setup/verify_codespace.sh
```

## File Structure After Installation

```
ADS599_Capstone/
├── scripts/setup/
│   ├── codespace_installation.sh    # Main installation script
│   ├── verify_codespace.sh          # Verification script
│   └── README.md                    # This file
├── docker-compose.yml               # Base Docker configuration
├── docker-compose.codespace.yml     # Codespace-specific overrides
├── .env.codespace                   # Codespace environment variables
├── start_codespace.sh               # Start services script
├── stop_codespace.sh                # Stop services script
├── status_codespace.sh              # Check status script
├── data/                            # Data directories
├── logs/                            # Log directories
├── notebooks/                       # Jupyter notebooks
└── config/                          # Configuration files
```

## Environment Variables

The installation creates several environment files:

### `.env.codespace`
Contains Codespace-specific configuration:
- Database connection settings
- Redis configuration
- Performance tuning parameters

### Codespace Secrets
Set these as GitHub Codespace secrets:
- `SPORTMONKS_API_KEY`: Your SportMonks API key

## Support

If you encounter issues:

1. **Check the verification script output**
2. **Review Docker logs**
3. **Ensure all required files are present**
4. **Verify API key configuration**

For additional help, refer to the main project documentation or contact the development team.
