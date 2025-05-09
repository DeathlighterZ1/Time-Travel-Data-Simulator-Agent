import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
import datetime
from dotenv import load_dotenv

# Load API keys from Streamlit secrets
NASA_API_KEY = st.secrets.get("NASA_API_KEY", "DEMO_KEY")

# Define TimeSimulator class directly in this file
class TimeSimulator:
    def __init__(self):
        self.data_sources = {
            "climate": self.get_climate_data,
            "population": self.get_population_data,
            "land_use": self.get_land_use_data,
            "natural_events": self.get_natural_events
        }
    
    def get_climate_data(self, location, year):
        try:
            # For historical data (Open-Meteo has data from 1940 to now)
            if year <= 2023 and year >= 1940:
                st.write(f"Attempting to fetch climate data from Open-Meteo API for {location}, {year}...")
                # Parse location (simplified)
                # In production, use geocoding API
                lat, lon = 40.7128, -74.0060  # Default to NYC coordinates
                
                # Open-Meteo API for historical temperature data
                start_date = f"{year}-01-01"
                end_date = f"{year}-12-31"
                meteo_url = f"https://archive-api.open-meteo.com/v1/archive"
                params = {
                    "latitude": lat,
                    "longitude": lon,
                    "start_date": start_date,
                    "end_date": end_date,
                    "daily": "temperature_2m_mean",
                    "timezone": "auto"
                }
                
                response = requests.get(meteo_url, params=params)
                if response.status_code == 200:
                    st.success("Open-Meteo API: Data retrieved successfully")
                    data = response.json()
                    # Calculate annual average temperature
                    temps = data.get('daily', {}).get('temperature_2m_mean', [])
                    if temps:
                        # Filter out None values
                        valid_temps = [t for t in temps if t is not None]
                        avg_temp = sum(valid_temps) / len(valid_temps) if valid_temps else 15
                        return {"temperature": avg_temp}
                    else:
                        st.error("Open-Meteo API: No temperature data returned")
                else:
                    st.error(f"Open-Meteo API: Failed with status code {response.status_code}")
            
            # Fallback to simulation
            st.info("Using fallback climate data simulation")
            return self._fallback_climate_data(location, year)
        except Exception as e:
            st.error(f"API error: {str(e)}, using fallback data")
            return self._fallback_climate_data(location, year)
        
    def _fallback_climate_data(self, location, year):
        # Existing simulation logic as fallback
        if year > 2023:  # Future prediction
            base_temp = 15 + np.random.normal(0, 2)
            # Assume warming trend
            predicted_temp = base_temp + (year - 2023) * 0.03
            return {"temperature": predicted_temp}
        else:  # Historical data
            # Simplified historical climate model
            base_temp = 14 + np.random.normal(0, 3)
            return {"temperature": base_temp}
    
    def get_population_data(self, location, year):
        # Simplified population model
        base_pop = 1000000 * np.random.uniform(0.5, 5)
        if year > 2023:
            # Exponential growth model
            growth_rate = 1.01
            years_from_now = year - 2023
            predicted_pop = base_pop * (growth_rate ** years_from_now)
            return {"population": predicted_pop}
        else:
            # Historical population (simplified)
            growth_factor = (year - 1900) / 123 if year > 1900 else 0.1
            historical_pop = base_pop * growth_factor
            return {"population": max(10000, historical_pop)}
    
    def get_land_use_data(self, location, year):
        # Simplified land use model
        if year > 2023:
            urban = min(0.8, 0.3 + (year - 2023) * 0.01)
            forest = max(0.1, 0.3 - (year - 2023) * 0.005)
            agriculture = 1 - urban - forest
        else:
            urban = max(0.05, min(0.3, (year - 1900) * 0.002))
            forest = max(0.2, min(0.6, 0.6 - (year - 1900) * 0.001))
            agriculture = 1 - urban - forest
            
        return {
            "urban": urban,
            "forest": forest, 
            "agriculture": agriculture
        }
    
    def get_natural_events(self, location, year):
        """Get natural events data from NASA EONET API"""
        # Only works for recent years (typically last 120 days)
        if year >= 2023:
            try:
                st.write(f"Attempting to fetch natural events data from NASA EONET API...")
                eonet_url = "https://eonet.gsfc.nasa.gov/api/v3/events"
                params = {
                    "api_key": NASA_API_KEY,
                    "status": "open"  # Get currently active events
                }
                
                response = requests.get(eonet_url, params=params)
                if response.status_code == 200:
                    st.success("NASA EONET API: Data retrieved successfully")
                    events_data = response.json()
                    # Filter and process events
                    events = events_data.get('events', [])
                    event_counts = {
                        "wildfires": 0,
                        "storms": 0,
                        "floods": 0,
                        "drought": 0,
                        "other": 0
                    }
                    
                    for event in events:
                        category = event.get('categories', [{}])[0].get('id', 'other')
                        if category == 'wildfires':
                            event_counts['wildfires'] += 1
                        elif category in ['severeStorms', 'volcanoes']:
                            event_counts['storms'] += 1
                        elif category == 'floods':
                            event_counts['floods'] += 1
                        elif category == 'drought':
                            event_counts['drought'] += 1
                        else:
                            event_counts['other'] += 1
                    
                    return event_counts
                else:
                    st.error(f"NASA EONET API: Failed with status code {response.status_code}")
            except Exception as e:
                st.error(f"EONET API error: {str(e)}")
        
        # Fallback or historical simulation
        st.info("Using simulated natural events data")
        return {
            "wildfires": int(np.random.poisson(3 + (year - 2000) * 0.1 if year > 2000 else 1)),
            "storms": int(np.random.poisson(5 + (year - 2000) * 0.05 if year > 2000 else 2)),
            "floods": int(np.random.poisson(2 + (year - 2000) * 0.03 if year > 2000 else 1)),
            "drought": int(np.random.poisson(1 + (year - 2000) * 0.02 if year > 2000 else 0)),
            "other": int(np.random.poisson(2))
        }
    
    def simulate(self, location, year, data_type):
        if data_type in self.data_sources:
            return self.data_sources[data_type](location, year)
        return {"error": "Data type not supported"}

