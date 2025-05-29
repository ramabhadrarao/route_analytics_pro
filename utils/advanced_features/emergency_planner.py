# utils/advanced_features/emergency_planner.py - FULLY IMPLEMENTABLE

import requests
import json
from typing import Dict, List
from geopy.distance import geodesic

class EmergencyPlanner:
    """Advanced emergency planning using Google APIs"""
    
    def __init__(self, google_api_key):
        self.google_api_key = google_api_key
    
    def analyze_emergency_preparedness(self, route_data: Dict) -> Dict:
        """Complete emergency preparedness analysis"""
        
        route_points = route_data.get('route_points', [])
        if not route_points:
            return {'error': 'No route points provided'}
        
        print("🚨 Starting Advanced Emergency Planning Analysis...")
        
        analysis = {
            'alternate_routes': self.find_alternate_routes(route_points),
            'emergency_services': self.map_emergency_services(route_points),
            'rerouting_options': self.calculate_rerouting_options(route_points),
            'emergency_contacts': self.get_emergency_contact_info(),
            'contingency_plans': self.generate_contingency_plans(route_points),
            'communication_dead_zones': route_data.get('network_coverage', {}).get('dead_zones', [])
        }
        
        return analysis
    
    def find_alternate_routes(self, route_points: List) -> Dict:
        """Find alternate routes using Google Directions API"""
        try:
            if len(route_points) < 2:
                return {'error': 'Insufficient route points'}
            
            start_point = route_points[0]
            end_point = route_points[-1]
            
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': f"{start_point[0]},{start_point[1]}",
                'destination': f"{end_point[0]},{end_point[1]}",
                'alternatives': 'true',
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK':
                    routes = data.get('routes', [])
                    
                    alternate_routes = []
                    for i, route in enumerate(routes[1:], 1):  # Skip first route (main route)
                        leg = route['legs'][0]
                        
                        alternate_route = {
                            'route_index': i,
                            'distance': leg.get('distance', {}).get('text', 'Unknown'),
                            'duration': leg.get('duration', {}).get('text', 'Unknown'),
                            'summary': route.get('summary', 'Alternate Route'),
                            'via_waypoints': self.extract_waypoints(route),
                            'suitability': self.assess_alternate_route_suitability(route)
                        }
                        alternate_routes.append(alternate_route)
                    
                    return {
                        'total_alternates': len(alternate_routes),
                        'routes': alternate_routes,
                        'recommendation': self.recommend_best_alternate(alternate_routes)
                    }
            
            return {'error': 'No alternate routes found'}
            
        except Exception as e:
            return {'error': f'Alternate route analysis failed: {str(e)}'}
    
    def map_emergency_services(self, route_points: List) -> Dict:
        """Map emergency services along route"""
        try:
            # Sample points along route for emergency services search
            sample_points = route_points[::max(1, len(route_points)//8)]  # 8 sample points
            
            emergency_services = {
                'hospitals': [],
                'police_stations': [],
                'fire_stations': [],
                'service_centers': [],
                'towing_services': []
            }
            
            service_types = {
                'hospitals': 'hospital',
                'police_stations': 'police',
                'fire_stations': 'fire_station', 
                'service_centers': 'car_repair',
                'towing_services': 'car_repair'
            }
            
            for point in sample_points:
                lat, lng = point[0], point[1]
                
                for service_key, service_type in service_types.items():
                    services = self.search_emergency_services(lat, lng, service_type)
                    emergency_services[service_key].extend(services)
            
            # Remove duplicates and sort by distance
            for service_key in emergency_services:
                emergency_services[service_key] = self.deduplicate_services(emergency_services[service_key])
            
            return {
                'emergency_services': emergency_services,
                'service_density': self.calculate_service_density(emergency_services),
                'coverage_gaps': self.identify_coverage_gaps(emergency_services, route_points),
                'emergency_preparedness_score': self.calculate_emergency_score(emergency_services)
            }
            
        except Exception as e:
            return {'error': f'Emergency services mapping failed: {str(e)}'}
    
    def search_emergency_services(self, lat: float, lng: float, service_type: str) -> List[Dict]:
        """Search for emergency services near a point"""
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': 15000,  # 15km radius
                'type': service_type,
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                services = []
                for result in results[:3]:  # Top 3 per location
                    service = {
                        'name': result.get('name', 'Unknown'),
                        'location': result.get('vicinity', 'Unknown Location'),
                        'coordinates': result.get('geometry', {}).get('location', {}),
                        'rating': result.get('rating', 'No rating'),
                        'place_id': result.get('place_id'),
                        'service_type': service_type,
                        'distance_from_route': self.calculate_distance_from_point(
                            result.get('geometry', {}).get('location', {}), lat, lng
                        )
                    }
                    services.append(service)
                
                return services
            
            return []
            
        except Exception as e:
            print(f"Emergency service search error: {e}")
            return []
    
    def calculate_rerouting_options(self, route_points: List) -> Dict:
        """Calculate rerouting options for different scenarios"""
        try:
            if len(route_points) < 4:
                return {'error': 'Route too short for rerouting analysis'}
            
            # Define critical rerouting points (25%, 50%, 75% of route)
            quarter_point = len(route_points) // 4
            half_point = len(route_points) // 2  
            three_quarter_point = (3 * len(route_points)) // 4
            
            rerouting_scenarios = []
            
            for scenario_name, start_index in [
                ('Early Route Blockage', quarter_point),
                ('Mid Route Blockage', half_point),
                ('Late Route Blockage', three_quarter_point)
            ]:
                if start_index < len(route_points) - 1:
                    reroute_option = self.calculate_emergency_reroute(
                        route_points[start_index], 
                        route_points[-1],
                        scenario_name
                    )
                    if reroute_option:
                        rerouting_scenarios.append(reroute_option)
            
            return {
                'rerouting_scenarios': rerouting_scenarios,
                'total_scenarios_analyzed': len(rerouting_scenarios),
                'best_contingency_point': self.identify_best_contingency_point(rerouting_scenarios)
            }
            
        except Exception as e:
            return {'error': f'Rerouting analysis failed: {str(e)}'}
    
    def calculate_emergency_reroute(self, from_point: List, to_point: List, scenario_name: str) -> Dict:
        """Calculate emergency reroute from a specific point"""
        try:
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': f"{from_point[0]},{from_point[1]}",
                'destination': f"{to_point[0]},{to_point[1]}",
                'alternatives': 'true',
                'avoid': 'tolls',  # Assume emergency scenario
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and data.get('routes'):
                    route = data['routes'][0]
                    leg = route['legs'][0]
                    
                    return {
                        'scenario': scenario_name,
                        'from_coordinates': from_point,
                        'to_coordinates': to_point,
                        'emergency_distance': leg.get('distance', {}).get('text', 'Unknown'),
                        'emergency_duration': leg.get('duration', {}).get('text', 'Unknown'),
                        'route_summary': route.get('summary', 'Emergency Route'),
                        'feasibility': 'HIGH'  # Assume feasible if Google returns route
                    }
            
            return None
            
        except Exception as e:
            print(f"Emergency reroute calculation error: {e}")
            return None
    
    def get_emergency_contact_info(self) -> Dict:
        """Get standard emergency contact information"""
        return {
            'national_emergency_numbers': {
                'Police': '100',
                'Fire Service': '101', 
                'Ambulance': '108',
                'Emergency Services': '112',
                'Highway Helpline': '1033'
            },
            'roadside_assistance': {
                'AAA India': '1800-425-5555',
                'RSA India': '1800-102-4444'
            },
            'traffic_helplines': {
                'National Highway Authority': '1033',
                'Traffic Police': '103'
            }
        }
    
    def generate_contingency_plans(self, route_points: List) -> List[Dict]:
        """Generate contingency plans for different emergency scenarios"""
        
        contingency_plans = [
            {
                'scenario': 'Vehicle Breakdown',
                'priority': 'HIGH',
                'immediate_actions': [
                    'Move vehicle to safe location (left shoulder)',
                    'Turn on hazard lights',
                    'Place reflective triangles 50m behind vehicle',
                    'Call roadside assistance: 1800-425-5555'
                ],
                'safety_precautions': [
                    'Exit vehicle from side away from traffic',
                    'Stand behind safety barrier if available',
                    'Wear high-visibility jacket',
                    'Keep emergency kit accessible'
                ]
            },
            {
                'scenario': 'Accident/Collision',
                'priority': 'CRITICAL',
                'immediate_actions': [
                    'Ensure personal safety first',
                    'Call emergency services: 112',
                    'Provide first aid if trained',
                    'Do not move injured persons unless in immediate danger'
                ],
                'documentation': [
                    'Take photos of accident scene',
                    'Exchange insurance information',
                    'Get witness contact details',
                    'Note police complaint number'
                ]
            },
            {
                'scenario': 'Road Closure/Traffic Jam',
                'priority': 'MEDIUM',
                'immediate_actions': [
                    'Check traffic apps for updates',
                    'Contact dispatch/family about delay',
                    'Find safe place to wait',
                    'Monitor fuel levels'
                ],
                'alternate_actions': [
                    'Use alternate route if available',
                    'Wait for traffic to clear',
                    'Take mandatory rest break',
                    'Update ETA with contacts'
                ]
            },
            {
                'scenario': 'Medical Emergency',
                'priority': 'CRITICAL',
                'immediate_actions': [
                    'Call ambulance: 108',
                    'Provide first aid if trained',
                    'Keep person calm and conscious',
                    'Locate nearest hospital'
                ],
                'information_to_provide': [
                    'Exact GPS location',
                    'Nature of medical emergency',
                    'Age and condition of patient',
                    'Visible injuries or symptoms'
                ]
            }
        ]
        
        return contingency_plans
    
    # Helper methods
    def extract_waypoints(self, route: Dict) -> List[str]:
        """Extract key waypoints from route"""
        try:
            steps = route.get('legs', [{}])[0].get('steps', [])
            waypoints = []
            
            for step in steps[:5]:  # First 5 major waypoints
                instruction = step.get('html_instructions', '')
                if any(keyword in instruction.lower() for keyword in ['highway', 'road', 'turn', 'exit']):
                    # Clean HTML tags
                    import re
                    clean_instruction = re.sub('<.*?>', '', instruction)
                    waypoints.append(clean_instruction[:50])
            
            return waypoints
        except:
            return ['Route waypoints not available']
    
    def assess_alternate_route_suitability(self, route: Dict) -> str:
        """Assess suitability of alternate route"""
        try:
            summary = route.get('summary', '').lower()
            
            # Check for highway routes (generally better for emergencies)
            if any(highway in summary for highway in ['highway', 'expressway', 'nh-']):
                return 'HIGH - Highway Route'
            elif 'toll' in summary:
                return 'MEDIUM - Toll Route'
            else:
                return 'MEDIUM - Local Roads'
        except:
            return 'UNKNOWN'
    
    def recommend_best_alternate(self, alternate_routes: List[Dict]) -> Dict:
        """Recommend best alternate route"""
        if not alternate_routes:
            return {'recommendation': 'No alternate routes available'}
        
        # Simple scoring: prefer highway routes and shorter distances
        best_route = max(alternate_routes, key=lambda r: (
            2 if 'HIGH' in r.get('suitability', '') else 1,
            -len(r.get('distance', '0 km'))  # Prefer shorter (negative for max)
        ))
        
        return {
            'recommended_route': best_route['route_index'],
            'reason': f"Best alternate: {best_route.get('summary', 'Alternate route')}",
            'suitability': best_route.get('suitability', 'MEDIUM')
        }
    
    def deduplicate_services(self, services: List[Dict]) -> List[Dict]:
        """Remove duplicate services and sort by distance"""
        seen_places = set()
        unique_services = []
        
        for service in services:
            place_id = service.get('place_id')
            if place_id and place_id not in seen_places:
                seen_places.add(place_id)
                unique_services.append(service)
        
        # Sort by distance from route
        return sorted(unique_services, key=lambda s: s.get('distance_from_route', float('inf')))[:5]
    
    def calculate_service_density(self, emergency_services: Dict) -> Dict:
        """Calculate density of emergency services"""
        total_services = sum(len(services) for services in emergency_services.values())
        
        return {
            'total_emergency_services': total_services,
            'hospitals_count': len(emergency_services.get('hospitals', [])),
            'police_stations_count': len(emergency_services.get('police_stations', [])),
            'service_centers_count': len(emergency_services.get('service_centers', [])),
            'emergency_density': 'HIGH' if total_services > 15 else 'MEDIUM' if total_services > 8 else 'LOW'
        }
    
    def identify_coverage_gaps(self, emergency_services: Dict, route_points: List) -> List[Dict]:
        """Identify areas with poor emergency service coverage"""
        # Simplified gap analysis
        gaps = []
        
        total_services = sum(len(services) for services in emergency_services.values())
        
        if total_services < 5:
            gaps.append({
                'gap_type': 'Overall Low Coverage',
                'description': f'Only {total_services} emergency services found along route',
                'severity': 'HIGH',
                'recommendation': 'Carry comprehensive emergency kit and contact information'
            })
        
        if len(emergency_services.get('hospitals', [])) < 2:
            gaps.append({
                'gap_type': 'Limited Medical Facilities',
                'description': 'Few hospitals available along route',
                'severity': 'MEDIUM',
                'recommendation': 'Identify medical facilities before travel'
            })
        
        return gaps
    
    def calculate_emergency_score(self, emergency_services: Dict) -> int:
        """Calculate overall emergency preparedness score"""
        score = 0
        
        # Points for different services
        score += min(len(emergency_services.get('hospitals', [])) * 20, 60)
        score += min(len(emergency_services.get('police_stations', [])) * 10, 30)
        score += min(len(emergency_services.get('service_centers', [])) * 5, 20)
        
        return min(100, score)
    
    def identify_best_contingency_point(self, rerouting_scenarios: List[Dict]) -> Dict:
        """Identify best point for contingency planning"""
        if not rerouting_scenarios:
            return {'error': 'No contingency points available'}
        
        # Find scenario with shortest emergency reroute
        best_scenario = min(rerouting_scenarios, 
                          key=lambda s: len(s.get('emergency_distance', '999 km')))
        
        return {
            'best_contingency_scenario': best_scenario.get('scenario'),
            'emergency_distance': best_scenario.get('emergency_distance'),
            'coordinates': best_scenario.get('from_coordinates'),
            'recommendation': f"Best contingency point at {best_scenario.get('scenario').lower()}"
        }
    
    def calculate_distance_from_point(self, service_coords: Dict, ref_lat: float, ref_lng: float) -> float:
        """Calculate distance from reference point"""
        try:
            if not service_coords or 'lat' not in service_coords:
                return float('inf')
            
            return geodesic((ref_lat, ref_lng), 
                          (service_coords['lat'], service_coords['lng'])).kilometers
        except:
            return float('inf')