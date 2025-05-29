# utils/heavy_vehicle_analyzer.py - Real Google API Integration

import requests
import json
import logging
from geopy.distance import geodesic
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class HeavyVehicleRouteAnalyzer:
    """Analyze route suitability for heavy vehicles using Google APIs"""
    
    def __init__(self, google_api_key):
        self.google_api_key = google_api_key
        
        # Heavy vehicle specifications
        self.heavy_vehicle_specs = {
            "length": 18.75,  # meters (max legal length in India)
            "width": 2.5,     # meters
            "height": 4.2,    # meters  
            "weight": 49000,  # kg (GVW)
            "turning_radius": 12.5,  # meters
            "ground_clearance": 0.23,  # meters
            "fuel_consumption": 3.5,   # km/liter loaded
            "max_speed_urban": 40,     # km/h
            "max_speed_highway": 80,   # km/h
            "mandatory_rest_interval": 4.5  # hours
        }
    
    def analyze_heavy_vehicle_suitability(self, route_data: Dict) -> Dict:
        """Complete heavy vehicle route analysis using Google APIs"""
        
        route_points = route_data.get('route_points', [])
        if not route_points:
            return {'error': 'No route points available'}
        
        print("🚛 Starting Heavy Vehicle Route Analysis with Google APIs...")
        
        analysis = {
            'travel_time_analysis': self.analyze_adjusted_travel_time(route_data),
            'road_infrastructure': self.analyze_road_suitability(route_points),
            'turning_capability': self.analyze_turning_requirements(route_data),
            'fuel_planning': self.analyze_fuel_requirements(route_data),
            'parking_facilities': self.analyze_parking_availability(route_points),
            'load_restrictions': self.analyze_load_restrictions(route_points),
            'compliance_score': 0,
            'critical_issues': [],
            'recommendations': []
        }
        
        # Calculate overall compliance score
        analysis['compliance_score'] = self.calculate_heavy_vehicle_score(analysis)
        
        # Generate recommendations
        analysis['recommendations'] = self.generate_heavy_vehicle_recommendations(analysis)
        
        return analysis
    
    def analyze_adjusted_travel_time(self, route_data: Dict) -> Dict:
        """Analyze travel time adjustments for heavy vehicles"""
        
        base_duration = route_data.get('duration', '0 hours')
        base_hours = self.parse_duration_to_hours(base_duration)
        distance_km = self.parse_distance_to_km(route_data.get('distance', '0 km'))
        
        # Heavy vehicle speed adjustments
        speed_reduction_factors = {
            'urban_areas': 0.7,      # 30% slower in cities
            'ghat_roads': 0.5,       # 50% slower on hills  
            'traffic_congestion': 0.6, # 40% slower in traffic
            'sharp_turns': 0.8       # 20% slower on curves
        }
        
        # Calculate adjusted time based on route characteristics
        sharp_turns_count = len(route_data.get('sharp_turns', []))
        ghat_factor = 1.5 if sharp_turns_count > 20 else 1.2  # Assume ghats if many turns
        
        adjusted_hours = base_hours * ghat_factor
        
        # Add mandatory rest stops (every 4.5 hours)
        rest_stops_needed = int(adjusted_hours / 4.5)
        rest_time_hours = rest_stops_needed * 0.75  # 45 min per stop
        
        total_travel_time = adjusted_hours + rest_time_hours
        
        # Add loading/unloading buffer
        operational_buffer = 3.0  # 3 hours for operations
        total_time_with_buffer = total_travel_time + operational_buffer
        
        return {
            'base_travel_time': f"{base_hours:.1f} hours",
            'heavy_vehicle_adjusted': f"{adjusted_hours:.1f} hours",
            'mandatory_rest_stops': rest_stops_needed,
            'rest_time_required': f"{rest_time_hours:.1f} hours",
            'operational_buffer': f"{operational_buffer:.1f} hours",
            'total_realistic_time': f"{total_time_with_buffer:.1f} hours",
            'time_increase_percentage': f"{((total_time_with_buffer - base_hours) / base_hours * 100):.0f}%",
            'analysis_status': 'completed'
        }
    
    def analyze_road_suitability(self, route_points: List) -> Dict:
        """Analyze road infrastructure using Google Roads API"""
        
        try:
            # Sample route points for analysis
            sample_points = route_points[::max(1, len(route_points)//10)][:10]
            
            road_analysis = []
            bridge_concerns = []
            width_issues = []
            
            for i, point in enumerate(sample_points):
                lat, lng = point[0], point[1]
                
                # Get road information using Google Roads API
                road_info = self.get_road_information(lat, lng)
                
                if road_info:
                    # Analyze road characteristics
                    road_type = road_info.get('road_type', 'unknown')
                    estimated_width = self.estimate_road_width(road_type)
                    
                    analysis_point = {
                        'location': f"Point {i+1}",
                        'coordinates': {'lat': lat, 'lng': lng},
                        'road_type': road_type,
                        'estimated_width': estimated_width,
                        'suitability': self.assess_road_suitability(road_type, estimated_width),
                        'concerns': self.identify_road_concerns(road_type, estimated_width)
                    }
                    
                    road_analysis.append(analysis_point)
                    
                    # Collect specific issues
                    if estimated_width < 7.5:  # Heavy vehicle needs 7.5m
                        width_issues.append(analysis_point)
                    
                    if 'bridge' in road_info.get('features', []):
                        bridge_concerns.append(analysis_point)
            
            # Use Google Places API to find bridges along route
            bridges_found = self.find_bridges_along_route(sample_points)
            
            return {
                'total_points_analyzed': len(road_analysis),
                'road_analysis': road_analysis,
                'width_suitable_percentage': self.calculate_width_suitability(road_analysis),
                'bridge_locations': bridges_found,
                'bridge_weight_validation': 'REQUIRED - Manual verification needed',
                'width_concerns': len(width_issues),
                'critical_width_points': width_issues[:5],  # Top 5 concerns
                'overhead_clearance_status': 'REQUIRES FIELD VERIFICATION',
                'analysis_status': 'completed_with_google_apis'
            }
            
        except Exception as e:
            logger.error(f"Road suitability analysis error: {e}")
            return {
                'error': str(e),
                'analysis_status': 'failed',
                'manual_verification_required': True
            }
    
    def get_road_information(self, lat: float, lng: float) -> Dict:
        """Get road information using Google Roads API"""
        try:
            # Use Google Roads API to get road information
            url = "https://roads.googleapis.com/v1/nearestRoads"
            params = {
                'points': f"{lat},{lng}",
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                roads = data.get('snappedPoints', [])
                
                if roads:
                    road = roads[0]
                    place_id = road.get('placeId')
                    
                    # Get additional details using Places API
                    place_details = self.get_place_details(place_id)
                    
                    return {
                        'place_id': place_id,
                        'road_type': self.classify_road_type(place_details),
                        'features': place_details.get('types', [])
                    }
            
            return None
            
        except Exception as e:
            logger.warning(f"Roads API error for {lat}, {lng}: {e}")
            return None
    
    def get_place_details(self, place_id: str) -> Dict:
        """Get place details using Google Places API"""
        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                'place_id': place_id,
                'fields': 'types,name,geometry',
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json().get('result', {})
            
            return {}
            
        except Exception as e:
            logger.warning(f"Places API error for {place_id}: {e}")
            return {}
    
    def classify_road_type(self, place_details: Dict) -> str:
        """Classify road type from place details"""
        types = place_details.get('types', [])
        name = place_details.get('name', '').lower()
        
        # Classification based on Google types and naming
        if 'route' in types:
            if any(highway in name for highway in ['nh', 'national highway', 'expressway']):
                return 'national_highway'
            elif any(state in name for state in ['sh', 'state highway']):
                return 'state_highway'
            else:
                return 'major_road'
        
        return 'local_road'
    
    def estimate_road_width(self, road_type: str) -> float:
        """Estimate road width based on type"""
        width_estimates = {
            'national_highway': 12.0,    # meters
            'expressway': 15.0,
            'state_highway': 10.0,
            'major_road': 8.0,
            'local_road': 6.0,
            'unknown': 7.0
        }
        
        return width_estimates.get(road_type, 7.0)
    
    def assess_road_suitability(self, road_type: str, width: float) -> str:
        """Assess road suitability for heavy vehicles"""
        min_width_required = 7.5  # meters for safe heavy vehicle operation
        
        if width >= min_width_required:
            if road_type in ['national_highway', 'expressway']:
                return 'EXCELLENT'
            elif road_type in ['state_highway', 'major_road']:
                return 'GOOD'
            else:
                return 'ADEQUATE'
        else:
            return 'UNSUITABLE'
    
    def identify_road_concerns(self, road_type: str, width: float) -> List[str]:
        """Identify specific concerns for heavy vehicles"""
        concerns = []
        
        if width < 7.5:
            concerns.append(f"Width {width}m insufficient for safe heavy vehicle operation")
        
        if road_type == 'local_road':
            concerns.append("Local road may have weight restrictions")
            concerns.append("Surface condition unknown - verification required")
        
        if width < 10.0:
            concerns.append("Limited overtaking opportunities")
        
        return concerns
    
    def find_bridges_along_route(self, route_points: List) -> List[Dict]:
        """Find bridges along route using Google Places API"""
        bridges = []
        
        try:
            for point in route_points[::2]:  # Check every other point
                lat, lng = point[0], point[1]
                
                # Search for bridges nearby
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                params = {
                    'location': f"{lat},{lng}",
                    'radius': 1000,  # 1km radius
                    'keyword': 'bridge',
                    'key': self.google_api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    for bridge in results[:2]:  # Max 2 bridges per search point
                        bridge_info = {
                            'name': bridge.get('name', 'Unknown Bridge'),
                            'location': bridge.get('vicinity', 'Unknown Location'),
                            'coordinates': bridge.get('geometry', {}).get('location', {}),
                            'weight_limit_status': 'VERIFICATION REQUIRED',
                            'heavy_vehicle_suitability': 'UNKNOWN - MANUAL CHECK NEEDED'
                        }
                        bridges.append(bridge_info)
            
            return bridges[:10]  # Limit to 10 bridges
            
        except Exception as e:
            logger.error(f"Bridge finding error: {e}")
            return []
    
    def analyze_turning_requirements(self, route_data: Dict) -> Dict:
        """Analyze turning capability using sharp turns data"""
        
        sharp_turns = route_data.get('sharp_turns', [])
        
        # Classify turns by heavy vehicle capability
        problematic_turns = []
        impossible_turns = []
        caution_turns = []
        
        for turn in sharp_turns:
            angle = turn.get('angle', 0)
            
            # Heavy vehicle turning analysis
            if angle > 90:
                # Extremely sharp - may be impossible for heavy vehicles
                turn_analysis = {
                    **turn,
                    'heavy_vehicle_capability': 'IMPOSSIBLE',
                    'required_turning_radius': f"{self.heavy_vehicle_specs['turning_radius']}m",
                    'estimated_space_needed': f"{self.heavy_vehicle_specs['turning_radius'] * 2}m",
                    'recommendation': 'AVOID - Find alternate route'
                }
                impossible_turns.append(turn_analysis)
                
            elif angle > 70:
                # Very difficult turns
                turn_analysis = {
                    **turn,
                    'heavy_vehicle_capability': 'VERY DIFFICULT',
                    'required_turning_radius': f"{self.heavy_vehicle_specs['turning_radius']}m",
                    'recommendation': 'Multi-point turn may be required'
                }
                problematic_turns.append(turn_analysis)
                
            elif angle > 45:
                # Requires caution
                turn_analysis = {
                    **turn,
                    'heavy_vehicle_capability': 'POSSIBLE WITH CAUTION',
                    'recommendation': 'Reduce speed to 15-20 km/h'
                }
                caution_turns.append(turn_analysis)
        
        return {
            'total_sharp_turns': len(sharp_turns),
            'impossible_turns': impossible_turns,
            'very_difficult_turns': problematic_turns,
            'caution_required_turns': caution_turns,
            'turning_radius_requirement': f"{self.heavy_vehicle_specs['turning_radius']}m",
            'route_navigability': 'PROBLEMATIC' if impossible_turns else 'DIFFICULT' if problematic_turns else 'MANAGEABLE',
            'alternate_route_recommended': len(impossible_turns) > 0,
            'analysis_status': 'completed'
        }
    
    def analyze_fuel_requirements(self, route_data: Dict) -> Dict:
        """Analyze fuel planning for heavy vehicles"""
        
        distance_km = self.parse_distance_to_km(route_data.get('distance', '0 km'))
        fuel_stations = route_data.get('petrol_bunks', {})
        
        # Heavy vehicle fuel calculations
        loaded_consumption = self.heavy_vehicle_specs['fuel_consumption']  # km/L
        fuel_needed = distance_km / loaded_consumption
        
        # Add buffer for hills and traffic
        fuel_buffer = fuel_needed * 0.3  # 30% buffer
        total_fuel_needed = fuel_needed + fuel_buffer
        
        # Typical heavy vehicle fuel tank capacity
        tank_capacity = 400  # liters (typical for heavy trucks)
        range_per_tank = tank_capacity * loaded_consumption
        
        refuel_stops_needed = max(0, int(distance_km / range_per_tank))
        
        return {
            'route_distance': f"{distance_km:.1f} km",
            'fuel_consumption_rate': f"{loaded_consumption} km/L (loaded)",
            'base_fuel_required': f"{fuel_needed:.1f} L",
            'fuel_buffer_recommended': f"{fuel_buffer:.1f} L",
            'total_fuel_needed': f"{total_fuel_needed:.1f} L",
            'tank_capacity': f"{tank_capacity} L",
            'range_per_tank': f"{range_per_tank:.1f} km",
            'refuel_stops_needed': refuel_stops_needed,
            'fuel_stations_found': len(fuel_stations),
            'fuel_availability_status': 'ADEQUATE' if len(fuel_stations) >= refuel_stops_needed else 'INSUFFICIENT',
            'diesel_availability': 'High-speed diesel required for heavy vehicles',
            'analysis_status': 'completed'
        }
    
    def analyze_parking_availability(self, route_points: List) -> Dict:
        """Find truck parking facilities using Google Places API"""
        
        try:
            truck_parking = []
            rest_areas = []
            
            # Sample points along route for parking search
            sample_points = route_points[::max(1, len(route_points)//5)]
            
            for i, point in enumerate(sample_points[:5]):
                lat, lng = point[0], point[1]
                
                # Search for truck parking
                parking_data = self.search_truck_facilities(lat, lng, 'truck parking')
                truck_parking.extend(parking_data)
                
                # Search for rest areas
                rest_data = self.search_truck_facilities(lat, lng, 'rest area')
                rest_areas.extend(rest_data)
            
            return {
                'truck_parking_locations': truck_parking[:10],
                'rest_areas_found': rest_areas[:10],
                'overnight_parking_available': len(truck_parking) > 0,
                'security_status': 'VERIFICATION REQUIRED',
                'driver_facilities': 'Check individual locations',
                'parking_adequacy': 'ADEQUATE' if len(truck_parking) > 2 else 'LIMITED',
                'analysis_status': 'completed_with_google_places'
            }
            
        except Exception as e:
            logger.error(f"Parking analysis error: {e}")
            return {
                'error': str(e),
                'analysis_status': 'failed',
                'manual_verification_required': True
            }
    
    def search_truck_facilities(self, lat: float, lng: float, facility_type: str) -> List[Dict]:
        """Search for truck facilities using Google Places API"""
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': 10000,  # 10km radius
                'keyword': facility_type,
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                facilities = []
                for result in results[:3]:  # Top 3 per location
                    facility = {
                        'name': result.get('name', 'Unknown Facility'),
                        'location': result.get('vicinity', 'Unknown Location'),
                        'rating': result.get('rating', 'No rating'),
                        'coordinates': result.get('geometry', {}).get('location', {}),
                        'facility_type': facility_type,
                        'heavy_vehicle_access': 'VERIFICATION REQUIRED'
                    }
                    facilities.append(facility)
                
                return facilities
            
            return []
            
        except Exception as e:
            logger.warning(f"Truck facilities search error: {e}")
            return []
    
    def analyze_load_restrictions(self, route_points: List) -> Dict:
        """Analyze load and weight restrictions"""
        
        # This would ideally connect to government databases
        # For now, provide general analysis based on vehicle specs
        
        vehicle_weight = self.heavy_vehicle_specs['weight']
        legal_limits = {
            'gross_vehicle_weight': 49000,  # kg
            'front_axle_limit': 10200,      # kg
            'rear_axle_limit': 18500,       # kg
            'bridge_formula_compliance': True
        }
        
        return {
            'vehicle_gross_weight': f"{vehicle_weight} kg",
            'legal_gvw_limit': f"{legal_limits['gross_vehicle_weight']} kg",
            'weight_compliance': 'COMPLIANT' if vehicle_weight <= legal_limits['gross_vehicle_weight'] else 'OVERWEIGHT',
            'axle_load_distribution': {
                'front_axle_limit': f"{legal_limits['front_axle_limit']} kg",
                'rear_axle_limit': f"{legal_limits['rear_axle_limit']} kg",
                'compliance_status': 'REQUIRES WEIGHBRIDGE VERIFICATION'
            },
            'oversize_permit_required': self.check_oversize_requirements(),
            'bridge_weight_restrictions': 'MANUAL VERIFICATION REQUIRED',
            'analysis_status': 'completed'
        }
    
    def check_oversize_requirements(self) -> Dict:
        """Check if oversize permits are required"""
        specs = self.heavy_vehicle_specs
        
        legal_limits = {
            'length': 18.75,  # meters
            'width': 2.5,     # meters  
            'height': 4.2     # meters
        }
        
        oversize_required = (
            specs['length'] > legal_limits['length'] or
            specs['width'] > legal_limits['width'] or
            specs['height'] > legal_limits['height']
        )
        
        return {
            'permit_required': oversize_required,
            'dimensions_check': {
                'length_status': 'COMPLIANT' if specs['length'] <= legal_limits['length'] else 'OVERSIZE',
                'width_status': 'COMPLIANT' if specs['width'] <= legal_limits['width'] else 'OVERSIZE',
                'height_status': 'COMPLIANT' if specs['height'] <= legal_limits['height'] else 'OVERSIZE'
            }
        }
    
    # Helper methods
    def parse_duration_to_hours(self, duration_str: str) -> float:
        """Parse duration string to hours"""
        try:
            if "hour" in duration_str.lower():
                parts = duration_str.lower().split()
                for i, part in enumerate(parts):
                    if "hour" in part and i > 0:
                        return float(parts[i-1])
            elif "min" in duration_str.lower():
                parts = duration_str.lower().split()
                for i, part in enumerate(parts):
                    if "min" in part and i > 0:
                        return float(parts[i-1]) / 60
            return 8.0
        except:
            return 8.0
    
    def parse_distance_to_km(self, distance_str: str) -> float:
        """Parse distance string to kilometers"""
        try:
            distance_str = distance_str.lower().replace('km', '').replace(',', '').strip()
            return float(distance_str)
        except:
            return 100.0  # Default assumption
    
    def calculate_width_suitability(self, road_analysis: List) -> float:
        """Calculate percentage of route suitable for heavy vehicles"""
        if not road_analysis:
            return 0.0
        
        suitable_count = len([r for r in road_analysis if r.get('suitability') in ['EXCELLENT', 'GOOD', 'ADEQUATE']])
        return (suitable_count / len(road_analysis)) * 100
    
    def calculate_heavy_vehicle_score(self, analysis: Dict) -> int:
        """Calculate overall heavy vehicle suitability score"""
        score = 100
        
        # Deduct for turning issues
        turning = analysis.get('turning_capability', {})
        impossible_turns = len(turning.get('impossible_turns', []))
        difficult_turns = len(turning.get('very_difficult_turns', []))
        
        score -= impossible_turns * 25  # Major deduction for impossible turns
        score -= difficult_turns * 10   # Moderate deduction for difficult turns
        
        # Deduct for road infrastructure
        road_info = analysis.get('road_infrastructure', {})
        width_concerns = road_info.get('width_concerns', 0)
        score -= width_concerns * 15
        
        # Deduct for fuel availability
        fuel_info = analysis.get('fuel_planning', {})
        if fuel_info.get('fuel_availability_status') == 'INSUFFICIENT':
            score -= 20
        
        return max(0, min(100, score))
    
    def generate_heavy_vehicle_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate specific recommendations based on analysis"""
        recommendations = []
        
        # Turning capability recommendations
        turning = analysis.get('turning_capability', {})
        impossible_turns = turning.get('impossible_turns', [])
        
        if impossible_turns:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Route Navigation',
                'title': f'{len(impossible_turns)} Impossible Turns Detected',
                'description': 'Heavy vehicle cannot navigate these sharp turns safely',
                'actions': [
                    'Find alternate route avoiding these turn locations',
                    'Consider breaking load into smaller vehicles',
                    'Use escort vehicle for guidance',
                    'Plan multi-point turning maneuvers where possible'
                ]
            })
        
        # Road infrastructure recommendations
        road_info = analysis.get('road_infrastructure', {})
        width_concerns = road_info.get('width_concerns', 0)
        
        if width_concerns > 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Road Infrastructure',
                'title': f'{width_concerns} Road Width Concerns',
                'description': 'Some route sections may be too narrow for safe heavy vehicle operation',
                'actions': [
                    'Conduct physical road width measurement',
                    'Plan travel during low-traffic hours',
                    'Use escort vehicle on narrow sections',
                    'Coordinate with local traffic police'
                ]
            })
        
        # Travel time recommendations
        time_analysis = analysis.get('travel_time_analysis', {})
        if time_analysis.get('analysis_status') == 'completed':
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Travel Planning',
                'title': 'Adjusted Travel Time Required',
                'description': f"Heavy vehicle journey will take {time_analysis.get('total_realistic_time')} vs original estimate",
                'actions': [
                    f"Plan for {time_analysis.get('mandatory_rest_stops')} mandatory rest stops",
                    f"Add {time_analysis.get('operational_buffer')} for loading/unloading",
                    'Start journey early to avoid night driving',
                    'Inform consignee of realistic delivery time'
                ]
            })
        
        return recommendations