# Function to test API connections
def test_apis():
    """Test API connections and display status"""
    # Test NASA API
    try:
        test_url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
        response = requests.get(test_url)
        if response.status_code == 200:
            return "NASA API: Connected successfully"
        else:
            return f"NASA API: Connection failed (Status code: {response.status_code})"
    except Exception as e:
        return f"NASA API: Connection error - {str(e)}"

# Page config
st.set_page_config(
    page_title="Time-Travel Data Simulator",
    page_icon="🌍",
    layout="wide"
)

# Title and description
st.title("Time-Travel Data Simulator")
st.markdown("Simulate historical reconstructions or future predictions based on user-input timeframes, locations, and topics.")

# Test APIs and show status
if st.sidebar.checkbox("Show API Status", value=False):
    st.sidebar.subheader("API Connection Status")
    
    # Test NASA API
    try:
        test_url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
        response = requests.get(test_url)
        if response.status_code == 200:
            st.sidebar.success("NASA API: Connected successfully")
        else:
            st.sidebar.error(f"NASA API: Connection failed (Status code: {response.status_code})")
    except Exception as e:
        st.sidebar.error(f"NASA API: Connection error - {str(e)}")
    
    # Test Open-Meteo API
    try:
        test_url = "https://archive-api.open-meteo.com/v1/archive?latitude=40.71&longitude=-74.01&start_date=2023-01-01&end_date=2023-01-02&daily=temperature_2m_mean"
        response = requests.get(test_url)
        if response.status_code == 200:
            st.sidebar.success("Open-Meteo API: Connected successfully")
        else:
            st.sidebar.error(f"Open-Meteo API: Connection failed (Status code: {response.status_code})")
    except Exception as e:
        st.sidebar.error(f"Open-Meteo API: Connection error - {str(e)}")

