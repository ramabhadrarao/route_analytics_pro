# utils/google_maps_enhancements.py - NEW MODULE FOR JMP MISSING FEATURES

import requests
import json
import time
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class GoogleMapsEnhancements:
    """Enhanced Google Maps features for JMP compliance - NEW FEATURES ONLY"""
    
    def __init__(self, google_api_key):
        self.google_api_key = google_api_key
        
        # Terrain classification rules
        self.terrain_types = {
            'urban': ['locality', 'sublocality', 'administrative_area_level_2'],
            'semi_urban': ['administrative_area_level_3', 'neighborhood'],
            'rural': ['administrative_area_level_1', 'country', 'natural_feature']
        }
    
    def enhance_route_with_supply_customer_details(self, route_data: Dict, supply_location: str = None, customer_name: str = None) -> Dict:
        """JMP Feature 1: Supply location & customer details with geocoding"""
        
        enhanced_data = {
            'supply_details': {},
            'customer_details': {},
            'geocoded_locations': {}
        }
        
        try:
            # Get route start and end coordinates
            route_points = route_data.get('route_points', [])
            if not route_points:
                return enhanced_data
            
            start_point = route_points[0]
            end_point = route_points[-1]
            
            # Reverse geocode start location (supply location)
            supply_address = self.reverse_geocode(start_point[0], start_point[1])
            enhanced_data['supply_details'] = {
                'coordinates': {'lat': start_point[0], 'lng': start_point[1]},
                'formatted_address': supply_address.get('formatted_address', 'Unknown'),
                'place_name': supply_location or supply_address.get('name', 'Supply Location'),
                'place_types': supply_address.get('types', []),
                'address_components': supply_address.get('address_components', [])
            }
            
            # Reverse geocode end location (customer location)
            customer_address = self.reverse_geocode(end_point[0], end_point[1])
            enhanced_data['customer_details'] = {
                'coordinates': {'lat': end_point[0], 'lng': end_point[1]},
                'formatted_address': customer_address.get('formatted_address', 'Unknown'),
                'customer_name': customer_name or 'Customer Location',
                'place_types': customer_address.get('types', []),
                'address_components': customer_address.get('address_components', [])
            }
            
            print("✅ Supply & Customer details enhanced with geocoding")
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error enhancing supply/customer details: {e}")
            return enhanced_data
    
    def classify_route_terrain(self, route_points: List) -> Dict:
        """JMP Feature 2: Terrain classification (urban/semi-urban/rural)"""
        
        terrain_analysis = {
            'terrain_segments': [],
            'overall_classification': 'mixed',
            'terrain_distribution': {'urban': 0, 'semi_urban': 0, 'rural': 0},
            'classification_method': 'Google Roads API + Geocoding'
        }
        
        try:
            # Sample points along route for terrain analysis
            sample_size = min(20, len(route_points))
            step = max(1, len(route_points) // sample_size)
            sampled_points = route_points[::step]
            
            for i, point in enumerate(sampled_points):
                lat, lng = point[0], point[1]
                
                # Get detailed location information
                location_info = self.reverse_geocode(lat, lng)
                terrain_type = self.determine_terrain_type(location_info)
                
                segment = {
                    'segment_id': i + 1,
                    'coordinates': {'lat': lat, 'lng': lng},
                    'terrain_type': terrain_type,
                    'location_types': location_info.get('types', []),
                    'formatted_address': location_info.get('formatted_address', 'Unknown'),
                    'distance_from_start': self.calculate_distance_from_start(point, route_points[0])
                }
                
                terrain_analysis['terrain_segments'].append(segment)
                terrain_analysis['terrain_distribution'][terrain_type] += 1
                
                time.sleep(0.1)  # Rate limiting
            
            # Calculate overall classification
            distribution = terrain_analysis['terrain_distribution']
            total_segments = len(terrain_analysis['terrain_segments'])
            
            if total_segments > 0:
                urban_pct = (distribution['urban'] / total_segments) * 100
                rural_pct = (distribution['rural'] / total_segments) * 100
                
                if urban_pct > 60:
                    terrain_analysis['overall_classification'] = 'predominantly_urban'
                elif rural_pct > 60:
                    terrain_analysis['overall_classification'] = 'predominantly_rural'
                elif urban_pct > 30:
                    terrain_analysis['overall_classification'] = 'mixed_urban'
                else:
                    terrain_analysis['overall_classification'] = 'mixed_rural'
            
            print(f"✅ Terrain classification complete: {terrain_analysis['overall_classification']}")
            return terrain_analysis
            
        except Exception as e:
            logger.error(f"Error in terrain classification: {e}")
            return terrain_analysis
    
    def identify_major_highways(self, route_data: Dict) -> Dict:
        """JMP Feature 3: Major highways identification"""
        
        highway_analysis = {
            'major_highways': [],
            'highway_segments': [],
            'total_highway_distance': 0,
            'highway_percentage': 0
        }
        
        try:
            route_points = route_data.get('route_points', [])
            if not route_points:
                return highway_analysis
            
            # Use Google Directions API with detailed steps
            start_point = route_points[0]
            end_point = route_points[-1]
            
            directions = self.get_detailed_directions(start_point, end_point)
            
            if directions and 'routes' in directions:
                route = directions['routes'][0]
                
                for leg in route.get('legs', []):
                    for step in leg.get('steps', []):
                        instruction = step.get('html_instructions', '').lower()
                        maneuver = step.get('maneuver', '')
                        
                        # Identify highway segments
                        if self.is_highway_instruction(instruction, maneuver):
                            highway_info = self.extract_highway_info(instruction, step)
                            if highway_info:
                                highway_analysis['highway_segments'].append(highway_info)
                                
                                # Add to major highways list if not already present
                                highway_name = highway_info.get('highway_name')
                                if highway_name and highway_name not in [h['name'] for h in highway_analysis['major_highways']]:
                                    highway_analysis['major_highways'].append({
                                        'name': highway_name,
                                        'type': highway_info.get('highway_type'),
                                        'first_encounter_distance': highway_info.get('distance_from_start')
                                    })
            
            # Calculate highway statistics
            total_distance = self.parse_distance_to_km(route_data.get('distance', '0 km'))
            highway_distance = sum([seg.get('distance_km', 0) for seg in highway_analysis['highway_segments']])
            
            highway_analysis['total_highway_distance'] = highway_distance
            highway_analysis['highway_percentage'] = (highway_distance / total_distance * 100) if total_distance > 0 else 0
            
            print(f"✅ Major highways identified: {len(highway_analysis['major_highways'])} highways")
            return highway_analysis
            
        except Exception as e:
            logger.error(f"Error identifying major highways: {e}")
            return highway_analysis
    
    def generate_color_coded_risk_map(self, route_data: Dict, map_size: str = "640x640") -> str:
        """JMP Feature 4: Color-coded map visualization"""
        
        try:
            route_points = route_data.get('route_points', [])
            sharp_turns = route_data.get('sharp_turns', [])
            
            if not route_points:
                return None
            
            # Calculate map center
            center_lat = sum(point[0] for point in route_points) / len(route_points)
            center_lng = sum(point[1] for point in route_points) / len(route_points)
            
            # Create color-coded markers based on risk levels
            markers = []
            
            # Route path (blue)
            path_points = route_points[::5]  # Sample every 5th point
            path_string = '|'.join([f"{point[0]},{point[1]}" for point in path_points])
            
            # Add risk-based markers
            for i, turn in enumerate(sharp_turns[:15]):  # Limit to 15 for URL length
                angle = turn.get('angle', 0)
                lat, lng = turn.get('lat'), turn.get('lng')
                
                if angle > 80:
                    color = 'red'
                    label = 'H'  # High risk
                elif angle > 70:
                    color = 'orange' 
                    label = 'M'  # Medium risk
                else:
                    color = 'yellow'
                    label = 'L'  # Low risk
                
                markers.append(f"markers=color:{color}|label:{label}|{lat},{lng}")
            
            # Create Static Maps URL
            base_url = "https://maps.googleapis.com/maps/api/staticmap"
            params = [
                f"center={center_lat},{center_lng}",
                "zoom=10",
                f"size={map_size}",
                "maptype=roadmap",
                f"path=color:0x0000ff|weight:3|{path_string}"
            ]
            
            params.extend(markers)
            params.append(f"key={self.google_api_key}")
            
            url = f"{base_url}?" + "&".join(params)
            
            print("✅ Color-coded risk map URL generated")
            return url
            
        except Exception as e:
            logger.error(f"Error generating color-coded map: {e}")
            return None
    
    def analyze_time_specific_congestion(self, route_points: List) -> Dict:
        """JMP Feature 5: Time-specific congestion mapping"""
        
        congestion_analysis = {
            'peak_hours': {
                'morning': {'start': '07:00', 'end': '10:00', 'segments': []},
                'evening': {'start': '17:00', 'end': '20:00', 'segments': []},
                'night': {'start': '22:00', 'end': '06:00', 'segments': []}
            },
            'congestion_hotspots': [],
            'time_recommendations': []
        }
        
        try:
            # Sample key points for congestion analysis
            sample_points = route_points[::max(1, len(route_points)//10)]
            
            for i, point in enumerate(sample_points):
                lat, lng = point[0], point[1]
                
                # Get traffic information for different times
                for period, time_data in congestion_analysis['peak_hours'].items():
                    traffic_info = self.get_traffic_info_for_time(lat, lng, period)
                    
                    if traffic_info:
                        segment = {
                            'location': f"Segment {i+1}",
                            'coordinates': {'lat': lat, 'lng': lng},
                            'traffic_level': traffic_info.get('traffic_level', 'unknown'),
                            'delay_minutes': traffic_info.get('delay_minutes', 0),
                            'recommended_speed': traffic_info.get('recommended_speed', 'normal')
                        }
                        time_data['segments'].append(segment)
                
                time.sleep(0.2)  # Rate limiting
            
            # Generate recommendations
            congestion_analysis['time_recommendations'] = self.generate_time_recommendations(congestion_analysis)
            
            print("✅ Time-specific congestion analysis complete")
            return congestion_analysis
            
        except Exception as e:
            logger.error(f"Error in congestion analysis: {e}")
            return congestion_analysis
    
    def enhanced_elevation_analysis(self, route_points: List) -> Dict:
        """JMP Feature 6: Enhanced ascents/descents with coordinates"""
        
        elevation_enhancement = {
            'ascent_segments': [],
            'descent_segments': [],
            'elevation_risk_points': [],
            'gradient_statistics': {}
        }
        
        try:
            # Get elevation data for all points
            elevation_data = self.get_bulk_elevation_data(route_points)
            
            if not elevation_data:
                return elevation_enhancement
            
            # Analyze ascents and descents
            for i in range(1, len(elevation_data)):
                current = elevation_data[i]
                previous = elevation_data[i-1]
                
                elevation_diff = current['elevation'] - previous['elevation']
                distance_diff = current.get('distance_from_start', 0) - previous.get('distance_from_start', 0)
                
                if distance_diff > 0:
                    gradient = (elevation_diff / (distance_diff * 1000)) * 100  # Percentage
                    
                    segment = {
                        'start_coordinates': previous['location'],
                        'end_coordinates': current['location'],
                        'elevation_change': elevation_diff,
                        'gradient_percent': gradient,
                        'distance_km': distance_diff,
                        'segment_type': 'ascent' if elevation_diff > 0 else 'descent'
                    }
                    
                    # Categorize significant ascents/descents
                    if abs(gradient) > 5:  # Significant gradient
                        if elevation_diff > 0:
                            elevation_enhancement['ascent_segments'].append(segment)
                        else:
                            elevation_enhancement['descent_segments'].append(segment)
                    
                    # Identify risk points
                    if abs(gradient) > 8:  # High risk gradient
                        risk_point = {
                            'coordinates': current['location'],
                            'risk_level': 'HIGH' if abs(gradient) > 12 else 'MEDIUM',
                            'gradient_percent': gradient,
                            'elevation_m': current['elevation'],
                            'risk_type': 'steep_ascent' if gradient > 0 else 'steep_descent'
                        }
                        elevation_enhancement['elevation_risk_points'].append(risk_point)
            
            # Calculate statistics
            all_gradients = [abs(seg['gradient_percent']) for seg in elevation_enhancement['ascent_segments'] + elevation_enhancement['descent_segments']]
            
            elevation_enhancement['gradient_statistics'] = {
                'max_ascent_gradient': max([seg['gradient_percent'] for seg in elevation_enhancement['ascent_segments']], default=0),
                'max_descent_gradient': min([seg['gradient_percent'] for seg in elevation_enhancement['descent_segments']], default=0),
                'average_gradient': sum(all_gradients) / len(all_gradients) if all_gradients else 0,
                'total_ascent_segments': len(elevation_enhancement['ascent_segments']),
                'total_descent_segments': len(elevation_enhancement['descent_segments'])
            }
            
            print(f"✅ Enhanced elevation analysis: {len(elevation_enhancement['elevation_risk_points'])} risk points identified")
            return elevation_enhancement
            
        except Exception as e:
            logger.error(f"Error in enhanced elevation analysis: {e}")
            return elevation_enhancement
    
    def generate_printable_coordinate_tables(self, route_data: Dict) -> Dict:
        """JMP Feature 8: Printable lat/long tables with enhanced data"""
        
        printable_tables = {
            'main_route_table': [],
            'critical_points_table': [],
            'poi_coordinates_table': [],
            'risk_points_table': []
        }
        
        try:
            route_points = route_data.get('route_points', [])
            sharp_turns = route_data.get('sharp_turns', [])
            
            # Main route table (sampled points)
            sample_interval = max(1, len(route_points) // 50)  # Max 50 points for printability
            sampled_points = route_points[::sample_interval]
            
            for i, point in enumerate(sampled_points):
                lat, lng = point[0], point[1]
                
                route_entry = {
                    'point_number': i + 1,
                    'latitude': f"{lat:.6f}",
                    'longitude': f"{lng:.6f}",
                    'coordinates_dms': self.convert_to_dms(lat, lng),
                    'distance_from_start': self.calculate_distance_from_start(point, route_points[0]),
                    'location_description': self.get_location_description(lat, lng)
                }
                printable_tables['main_route_table'].append(route_entry)
            
            # Critical points table (sharp turns)
            for i, turn in enumerate(sharp_turns):
                critical_entry = {
                    'turn_number': i + 1,
                    'latitude': f"{turn.get('lat', 0):.6f}",
                    'longitude': f"{turn.get('lng', 0):.6f}",
                    'turn_angle': f"{turn.get('angle', 0):.1f}°",
                    'danger_level': turn.get('classification', 'Unknown'),
                    'recommended_speed': '15-20 km/h' if turn.get('angle', 0) > 80 else '25-30 km/h'
                }
                printable_tables['critical_points_table'].append(critical_entry)
            
            # POI coordinates table
            poi_categories = ['hospitals', 'petrol_bunks', 'schools', 'food_stops']
            poi_counter = 1
            
            for category in poi_categories:
                pois = route_data.get(category, {})
                for poi_name, poi_location in list(pois.items())[:5]:  # Limit to 5 per category
                    # Estimate coordinates (in production, use actual POI coordinates)
                    est_coords = self.estimate_poi_coordinates(poi_name, poi_location, route_points)
                    
                    poi_entry = {
                        'poi_number': poi_counter,
                        'poi_type': category.replace('_', ' ').title(),
                        'name': poi_name[:30],
                        'latitude': f"{est_coords[0]:.6f}",
                        'longitude': f"{est_coords[1]:.6f}",
                        'location': poi_location[:40]
                    }
                    printable_tables['poi_coordinates_table'].append(poi_entry)
                    poi_counter += 1
            
            print("✅ Printable coordinate tables generated")
            return printable_tables
            
        except Exception as e:
            logger.error(f"Error generating printable tables: {e}")
            return printable_tables
    
    def create_risk_emergency_elevation_layers(self, route_data: Dict) -> str:
        """JMP Feature 9: Risk/emergency/elevation layers map"""
        
        try:
            route_points = route_data.get('route_points', [])
            sharp_turns = route_data.get('sharp_turns', [])
            
            if not route_points:
                return None
            
            # Calculate map center and zoom
            center_lat = sum(point[0] for point in route_points) / len(route_points)
            center_lng = sum(point[1] for point in route_points) / len(route_points)
            
            # Create layered map with multiple data types
            markers = []
            
            # Risk layer (sharp turns)
            for turn in sharp_turns[:10]:
                angle = turn.get('angle', 0)
                if angle > 70:
                    color = 'red' if angle > 80 else 'orange'
                    markers.append(f"markers=color:{color}|label:R|{turn['lat']},{turn['lng']}")
            
            # Emergency layer (hospitals from POI data)
            hospitals = route_data.get('hospitals', {})
            for i, (hospital, location) in enumerate(list(hospitals.items())[:5]):
                # Estimate coordinates for hospitals
                est_coords = self.estimate_poi_coordinates(hospital, location, route_points)
                markers.append(f"markers=color:blue|label:H|{est_coords[0]},{est_coords[1]}")
            
            # Elevation layer (elevation changes)
            elevation_data = route_data.get('elevation', [])
            for elev in elevation_data[:5]:
                if 'location' in elev:
                    loc = elev['location']
                    if loc.get('lat') and loc.get('lng'):
                        markers.append(f"markers=color:brown|label:E|{loc['lat']},{loc['lng']}")
            
            # Route path
            path_points = route_points[::8]  # Sample for URL length
            path_string = '|'.join([f"{point[0]},{point[1]}" for point in path_points])
            
            # Create Static Maps URL
            base_url = "https://maps.googleapis.com/maps/api/staticmap"
            params = [
                f"center={center_lat},{center_lng}",
                "zoom=10",
                "size=800x600",
                "maptype=roadmap",
                f"path=color:0x0000ff|weight:3|{path_string}"
            ]
            
            params.extend(markers)
            params.append(f"key={self.google_api_key}")
            
            url = f"{base_url}?" + "&".join(params)
            
            print("✅ Risk/Emergency/Elevation layers map generated")
            return url
            
        except Exception as e:
            logger.error(f"Error creating layered map: {e}")
            return None
    
    # Helper methods
    def reverse_geocode(self, lat: float, lng: float) -> Dict:
        """Get detailed location information from coordinates"""
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'latlng': f"{lat},{lng}",
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK' and data.get('results'):
                    return data['results'][0]
            
            return {}
            
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return {}
    
    def determine_terrain_type(self, location_info: Dict) -> str:
        """Determine terrain type from location information"""
        types = location_info.get('types', [])
        
        # Check for urban indicators
        urban_indicators = ['locality', 'sublocality', 'neighborhood', 'administrative_area_level_2']
        if any(indicator in types for indicator in urban_indicators):
            return 'urban'
        
        # Check for semi-urban indicators
        semi_urban_indicators = ['administrative_area_level_3', 'sublocality_level_1']
        if any(indicator in types for indicator in semi_urban_indicators):
            return 'semi_urban'
        
        # Default to rural
        return 'rural'
    
    def get_detailed_directions(self, start_point: List, end_point: List) -> Dict:
        """Get detailed directions with highway information"""
        try:
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': f"{start_point[0]},{start_point[1]}",
                'destination': f"{end_point[0]},{end_point[1]}",
                'key': self.google_api_key,
                'alternatives': 'false'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            
            return {}
            
        except Exception as e:
            logger.error(f"Directions API error: {e}")
            return {}
    
    def is_highway_instruction(self, instruction: str, maneuver: str) -> bool:
        """Check if instruction indicates highway travel"""
        highway_keywords = ['highway', 'expressway', 'nh-', 'sh-', 'freeway', 'motorway']
        return any(keyword in instruction for keyword in highway_keywords)
    
    def extract_highway_info(self, instruction: str, step: Dict) -> Dict:
        """Extract highway information from direction step"""
        try:
            # Simple highway name extraction
            highway_name = "Unknown Highway"
            if 'nh-' in instruction:
                highway_name = instruction.split('nh-')[1].split()[0]
                highway_name = f"NH-{highway_name}"
            elif 'sh-' in instruction:
                highway_name = instruction.split('sh-')[1].split()[0]
                highway_name = f"SH-{highway_name}"
            
            return {
                'highway_name': highway_name,
                'highway_type': 'National Highway' if 'nh-' in instruction else 'State Highway',
                'distance_km': step.get('distance', {}).get('value', 0) / 1000,
                'duration_minutes': step.get('duration', {}).get('value', 0) / 60
            }
            
        except Exception:
            return None
    
    def get_traffic_info_for_time(self, lat: float, lng: float, time_period: str) -> Dict:
        """Get traffic information for specific time period"""
        # This would require Google Maps Roads API or Traffic API
        # For now, return estimated data based on location type
        try:
            location_info = self.reverse_geocode(lat, lng)
            types = location_info.get('types', [])
            
            # Estimate traffic based on location type
            if any(t in types for t in ['locality', 'sublocality']):
                return {
                    'traffic_level': 'heavy' if time_period in ['morning', 'evening'] else 'moderate',
                    'delay_minutes': 15 if time_period in ['morning', 'evening'] else 5,
                    'recommended_speed': 'reduced'
                }
            else:
                return {
                    'traffic_level': 'light',
                    'delay_minutes': 0,
                    'recommended_speed': 'normal'
                }
                
        except Exception:
            return {}
    
    def get_bulk_elevation_data(self, route_points: List) -> List[Dict]:
        """Get elevation data for multiple points"""
        try:
            # Sample points for elevation (Google has limits)
            sample_points = route_points[::max(1, len(route_points)//100)]
            
            locations = '|'.join([f"{point[0]},{point[1]}" for point in sample_points])
            
            url = "https://maps.googleapis.com/maps/api/elevation/json"
            params = {
                'locations': locations,
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for i, result in enumerate(data.get('results', [])):
                    results.append({
                        'location': result.get('location', {}),
                        'elevation': result.get('elevation', 0),
                        'distance_from_start': self.calculate_distance_from_start(
                            [result.get('location', {}).get('lat', 0), 
                             result.get('location', {}).get('lng', 0)], 
                            route_points[0]
                        )
                    })
                
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Bulk elevation data error: {e}")
            return []
    
    def convert_to_dms(self, lat: float, lng: float) -> str:
        """Convert decimal degrees to degrees, minutes, seconds"""
        try:
            def dd_to_dms(dd):
                d = int(dd)
                m = int((dd - d) * 60)
                s = ((dd - d) * 60 - m) * 60
                return d, m, s
            
            lat_d, lat_m, lat_s = dd_to_dms(abs(lat))
            lng_d, lng_m, lng_s = dd_to_dms(abs(lng))
            
            lat_dir = 'N' if lat >= 0 else 'S'
            lng_dir = 'E' if lng >= 0 else 'W'
            
            return f"{lat_d}°{lat_m}'{lat_s:.1f}\"{lat_dir}, {lng_d}°{lng_m}'{lng_s:.1f}\"{lng_dir}"
            
        except Exception:
            return f"{lat:.6f}, {lng:.6f}"
    
    def get_location_description(self, lat: float, lng: float) -> str:
        """Get brief location description"""
        try:
            location_info = self.reverse_geocode(lat, lng)
            formatted_address = location_info.get('formatted_address', '')
            
            # Extract key components
            if formatted_address:
                parts = formatted_address.split(',')
                return parts[0] if parts else 'Unknown Location'
            
            return 'Unknown Location'
            
        except Exception:
            return 'Unknown Location'
    
    def estimate_poi_coordinates(self, poi_name: str, poi_location: str, route_points: List) -> Tuple[float, float]:
        """Estimate POI coordinates based on route"""
        try:
            # Simple estimation - distribute along route
            import hashlib
            hash_value = int(hashlib.md5(poi_name.encode()).hexdigest(), 16)
            index = hash_value % len(route_points)
            
            base_point = route_points[index]
            # Add small random offset
            offset = (hash_value % 1000) / 100000  # Small offset
            
            return (base_point[0] + offset, base_point[1] + offset)
            
        except Exception:
            if route_points:
                return (route_points[0][0], route_points[0][1])
            return (0.0, 0.0)
    
    def calculate_distance_from_start(self, point: List, start_point: List) -> float:
        """Calculate distance from start point"""
        try:
            from geopy.distance import geodesic
            return geodesic(start_point, point).kilometers
        except Exception:
            return 0.0
    
    def parse_distance_to_km(self, distance_str: str) -> float:
        """Parse distance string to kilometers"""
        try:
            return float(distance_str.lower().replace('km', '').replace(',', '').strip())
        except Exception:
            return 0.0
    
    def generate_time_recommendations(self, congestion_analysis: Dict) -> List[str]:
        """Generate time-based travel recommendations"""
        recommendations = []
        
        peak_hours = congestion_analysis.get('peak_hours', {})
        
        # Analyze each time period
        for period, data in peak_hours.items():
            segments = data.get('segments', [])
            if segments:
                high_traffic_count = len([s for s in segments if s.get('traffic_level') == 'heavy'])
                
                if high_traffic_count > len(segments) * 0.5:  # More than 50% segments have heavy traffic
                    if period == 'morning':
                        recommendations.append("Avoid travel during 07:00-10:00 (morning peak hours)")
                    elif period == 'evening':
                        recommendations.append("Avoid travel during 17:00-20:00 (evening peak hours)")
                    elif period == 'night':
                        recommendations.append("Night travel (22:00-06:00) may have traffic restrictions")
        
        # Add general recommendations
        recommendations.extend([
            "Plan extra 30-45 minutes during peak hours",
            "Monitor real-time traffic before departure",
            "Consider alternate routes during congestion"
        ])
        
        return recommendations