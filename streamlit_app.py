"""
Rahalah Trip Planning Assistant - Streamlit Frontend
A simplified but powerful UI for the Rahalah Trip Planning system.
"""
import json
import os
import requests
from typing import Dict, List, Optional, Any, Union, Tuple

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_URL = "http://localhost:8000"
DEFAULT_MODE = "trip"

# Set page configuration
st.set_page_config(
    page_title="Rahalah - Your Saudi Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e6f3ff;
        border-left: 5px solid #2b6cb0;
    }
    .chat-message.assistant {
        background-color: #f0f4f8;
        border-left: 5px solid #4a5568;
    }
    .search-result {
        background-color: white;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .search-result-header {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .search-result-title {
        font-weight: bold;
        font-size: 1.1rem;
    }
    .search-result-price {
        color: #2b6cb0;
        font-weight: bold;
    }
    .stars {
        color: gold;
    }
    .info-label {
        font-weight: bold;
        color: #4a5568;
    }
    .amenities {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    .amenity-tag {
        background-color: #e2e8f0;
        padding: 0.2rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.8rem;
    }
    .bold-text {
        font-weight: bold;
    }
    .main-title {
        text-align: center;
        color: #2b6cb0;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def display_stars(rating: float) -> str:
    """Convert a numerical rating to star symbols.
    
    Args:
        rating: The numerical rating (typically 1-5)
        
    Returns:
        String of star symbols
    """
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    
    stars = "★" * full_stars
    if half_star:
        stars += "½"
    
    return stars

def send_message_to_api(message: str, mode: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """Send a message to the backend API.
    
    Args:
        message: User's message
        mode: The mode (flight, hotel, trip)
        conversation_id: Optional conversation ID for context
        
    Returns:
        API response as a dictionary
    """
    try:
        # Format payload exactly as expected by the backend API
        # The MessageRequest model in backend expects: message, session_id, mode
        # Note: session_id must be a string, not None
        payload = {
            "message": message,
            "session_id": conversation_id if conversation_id else "",  # Empty string if None
            "mode": mode
        }
        
        # Add debugging information
        if 'debug' not in st.session_state:
            st.session_state.debug = []
        
        st.session_state.debug.append(f"Sending request to {API_URL}/api/chat: {json.dumps(payload)}")
        
        # Make the API request
        response = requests.post(
            f"{API_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            # Add debugging info
            if 'debug' in st.session_state:
                st.session_state.debug.append(f"API Response: {json.dumps(data)}")
            return data
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            if 'debug' in st.session_state:
                st.session_state.debug.append(error_msg)
            st.error(error_msg)
            return {"response": f"Error: Unable to get response from the assistant. Status code: {response.status_code}"}
    
    except Exception as e:
        error_msg = f"Error communicating with the API: {str(e)}"
        if 'debug' in st.session_state:
            st.session_state.debug.append(error_msg)
        st.error(error_msg)
        return {"response": f"Error: {str(e)}"}

def display_flight_results(flights: List[Dict[str, Any]]) -> None:
    """Display flight search results.
    
    Args:
        flights: List of flight result objects
    """
    if not flights:
        st.info("No flight results available.")
        return
    
    for flight in flights:
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"### {flight.get('airline', 'Unknown Airline')}")
                st.write(f"**From** {flight.get('origin', 'Origin')} **to** {flight.get('destination', 'Destination')}")
                st.write(f"**Duration:** {flight.get('duration', 'N/A')}")
            
            with col2:
                st.write("**Departure:** " + flight.get('departure_time', 'N/A'))
                st.write("**Arrival:** " + flight.get('arrival_time', 'N/A'))
                st.write(f"**Stops:** {flight.get('stops', 0)}")
            
            with col3:
                st.markdown(f"### {flight.get('formatted_price', flight.get('price', 'N/A'))}")
                if flight.get('booking_link'):
                    st.markdown(f"[Book Now]({flight.get('booking_link')})")
            
            st.markdown("---")

def display_hotel_results(hotels: List[Dict[str, Any]]) -> None:
    """Display hotel search results.
    
    Args:
        hotels: List of hotel result objects
    """
    if not hotels:
        st.info("No hotel results available.")
        return
    
    for hotel in hotels:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {hotel.get('title', 'Unknown Hotel')}")
                stars = display_stars(hotel.get('rating_stars', 0))
                st.markdown(f"<span class='stars'>{stars}</span>", unsafe_allow_html=True)
                st.write(f"**Location:** {hotel.get('address', hotel.get('location', 'N/A'))}")
                
                if hotel.get('amenities'):
                    st.write("**Amenities:**")
                    amenities_html = "<div class='amenities'>"
                    for amenity in hotel.get('amenities', []):
                        amenities_html += f"<span class='amenity-tag'>{amenity}</span>"
                    amenities_html += "</div>"
                    st.markdown(amenities_html, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"### {hotel.get('formatted_price', hotel.get('price', 'N/A'))}")
                if hotel.get('booking_link'):
                    st.markdown(f"[Book Now]({hotel.get('booking_link')})")
            
            st.markdown("---")

def display_place_results(places: List[Dict[str, Any]]) -> None:
    """Display place/attraction search results.
    
    Args:
        places: List of place result objects
    """
    if not places:
        st.info("No place results available.")
        return
    
    for place in places:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {place.get('title', 'Unknown Attraction')}")
                stars = display_stars(place.get('rating_stars', 0))
                ratings_count = place.get('rating_count', 0)
                st.markdown(f"<span class='stars'>{stars}</span> ({ratings_count} reviews)", unsafe_allow_html=True)
                st.write(f"**Address:** {place.get('address', 'N/A')}")
                
                if place.get('categories'):
                    categories = ", ".join(place.get('categories', []))
                    st.write(f"**Categories:** {categories}")
                
                if place.get('phone'):
                    st.write(f"**Phone:** {place.get('phone')}")
            
            with col2:
                if place.get('website'):
                    st.markdown(f"[Visit Website]({place.get('website')})")
                
                if place.get('hours'):
                    with st.expander("Opening Hours"):
                        for hour in place.get('hours', []):
                            st.write(f"{hour.get('day')}: {hour.get('open')} - {hour.get('close')}")
            
            st.markdown("---")

def init_session_state():
    """Initialize session state variables if they don't exist."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = None
    
    if 'mode' not in st.session_state:
        st.session_state.mode = DEFAULT_MODE
    
    if 'search_results' not in st.session_state:
        st.session_state.search_results = {}
        
    if 'debug' not in st.session_state:
        st.session_state.debug = []
        
    if 'show_debug' not in st.session_state:
        st.session_state.show_debug = False

def main():
    """Main application function."""
    # Initialize session state
    init_session_state()
    
    # App header
    st.markdown("<h1 class='main-title'>Rahalah - Your Saudi Travel Assistant</h1>", unsafe_allow_html=True)
    
    # Debug toggle in sidebar
    with st.sidebar:
        st.session_state.show_debug = st.checkbox("Show Debug Panel", value=st.session_state.show_debug)
        
        if st.session_state.show_debug:
            if st.button("Clear Debug Logs"):
                st.session_state.debug = []
                
    # Show debug panel if enabled
    if st.session_state.show_debug:
        with st.expander("Debug Information", expanded=True):
            st.write(f"API URL: {API_URL}")
            st.write(f"Current Mode: {st.session_state.mode}")
            st.write(f"Conversation ID: {st.session_state.conversation_id}")
            
            if st.session_state.debug:
                for i, log in enumerate(st.session_state.debug):
                    st.text(f"{i+1}. {log}")
            else:
                st.info("No debug logs yet.")
    
    # Sidebar for mode selection
    st.sidebar.title("Mode Selection")
    selected_mode = st.sidebar.radio(
        "Choose Mode",
        ["trip", "flight", "hotel"],
        index=["trip", "flight", "hotel"].index(st.session_state.mode)
    )
    
    if selected_mode != st.session_state.mode:
        st.session_state.mode = selected_mode
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.session_state.search_results = {}
    
    # Sidebar for sample queries
    st.sidebar.title("Sample Queries")
    sample_queries = {
        "trip": [
            "Plan a 7-day trip to Riyadh",
            "What's a good itinerary for a weekend in Jeddah?",
            "Suggest activities for a family vacation in Mecca"
        ],
        "flight": [
            "Find flights from Riyadh to Jeddah next weekend",
            "What are the cheapest flights to Madinah in July?",
            "Show me business class options from Riyadh to Dubai"
        ],
        "hotel": [
            "Find hotels in Riyadh near Kingdom Centre",
            "What are the best 5-star hotels in Jeddah?",
            "Show me family-friendly accommodations in Mecca"
        ]
    }
    
    for query in sample_queries.get(st.session_state.mode, []):
        if st.sidebar.button(query, key=query):
            st.session_state.user_input = query
            process_user_input(query)
    
    # Display conversation history
    if st.session_state.messages:
        for message in st.session_state.messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "user":
                st.markdown(f"<div class='chat-message user'><p>{content}</p></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-message assistant'><p>{content}</p></div>", unsafe_allow_html=True)
    else:
        # Welcome message
        if st.session_state.mode == "trip":
            st.info("Welcome to Rahalah! Ask me to plan a trip for you, and I'll help with flights, hotels, and places to visit.")
        elif st.session_state.mode == "flight":
            st.info("Welcome to Rahalah Flight Search! Tell me where you want to fly from and to, and I'll find the best options.")
        elif st.session_state.mode == "hotel":
            st.info("Welcome to Rahalah Hotel Search! Tell me where you're looking to stay, and I'll find great accommodation options.")
    
    # Display search results if available
    if st.session_state.search_results:
        st.markdown("## Search Results")
        
        tabs = []
        if "flight" in st.session_state.search_results:
            tabs.append("Flights")
        if "hotel" in st.session_state.search_results:
            tabs.append("Hotels")
        if "place" in st.session_state.search_results:
            tabs.append("Places to Visit")
        
        if tabs:
            selected_tab = st.tabs(tabs)
            
            tab_index = 0
            if "flight" in st.session_state.search_results:
                with selected_tab[tab_index]:
                    display_flight_results(st.session_state.search_results.get("flight", []))
                tab_index += 1
            
            if "hotel" in st.session_state.search_results:
                with selected_tab[tab_index]:
                    display_hotel_results(st.session_state.search_results.get("hotel", []))
                tab_index += 1
            
            if "place" in st.session_state.search_results:
                with selected_tab[tab_index]:
                    display_place_results(st.session_state.search_results.get("place", []))
    
    # User input for chat
    user_input = st.chat_input("Type your travel query...")
    if user_input:
        process_user_input(user_input)

def process_user_input(user_input: str) -> None:
    """Process user input, send to API, and update UI.
    
    Args:
        user_input: The user's input message
    """
    # Add debug log
    if 'debug' in st.session_state:
        st.session_state.debug.append(f"Processing user input: {user_input}")
        st.session_state.debug.append(f"Current mode: {st.session_state.mode}")
    
    # Add user message to chat history
    user_message = {"role": "user", "content": user_input}
    st.session_state.messages.append(user_message)
    
    # Get response from the API
    response_data = send_message_to_api(
        user_input,
        st.session_state.mode,
        st.session_state.conversation_id
    )
    
    # Add debug log for response data
    if 'debug' in st.session_state:
        st.session_state.debug.append(f"Received response_data keys: {list(response_data.keys() if response_data else [])}")
    
    # Update conversation ID if present
    if response_data.get("session_id"):
        st.session_state.conversation_id = response_data.get("session_id")
        if 'debug' in st.session_state:
            st.session_state.debug.append(f"Updated conversation_id: {st.session_state.conversation_id}")
    
    # Add assistant response to chat history
    assistant_message = {"role": "assistant", "content": response_data.get("response", "")}
    st.session_state.messages.append(assistant_message)
    
    # Update search results if present
    if response_data.get("search_results"):
        st.session_state.search_results = response_data.get("search_results", {})
        if 'debug' in st.session_state:
            st.session_state.debug.append(f"Updated search_results with keys: {list(st.session_state.search_results.keys())}")
    
    # Rerun the app to show updated messages and results
    st.rerun()

if __name__ == "__main__":
    main()
