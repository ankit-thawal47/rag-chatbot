#!/bin/bash

# RAG Document Management System - Development Setup Script
# Run this script to set up your development environment

echo "🚀 Setting up RAG Document Management System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.9+ and try again."
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js is not installed. Please install Node.js 18+ and try again."
        exit 1
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Install requirements
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Copy environment template
    if [ ! -f .env ]; then
        print_status "Creating environment file from template..."
        cp .env.template .env
        print_warning "Please edit backend/.env with your API keys and configuration"
    else
        print_warning "backend/.env already exists. Please verify your configuration."
    fi
    
    cd ..
    print_success "Backend setup complete!"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install npm dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Copy environment template
    if [ ! -f .env.local ]; then
        print_status "Creating environment file from template..."
        cp .env.local.template .env.local
        print_warning "Please edit frontend/.env.local with your Firebase configuration"
    else
        print_warning "frontend/.env.local already exists. Please verify your configuration."
    fi
    
    cd ..
    print_success "Frontend setup complete!"
}

# Main setup function
main() {
    echo ""
    echo "======================================"
    echo "  RAG Document Management System"
    echo "  Development Environment Setup"
    echo "======================================"
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    check_python
    check_node
    echo ""
    
    # Setup backend
    setup_backend
    echo ""
    
    # Setup frontend
    setup_frontend
    echo ""
    
    # Final instructions
    echo "======================================"
    echo "🎉 Setup Complete!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Configure your environment variables:"
    echo "   - Edit backend/.env with your API keys"
    echo "   - Edit frontend/.env.local with your Firebase config"
    echo ""
    echo "2. Set up external services:"
    echo "   - Firebase (Authentication)"
    echo "   - Google Cloud Storage"
    echo "   - Supabase (Database)"
    echo "   - Pinecone (Vector Database)"
    echo "   - OpenAI (API Key)"
    echo ""
    echo "3. Run the database setup:"
    echo "   - Go to Supabase SQL Editor"
    echo "   - Execute the contents of database/schema.sql"
    echo ""
    echo "4. Start the development servers:"
    echo ""
    echo "   Backend:"
    echo "   cd backend"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "   source venv/Scripts/activate"
    else
        echo "   source venv/bin/activate"
    fi
    echo "   uvicorn main:app --reload"
    echo ""
    echo "   Frontend (in another terminal):"
    echo "   cd frontend"
    echo "   npm run dev"
    echo ""
    echo "5. Visit http://localhost:3000 to start using the app!"
    echo ""
    echo "📚 For detailed setup instructions, see:"
    echo "   - README.md (overview)"
    echo "   - database/setup_instructions.md (database setup)"
    echo "   - DEPLOYMENT.md (deployment guide)"
    echo ""
}

# Run main function
main