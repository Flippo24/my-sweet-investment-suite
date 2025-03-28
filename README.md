# My Sweet Investment Suite

## Overview
My Sweet Investment Suite is a modern trading platform built with Python and PySide6. It offers a flexible, modular architecture that combines a customizable widget system with dynamic theming, real-time data integration, and a simulated broker environment. Designed to integrate with Interactive Brokers via an asynchronous API, this platform provides both live and simulated market data, making it a versatile tool for traders and developers alike.

## Key Features
- **Dynamic Theming & Custom UI:** 
  - A dedicated Theme Manager for loading, applying, and managing custom themes.
  - A robust widget system to build interactive, resizable, and movable UI elements.
  
- **Broker Integration & Simulation:**
  - Integrates with Interactive Brokers using asynchronous connections (via ib-async) for live trading and market data.
  - Includes a Simulator for testing and development without requiring a live broker connection.

- **Modular Architecture:**
  - Separates concerns with dedicated modules for settings, logging, data management, and workspace management.
  - Manages configurations with JSON for settings and Parquet for market data storage.

- **Asynchronous Data Handling:**
  - Leverages Python’s asyncio for real-time data subscriptions, historical data fetching, and concurrent operations.

## Development Status
> **Note:** This project is still in its early stages. Expect frequent updates, potential breaking changes, and ongoing improvements as new features are developed and the codebase is refined.

## Technologies Used
- **Programming Language:** Python
- **GUI Framework:** PySide6
- **Asynchronous Programming:** asyncio
- **Broker Integration:** ib-async (Interactive Brokers API)
- **Data Management:** JSON, Parquet

## Getting Started
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Flippo24/my-sweet-investment-suite.git
   cd my-sweet-investment-suite

## Run the Application
1. **Using uv to run the Application:**  
   ```bash
   uv run src/main.py
