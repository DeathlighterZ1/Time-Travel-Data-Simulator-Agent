# Time-Travel Data Simulator

This application simulates historical reconstructions or future predictions based on user-input timeframes, locations, and topics using AI-driven data analysis.

## Features

- Simulate past or future scenarios for different locations
- Interactive visualizations of predictions or reconstructions
- Support for climate, population, land use, and natural events data
- Real data from NASA and Open-Meteo APIs when available
- Interactive map for location selection

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a .env file with your NASA API key (optional):
   ```
   NASA_API_KEY=your_api_key_here
   ```

3. Run the application with Streamlit:
   ```
   streamlit run streamlit_app.py
   ```

## Usage

1. Enter a location (city, country) or select on the map
2. Select a year (1900-2100) using the slider
3. Choose a data type (climate, population, land use, natural events)
4. Click "Simulate" to generate visualizations

## Data Sources

- Climate data: Open-Meteo API (1940-present), NASA POWER API (1981-present), and simulated data
- Population data: Simplified growth models
- Land use data: Simulated urban, forest, and agricultural distributions
- Natural events: NASA EONET API (recent events) and simulated historical data

