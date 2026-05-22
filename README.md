# Demand and Supply Cognitive Control Tower

## Overview

The Demand and Supply Cognitive Control Tower is an advanced, AI-driven platform tailored for HVAC supply chain operations planning. It integrates various analytical, machine learning, and operational modules to provide a holistic view of the supply chain, enabling accurate demand forecasting, inventory allocation, financial analysis, and strategic optimization. 

The architecture is structured into a multi-layered system that covers data processing, business intelligence, analytics, autonomous agents, and a visual interface. 

## Key Components

1. HVAC Forecast System:
   Handles demand forecasting and inventory allocation.
   Leverages machine learning models for accurate prediction and handles complex cross-regional datasets.
   Provides insights and data to the downstream services to ensure reliable supply chain inventory management.

2. HVAC Control Tower (Backend):
   The core backend orchestration service built on a microservices-inspired architecture using FastAPI.
   Orchestrates the different layers of the supply chain (Sensing, Digital Twin, Intelligence, Policy/Optimization, Tower).
   Serves analytical data and manages the event bus for inter-service communication.
   Includes the Financial Copilot, an LLM-powered agent to answer financial queries, model what-if scenarios, and explain variances between budgets, forecasts, and actuals.

3. Planning Dashboard (Frontend):
   A visual analytics layer that provides coordinated multi-views and inline insights for executives and supply chain managers.
   Integrates the Financial Copilot chat interface for conversational Q&A based on real-time data.

## Project Structure

- hvac_forecast_system/ : Code and models for demand prediction and inventory planning.
- hvac_control_tower/ : FastAPI backend services, routing, agents, and data access layers.
- planning-dashboard/ : Frontend application for the visual control tower.
- data/ : Raw, processed, and output data for the forecast and control tower components.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js (for the frontend dashboard)
- PostgreSQL and Redis (for backend data storage and caching)

### Running the System

To start the system, you must start the individual services in order. Please refer to the specific documentation within each directory for exact startup commands, but generally:

1. Setup virtual environments and install requirements for Python services.
2. Ensure database services are running.
3. Start the forecasting service.
4. Start the control tower backend.
5. Start the planning dashboard frontend.