# Create columns for inputs
col1, col2, col3 = st.columns(3)

with col1:
    location = st.text_input("Location (City, Country)", "New York, USA")
    
with col2:
    year = st.slider("Year", min_value=1900, max_value=2100, value=2023, step=1)
    
with col3:
    data_type = st.selectbox(
        "Data Type",
        options=["climate", "population", "land_use", "natural_events"],
        index=0
    )

# Create a map for location selection
st.sidebar.subheader("Location Selection")
st.sidebar.markdown("Click on the map to select a location or use the text input above.")

# Default coordinates (New York)
default_lat, default_lon = 40.7128, -74.0060

# Create a map centered at the default location
m = folium.Map(location=[default_lat, default_lon], zoom_start=4)
folium.Marker([default_lat, default_lon], tooltip="New York").add_to(m)

# Display the map
with st.sidebar:
    folium_static(m)

# Simulate button
if st.button("Simulate", type="primary"):
    # Show a spinner while processing
    with st.spinner("Simulating data..."):
        # Create simulator instance
        simulator = TimeSimulator()
        
        # Get data
        data = simulator.simulate(location, year, data_type)
        
        # Display results based on data type
        if data_type == "climate":
            st.subheader(f"Climate Simulation for {location} in {year}")
            
            # Create temperature visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(["Temperature"], [data["temperature"]], color="orange", width=0.4)
            ax.set_ylabel("Temperature (°C)")
            ax.set_title(f"Simulated Temperature")
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Display the plot
            st.pyplot(fig)
            
            # Display additional information
            st.info(f"The average temperature in {location} for {year} is projected to be {data['temperature']:.2f}°C.")
            
        elif data_type == "population":
            st.subheader(f"Population Simulation for {location} in {year}")
            
            # Create population visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(["Population"], [data["population"]], color="blue", width=0.4)
            ax.set_ylabel("Population")
            ax.set_title(f"Simulated Population")
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Format y-axis with commas for thousands
            ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
            
            # Display the plot
            st.pyplot(fig)
            
            # Display additional information
            st.info(f"The estimated population of {location} in {year} is {int(data['population']):,} people.")
            
        elif data_type == "land_use":
            st.subheader(f"Land Use Simulation for {location} in {year}")
            
            # Create land use visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            labels = ["Urban", "Forest", "Agriculture"]
            values = [data["urban"], data["forest"], data["agriculture"]]
            colors = ["#FF9999", "#66B2FF", "#99FF99"]
            
            ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            ax.set_title(f"Simulated Land Use Distribution")
            
            # Display the plot
            st.pyplot(fig)
            
            # Display additional information
            st.info(f"""
            Land use distribution for {location} in {year}:
            - Urban areas: {data['urban']*100:.1f}%
            - Forest areas: {data['forest']*100:.1f}%
            - Agricultural areas: {data['agriculture']*100:.1f}%
            """)
            
        elif data_type == "natural_events":
            st.subheader(f"Natural Events Simulation for {location} in {year}")
            
            # Create natural events visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            events = list(data.keys())
            counts = list(data.values())
            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFBE0B", "#9D80CB"]
            
            bars = ax.bar(events, counts, color=colors)
            ax.set_ylabel("Event Count")
            ax.set_title("Simulated Natural Events")
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')
            
            # Display the plot
            st.pyplot(fig)
            
            # Display additional information
            st.info(f"""
            Predicted natural events for {location} in {year}:
            - Wildfires: {data['wildfires']}
            - Storms: {data['storms']}
            - Floods: {data['floods']}
            - Droughts: {data['drought']}
            - Other events: {data['other']}
            """)

# Add information about the data sources
st.sidebar.subheader("Data Sources")
st.sidebar.markdown("""
- Climate data: Open-Meteo API (1940-present), NASA POWER API (1981-present)
- Population data: Simplified growth models
- Land use data: Simulated urban, forest, and agricultural distributions
- Natural events: NASA EONET API (recent events)
""")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2023 Time-Travel Data Simulator")


