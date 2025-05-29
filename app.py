# app.py - UPDATED WITH ENHANCED PDF GENERATOR INTEGRATION

#!/usr/bin/env python3
"""
ENHANCED Flask Route Analytics Application - File-based Session Storage
Fixed PDF generation with detailed tables, maps with markers, and weather graphs
"""

import os
import io
import csv
import json
import datetime
import tempfile
import uuid
from pathlib import Path
import pandas as pd
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
import polyline
from geopy.distance import geodesic
import logging
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import our custom modules
try:
    from utils.pdf_generator import generate_pdf
    from utils.network_coverage import NetworkCoverageAnalyzer
    print("✅ Enhanced PDF generator and network coverage analyzer imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import utils modules: {e}")
    print("📋 Please ensure utils/pdf_generator.py and utils/network_coverage.py are created")
    # Try to import simple fallback
    try:
        from utils.pdf_generator_simple import generate_pdf
        print("✅ Fallback simple PDF generator imported")
    except ImportError:
        print("❌ No PDF generator available")
        generate_pdf = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-route-analytics-2024')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SESSION_DATA_FOLDER'] = 'session_data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SESSION_DATA_FOLDER'], exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Fixed credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# API Keys
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'AIzaSyAXa6qLmUm7YEoUOqpIZF8A00663AKgq68')
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '904f1f92432e925f1536c88b0a6c613f')

class SessionDataManager:
    """Manage large session data using file storage"""
    
    def __init__(self, data_folder):
        self.data_folder = data_folder
        os.makedirs(data_folder, exist_ok=True)
    
    def store_route_data(self, session_id, route_data):
        """Store route data in a file"""
        try:
            filename = f"route_data_{session_id}.json"
            filepath = os.path.join(self.data_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(route_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Route data stored in {filename}")
            return True
        except Exception as e:
            logger.error(f"Error storing route data: {e}")
            return False
    
    def get_route_data(self, session_id):
        """Retrieve route data from file"""
        try:
            filename = f"route_data_{session_id}.json"
            filepath = os.path.join(self.data_folder, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    route_data = json.load(f)
                logger.info(f"Route data retrieved from {filename}")
                return route_data
            else:
                logger.warning(f"Route data file not found: {filename}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving route data: {e}")
            return None
    
    def delete_route_data(self, session_id):
        """Delete route data file"""
        try:
            filename = f"route_data_{session_id}.json"
            filepath = os.path.join(self.data_folder, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Route data file deleted: {filename}")
                return True
        except Exception as e:
            logger.error(f"Error deleting route data: {e}")
        return False
    
    def cleanup_old_files(self, max_age_hours=24):
        """Clean up old session data files"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(self.data_folder):
                if filename.startswith('route_data_') and filename.endswith('.json'):
                    filepath = os.path.join(self.data_folder, filename)
                    file_age = current_time - os.path.getmtime(filepath)
                    
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        logger.info(f"Cleaned up old session file: {filename}")
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")

# Initialize session data manager
session_manager = SessionDataManager(app.config['SESSION_DATA_FOLDER'])

class RouteAnalyzer:
    """Complete route analysis with real-time data"""
    
    def __init__(self, google_api_key, weather_api_key):
        self.google_api_key = google_api_key
        self.weather_api_key = weather_api_key
        try:
            self.network_analyzer = NetworkCoverageAnalyzer()
        except NameError:
            self.network_analyzer = None
            logger.warning("NetworkCoverageAnalyzer not available")
    
    def analyze_csv_route(self, csv_file_path):
        """Analyze route from CSV coordinates"""
        try:
            # Read CSV coordinates
            route_points = self.read_csv_coordinates(csv_file_path)
            if not route_points:
                return {'error': 'No valid coordinates found in CSV'}
            
            logger.info(f"Analyzing route with {len(route_points)} points")
            
            # Get start and end points
            start_point = route_points[0]
            end_point = route_points[-1]
            
            # Get route information from Google Maps
            route_info = self.get_google_route_info(start_point, end_point)
            
            # Analyze sharp turns
            sharp_turns = self.analyze_sharp_turns(route_points)
            
            # Get weather data along route
            weather_data = self.get_weather_data(route_points)
            
            # Analyze network coverage
            network_coverage = self.analyze_network_coverage(route_points)
            
            # Find Points of Interest
            pois = self.find_points_of_interest(route_points)
            
            # Calculate risk segments
            risk_segments = self.calculate_risk_segments(sharp_turns, weather_data)
            
            # Get elevation data
            elevation_data = self.get_elevation_data(route_points)
            
            return {
                'status': 'success',
                'route_points': route_points,
                'from_address': route_info.get('start_address', f"{start_point[0]:.6f}, {start_point[1]:.6f}"),
                'to_address': route_info.get('end_address', f"{end_point[0]:.6f}, {end_point[1]:.6f}"),
                'distance': route_info.get('distance', 'Unknown'),
                'duration': route_info.get('duration', 'Unknown'),
                'sharp_turns': sharp_turns,
                'weather': weather_data,
                'network_coverage': network_coverage,
                'petrol_bunks': pois.get('gas_stations', {}),
                'hospitals': pois.get('hospitals', {}),
                'schools': pois.get('schools', {}),
                'food_stops': pois.get('restaurants', {}),
                'police_stations': pois.get('police', {}),
                'elevation': elevation_data,
                'risk_segments': risk_segments,
                'major_highways': route_info.get('major_highways', []),
                'route_polyline': route_points,
                'total_points': len(route_points)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing route: {e}")
            return {'error': f'Failed to analyze route: {str(e)}'}
    
    def read_csv_coordinates(self, csv_file_path):
        """Read coordinates from CSV file"""
        try:
            coordinates = []
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row_num, row in enumerate(reader):
                    if len(row) >= 2:
                        try:
                            lat = float(row[0])
                            lng = float(row[1])
                            if -90 <= lat <= 90 and -180 <= lng <= 180:
                                coordinates.append([lat, lng])
                        except (ValueError, IndexError):
                            continue
            
            logger.info(f"Read {len(coordinates)} valid coordinates from CSV")
            return coordinates
            
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            return []
    
    def get_google_route_info(self, start_point, end_point):
        """Get route information from Google Maps API"""
        try:
            base_url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': f"{start_point[0]},{start_point[1]}",
                'destination': f"{end_point[0]},{end_point[1]}",
                'key': self.google_api_key,
                'mode': 'driving',
                'alternatives': 'false'
            }
            
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and data.get('routes'):
                    route = data['routes'][0]
                    leg = route['legs'][0]
                    
                    # Extract highway information
                    major_highways = []
                    for step in leg['steps']:
                        if 'html_instructions' in step:
                            instruction = step['html_instructions'].lower()
                            if any(hw in instruction for hw in ['highway', 'expressway', 'freeway', 'nh-', 'sh-']):
                                major_highways.append(step['html_instructions'])
                    
                    return {
                        'start_address': leg.get('start_address', 'Unknown'),
                        'end_address': leg.get('end_address', 'Unknown'),
                        'distance': leg.get('distance', {}).get('text', 'Unknown'),
                        'duration': leg.get('duration', {}).get('text', 'Unknown'),
                        'major_highways': list(set(major_highways))[:5]  # Limit to 5 unique highways
                    }
            
            return {'error': 'Failed to get route information from Google Maps'}
            
        except Exception as e:
            logger.error(f"Error getting Google route info: {e}")
            return {'error': f'Google Maps API error: {str(e)}'}
    
    def analyze_sharp_turns(self, route_points):
        """Analyze sharp turns in the route"""
        if len(route_points) < 3:
            return []
        
        sharp_turns = []
        
        # Sample points to avoid too many calculations
        step = max(1, len(route_points) // 100)  # Sample ~100 points max
        sampled_points = route_points[::step]
        
        for i in range(1, len(sampled_points) - 1):
            try:
                p1 = sampled_points[i-1]
                p2 = sampled_points[i]
                p3 = sampled_points[i+1]
                
                # Calculate angle between three points
                angle = self.calculate_turn_angle(p1, p2, p3)
                
                # Consider turns >= 45 degrees as significant
                if angle >= 45:
                    sharp_turns.append({
                        'lat': p2[0],
                        'lng': p2[1],
                        'angle': round(angle, 2),
                        'index': i * step,
                        'classification': self.classify_turn(angle)
                    })
                    
            except Exception as e:
                continue
        
        # Sort by angle (most dangerous first)
        sharp_turns.sort(key=lambda x: x['angle'], reverse=True)
        
        logger.info(f"Found {len(sharp_turns)} sharp turns")
        return sharp_turns[:50]  # Limit to top 50 most dangerous turns
    
    def calculate_turn_angle(self, p1, p2, p3):
        """Calculate turn angle between three points"""
        import math
        
        # Calculate bearings
        bearing1 = self.calculate_bearing(p1, p2)
        bearing2 = self.calculate_bearing(p2, p3)
        
        # Calculate turn angle
        angle = abs(bearing2 - bearing1)
        if angle > 180:
            angle = 360 - angle
            
        return angle
    
    def calculate_bearing(self, point1, point2):
        """Calculate bearing between two points"""
        import math
        
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        dlon = lon2 - lon1
        
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360
        
        return bearing
    
    def classify_turn(self, angle):
        """Classify turn based on angle"""
        if angle >= 90:
            return "EXTREME BLIND SPOT"
        elif angle >= 80:
            return "HIGH-RISK BLIND SPOT"
        elif angle >= 70:
            return "BLIND SPOT"
        elif angle >= 60:
            return "HIGH-ANGLE TURN"
        else:
            return "SHARP TURN"
    
    def get_weather_data(self, route_points):
        """Get weather data along the route"""
        weather_data = []
        
        # Sample 10 points along the route for weather
        step = max(1, len(route_points) // 10)
        sampled_points = route_points[::step]
        
        for i, point in enumerate(sampled_points[:10]):
            try:
                url = f"http://api.openweathermap.org/data/2.5/weather"
                params = {
                    'lat': point[0],
                    'lon': point[1],
                    'appid': self.weather_api_key,
                    'units': 'metric'
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    weather_data.append({
                        'location': f"Point {i+1}",
                        'coordinates': {'lat': point[0], 'lng': point[1]},
                        'temp': data['main']['temp'],
                        'description': data['weather'][0]['description'],
                        'humidity': data['main']['humidity'],
                        'wind_speed': data.get('wind', {}).get('speed', 0)
                    })
                
            except Exception as e:
                logger.warning(f"Weather API error for point {point}: {e}")
                continue
        
        logger.info(f"Retrieved weather data for {len(weather_data)} points")
        return weather_data
    
    def analyze_network_coverage(self, route_points):
        """Analyze network coverage along the route"""
        if not self.network_analyzer:
            return {
                'error': 'Network analyzer not available',
                'coverage_analysis': [],
                'dead_zones': [],
                'poor_zones': [],
                'coverage_stats': {'error': 'NetworkCoverageAnalyzer not imported'},
                'recommendations': []
            }
        
        try:
            logger.info("Starting network coverage analysis...")
            
            # Analyze coverage
            coverage_analysis = self.network_analyzer.analyze_route_coverage(route_points, sample_interval=20)
            
            # Identify problem areas
            dead_zones = self.network_analyzer.identify_dead_zones(coverage_analysis)
            poor_zones = self.network_analyzer.identify_poor_coverage_zones(coverage_analysis)
            
            # Calculate statistics
            coverage_stats = self.network_analyzer.calculate_coverage_statistics(coverage_analysis)
            
            # Generate recommendations
            recommendations = self.network_analyzer.generate_recommendations(dead_zones, poor_zones, 'car')
            
            result = {
                'coverage_analysis': coverage_analysis,
                'dead_zones': dead_zones,
                'poor_zones': poor_zones,
                'coverage_stats': coverage_stats,
                'recommendations': recommendations
            }
            
            logger.info(f"Network coverage analysis completed. Success rate: {coverage_stats.get('api_success_rate', 0):.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"Network coverage analysis failed: {e}")
            return {
                'error': str(e),
                'coverage_analysis': [],
                'dead_zones': [],
                'poor_zones': [],
                'coverage_stats': {'error': str(e)},
                'recommendations': []
            }
    
    def find_points_of_interest(self, route_points):
        """Find Points of Interest along the route"""
        pois = {
            'gas_stations': {},
            'hospitals': {},
            'schools': {},
            'restaurants': {},
            'police': {}
        }
        
        # Sample 5 points along route for POI search
        step = max(1, len(route_points) // 5)
        sampled_points = route_points[::step]
        
        poi_types = {
            'gas_stations': 'gas_station',
            'hospitals': 'hospital',
            'schools': 'school',
            'restaurants': 'restaurant',
            'police': 'police'
        }
        
        for point in sampled_points[:5]:
            for poi_key, poi_type in poi_types.items():
                try:
                    places = self.search_nearby_places(point[0], point[1], poi_type)
                    for place in places[:3]:  # Top 3 per location
                        name = place.get('name', 'Unknown')
                        vicinity = place.get('vicinity', 'Unknown location')
                        pois[poi_key][name] = vicinity
                        
                except Exception as e:
                    logger.warning(f"Error finding {poi_type} near {point}: {e}")
                    continue
        
        logger.info(f"Found POIs: {sum(len(v) for v in pois.values())} total")
        return pois
    
    def search_nearby_places(self, lat, lng, place_type):
        """Search for nearby places using Google Places API"""
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': 5000,  # 5km radius
                'type': place_type,
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            
            return []
            
        except Exception as e:
            logger.warning(f"Places API error: {e}")
            return []
    
    def calculate_risk_segments(self, sharp_turns, weather_data):
        """Calculate risk segments based on turns and weather"""
        risk_segments = []
        
        for turn in sharp_turns:
            angle = turn.get('angle', 0)
            
            if angle >= 90:
                risk_level = 'HIGH'
            elif angle >= 70:
                risk_level = 'HIGH'
            elif angle >= 60:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            risk_segments.append({
                'coordinates': {'lat': turn['lat'], 'lng': turn['lng']},
                'risk_level': risk_level,
                'risk_factor': 'Sharp Turn',
                'angle': angle,
                'description': f"{turn.get('classification', 'Turn')} - {angle}°"
            })
        
        # Add weather-based risks
        for weather in weather_data:
            temp = weather.get('temp', 20)
            description = weather.get('description', '').lower()
            
            risk_level = 'LOW'
            if temp > 40 or temp < 5:
                risk_level = 'MEDIUM'
            if any(condition in description for condition in ['rain', 'storm', 'snow', 'fog']):
                risk_level = 'HIGH'
            
            if risk_level in ['MEDIUM', 'HIGH']:
                risk_segments.append({
                    'coordinates': weather.get('coordinates', {}),
                    'risk_level': risk_level,
                    'risk_factor': 'Weather',
                    'temperature': temp,
                    'description': f"Weather: {weather.get('description', 'Unknown')}"
                })
        
        return risk_segments
    
    def get_elevation_data(self, route_points):
        """Get elevation data for the route"""
        elevation_data = []
        
        # Sample 10 points for elevation
        step = max(1, len(route_points) // 10)
        sampled_points = route_points[::step]
        
        try:
            # Prepare locations for Google Elevation API
            locations = '|'.join([f"{point[0]},{point[1]}" for point in sampled_points[:10]])
            
            url = "https://maps.googleapis.com/maps/api/elevation/json"
            params = {
                'locations': locations,
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                for i, result in enumerate(data.get('results', [])):
                    elevation_data.append({
                        'location': result.get('location', {}),
                        'elevation': result.get('elevation', 0),
                        'resolution': result.get('resolution', 0),
                        'index': i
                    })
            
        except Exception as e:
            logger.warning(f"Elevation API error: {e}")
        
        return elevation_data

# Initialize the route analyzer
route_analyzer = RouteAnalyzer(GOOGLE_MAPS_API_KEY, OPENWEATHER_API_KEY)

# Helper function to get or create session ID
def get_session_id():
    """Get or create a unique session ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

# Flask Routes

@app.route('/')
def index():
    """Home page - redirect to login if not authenticated"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            # Generate unique session ID
            session['session_id'] = str(uuid.uuid4())
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and cleanup session data"""
    session_id = session.get('session_id')
    if session_id:
        session_manager.delete_route_data(session_id)
    
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Check if route data exists
    session_id = get_session_id()
    route_data = session_manager.get_route_data(session_id)
    
    # Store route data availability in session (small data)
    session['has_route_data'] = route_data is not None
    
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_csv():
    """Handle CSV upload and route analysis"""
    if 'logged_in' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        if 'csv_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['csv_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Please upload a CSV file'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze the route
        logger.info(f"Starting route analysis for file: {filename}")
        route_data = route_analyzer.analyze_csv_route(filepath)
        
        if 'error' in route_data:
            return jsonify({'error': route_data['error']}), 400
        
        # Store route data in file instead of session
        session_id = get_session_id()
        if session_manager.store_route_data(session_id, route_data):
            # Store only small metadata in session
            session['has_route_data'] = True
            session['uploaded_file'] = filename
            session['analysis_timestamp'] = datetime.datetime.now().isoformat()
            
            logger.info(f"Route data stored successfully for session {session_id}")
        else:
            return jsonify({'error': 'Failed to store route data'}), 500
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'status': 'success',
            'message': 'Route analyzed successfully!',
            'data': {
                'from_address': route_data.get('from_address'),
                'to_address': route_data.get('to_address'),
                'distance': route_data.get('distance'),
                'duration': route_data.get('duration'),
                'total_points': route_data.get('total_points'),
                'sharp_turns': len(route_data.get('sharp_turns', [])),
                'weather_points': len(route_data.get('weather', [])),
                'network_coverage': route_data.get('network_coverage', {}).get('coverage_stats', {}),
                'pois_found': sum(len(v) for v in [
                    route_data.get('petrol_bunks', {}),
                    route_data.get('hospitals', {}),
                    route_data.get('schools', {}),
                    route_data.get('food_stops', {}),
                    route_data.get('police_stations', {})
                ])
            }
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/generate-pdf')
def generate_pdf_report():
    """Generate enhanced PDF report with comprehensive analysis"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    session_id = get_session_id()
    route_data = session_manager.get_route_data(session_id)
    
    if not route_data:
        flash('No route data available. Please upload and analyze a route first.', 'error')
        return redirect(url_for('dashboard'))
    
    if not generate_pdf:
        flash('PDF generator not available. Please check system configuration.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"enhanced_route_analysis_report_{timestamp}.pdf"
        pdf_path = os.path.join('reports', pdf_filename)
        
        # Create reports directory
        os.makedirs('reports', exist_ok=True)
        
        # Generate enhanced PDF with comprehensive analysis
        logger.info(f"Generating enhanced PDF report: {pdf_filename}")
        
        result = generate_pdf(
            filename=pdf_path,
            from_addr=route_data.get('from_address', 'Unknown'),
            to_addr=route_data.get('to_address', 'Unknown'),
            distance=route_data.get('distance', 'Unknown'),
            duration=route_data.get('duration', 'Unknown'),
            turns=route_data.get('sharp_turns', []),
            petrol_bunks=route_data.get('petrol_bunks', {}),
            hospital_list=route_data.get('hospitals', {}),
            schools=route_data.get('schools', {}),
            food_stops=route_data.get('food_stops', {}),
            police_stations=route_data.get('police_stations', {}),
            elevation=route_data.get('elevation', []),
            weather=route_data.get('weather', []),
            risk_segments=route_data.get('risk_segments', []),
            major_highways=route_data.get('major_highways', []),
            vehicle_type='car',
            type='enhanced_comprehensive',
            api_key=GOOGLE_MAPS_API_KEY,
            route_data=route_data  # Pass complete route data
        )
        
        if result:
            logger.info(f"Enhanced PDF report generated successfully: {pdf_filename}")
            flash('Enhanced PDF report generated successfully with detailed tables, maps, and weather graphs!', 'success')
            return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
        else:
            flash('Failed to generate enhanced PDF report', 'error')
            return redirect(url_for('dashboard'))
            
    except Exception as e:
        logger.error(f"Enhanced PDF generation error: {e}")
        flash(f'Enhanced PDF generation failed: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/route-details')
def route_details():
    """Enhanced route details with comprehensive analysis"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    session_id = get_session_id()
    route_data = session_manager.get_route_data(session_id)
    
    if not route_data:
        flash('No route data available. Please upload and analyze a route first.', 'error')
        return redirect(url_for('dashboard'))
    
    # Add enhanced calculations for display
    sharp_turns = route_data.get('sharp_turns', [])
    network_coverage = route_data.get('network_coverage', {})
    
    # Enhanced route data with calculations
    enhanced_route_data = route_data.copy()
    enhanced_route_data['enhanced_stats'] = {
        'safety_score': calculate_route_safety_score(
            sharp_turns,
            len(network_coverage.get('dead_zones', [])),
            len(network_coverage.get('poor_zones', []))
        ),
        'blind_spots_count': len([t for t in sharp_turns if t.get('angle', 0) > 80]),
        'sharp_danger_count': len([t for t in sharp_turns if 70 <= t.get('angle', 0) <= 80]),
        'moderate_turns_count': len([t for t in sharp_turns if 45 <= t.get('angle', 0) < 70]),
        'total_critical_alerts': len([t for t in sharp_turns if t.get('angle', 0) > 80]) + len(network_coverage.get('dead_zones', [])),
        'network_reliability': 'HIGH' if network_coverage.get('coverage_stats', {}).get('overall_coverage_score', 0) > 80 else 'MEDIUM' if network_coverage.get('coverage_stats', {}).get('overall_coverage_score', 0) > 60 else 'LOW'
    }
    
    return render_template('route_details.html', 
                         route_data=enhanced_route_data, 
                         google_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/clear-analysis', methods=['POST'])
def clear_analysis():
    """Clear previous analysis data"""
    if 'logged_in' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        session_id = get_session_id()
        
        # Delete route data file
        if session_manager.delete_route_data(session_id):
            # Clear session flags
            session.pop('has_route_data', None)
            session.pop('uploaded_file', None)
            session.pop('analysis_timestamp', None)
            
            logger.info(f"Analysis data cleared for session {session_id}")
            
            return jsonify({
                'status': 'success',
                'message': 'Previous analysis cleared successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'No previous analysis found to clear'
            })
            
    except Exception as e:
        logger.error(f"Error clearing analysis: {e}")
        return jsonify({
            'status': 'error',
            'error': f'Failed to clear analysis: {str(e)}'
        }), 500

@app.route('/analysis-status')
def analysis_status():
    """Check if previous analysis data exists"""
    if 'logged_in' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        session_id = get_session_id()
        route_data = session_manager.get_route_data(session_id)
        
        if route_data:
            # Extract summary information
            summary = {
                'has_data': True,
                'from_address': route_data.get('from_address', 'Unknown'),
                'to_address': route_data.get('to_address', 'Unknown'),
                'distance': route_data.get('distance', 'Unknown'),
                'duration': route_data.get('duration', 'Unknown'),
                'total_points': route_data.get('total_points', 0),
                'sharp_turns_count': len(route_data.get('sharp_turns', [])),
                'network_dead_zones': len(route_data.get('network_coverage', {}).get('dead_zones', [])),
                'network_poor_zones': len(route_data.get('network_coverage', {}).get('poor_zones', [])),
                'network_coverage_score': route_data.get('network_coverage', {}).get('coverage_stats', {}).get('overall_coverage_score', 0),
                'pois_count': sum([
                    len(route_data.get('hospitals', {})),
                    len(route_data.get('petrol_bunks', {})),
                    len(route_data.get('schools', {})),
                    len(route_data.get('food_stops', {})),
                    len(route_data.get('police_stations', {}))
                ]),
                'analysis_timestamp': session.get('analysis_timestamp'),
                'uploaded_file': session.get('uploaded_file')
            }
            
            return jsonify({
                'status': 'success',
                'data': summary
            })
        else:
            return jsonify({
                'status': 'success',
                'data': {'has_data': False}
            })
            
    except Exception as e:
        logger.error(f"Error checking analysis status: {e}")
        return jsonify({
            'status': 'error',
            'error': f'Failed to check analysis status: {str(e)}'
        }), 500

def calculate_route_safety_score(sharp_turns, dead_zones_count, poor_zones_count):
    """Calculate overall route safety score (0-100)"""
    base_score = 100
    
    if not sharp_turns:
        return base_score
    
    # Categorize turns by severity
    blind_spots = len([t for t in sharp_turns if t.get('angle', 0) > 80])
    sharp_danger = len([t for t in sharp_turns if 70 <= t.get('angle', 0) <= 80])
    moderate_turns = len([t for t in sharp_turns if 45 <= t.get('angle', 0) < 70])
    
    # Deduct points based on severity
    base_score -= blind_spots * 15        # 15 points per blind spot
    base_score -= sharp_danger * 10       # 10 points per sharp turn
    base_score -= moderate_turns * 5      # 5 points per moderate turn
    base_score -= dead_zones_count * 8    # 8 points per dead zone
    base_score -= poor_zones_count * 4    # 4 points per poor coverage zone
    
    return max(0, min(100, base_score))

# Cleanup task - run periodically
@app.before_request
def cleanup_old_session_data():
    """Clean up old session data files periodically"""
    # Only run cleanup occasionally (1% chance per request)
    import random
    if random.random() < 0.01:
        session_manager.cleanup_old_files()

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('utils', exist_ok=True)
    os.makedirs('session_data', exist_ok=True)
    
    print("\n🚀 Starting Enhanced Route Analytics Application...")
    print("=" * 70)
    print(f"📍 Admin Login: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    print(f"🔑 Google Maps API Key: {'✅ Configured' if GOOGLE_MAPS_API_KEY else '❌ Missing'}")
    print(f"🌤️ Weather API Key: {'✅ Configured' if OPENWEATHER_API_KEY else '❌ Missing'}")
    print(f"📊 PDF Generator: {'✅ Enhanced Available' if generate_pdf else '❌ Not Available'}")
    print("💾 Session Storage: File-based (Optimized for large data)")
    print("📈 Features: Detailed POI Tables, Maps with Markers, Weather Graphs")
    print("🌐 Application URL: http://localhost:5000")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)