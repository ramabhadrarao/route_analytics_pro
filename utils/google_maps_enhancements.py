# utils/google_maps_enhancements.py - GOOGLE MAPS API INTEGRATION

import requests
import json
import time
from typing import Dict, List, Tuple, Optional
import logging
from geopy.distance import geodesic
import hashlib

logger = logging.getLogger(__name__)

class GoogleMapsEnhancements:
    """Enhanced Google Maps features for comprehensive route analysis"""
    
    def __init__(self, google_api_key: str):
        self.google_api_key = google_api_key
        self.session = requests.Session()
        
        # Terrain classification rules based on Google place types
        self.terrain_classifiers = {
            'urban': [
                'locality', 'sublocality', 'administrative_area_level_2',
                'neighborhood', 'establishment', 'point_of_interest'
            ],
            'semi_urban': [
                'administrative_area_level_3', 'postal_town', 'sublocality_level_1',
                'sublocality_level_2', 'political'
            ],
            'rural': [
                'administrative_area_level_1', 'country', 'natural_feature',
                'route', 'colloquial_area'
            ]
        }
    
    def enhance_route_with_supply_customer_details(self, route_data: Dict, 
                                                 supply_location: str = None, 
                                                 customer_name: str = None) -> Dict:
        """Enhanced supply location & customer details with precise geocoding"""
        
        enhanced_data = {
            'supply_details': {},
            'customer_details': {},
            'geocoded_locations': {},
            'route_optimization': {}
        }
        
        try:
            route_points = route_data.get('route_points', [])
            if not route_points:
                enhanced_data['error'] = 'No route points available'
                return enhanced_data
            
            start_point = route_points[0]
            end_point = route_points[-1]
            
            # Enhanced geocoding for supply location
            supply_details = self._enhanced_reverse_geocode(start_point[0], start_point[1])
            enhanced_data['supply_details'] = {
                'coordinates': {'lat': start_point[0], 'lng': start_point[1]},
                'formatted_address': supply_details.get('formatted_address', 'Unknown'),
                'place_name': supply_location or supply_details.get('name', 'Supply Location'),
                'place_types': supply_details.get('types', []),
                'address_components': supply_details.get('address_components', []),
                'place_id': supply_details.get('place_id', ''),
                'business_status': supply_details.get('business_status', ''),
                'accessibility': self._assess_location_accessibility(supply_details)
            }
            
            # Enhanced geocoding for customer location
            customer_details = self._enhanced_reverse_geocode(end_point[0], end_point[1])
            enhanced_data['customer_details'] = {
                'coordinates': {'lat': end_point[0], 'lng': end_point[1]},
                'formatted_address': customer_details.get('formatted_address', 'Unknown'),
                'customer_name': customer_name or 'Customer Location',
                'place_types': customer_details.get('types', []),
                'address_components': customer_details.get('address_components', []),
                'place_id': customer_details.get('place_id', ''),
                'delivery_accessibility': self._assess_delivery_accessibility(customer_details),
                'nearby_landmarks': self._get_nearby_landmarks(end_point[0], end_point[1])
            }
            
            # Route optimization suggestions
            enhanced_data['route_optimization'] = self._analyze_route_optimization(
                start_point, end_point, route_points
            )
            
            print("✅ Supply & Customer details enhanced with comprehensive geocoding")
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error enhancing supply/customer details: {e}")
            enhanced_data['error'] = str(e)
            return enhanced_data
    
    def classify_route_terrain(self, route_points: List) -> Dict:
        """Advanced terrain classification using Google Places and Roads APIs"""
        
        terrain_analysis = {
            'terrain_segments': [],
            'overall_classification': 'mixed',
            'terrain_distribution': {'urban': 0, 'semi_urban': 0, 'rural': 0},
            'detailed_analysis': {},
            'road_quality_assessment': {}
        }
        
        try:
            # Sample points strategically for terrain analysis
            sample_size = min(25, len(route_points))
            sampled_points = self._strategic_sample_points(route_points, sample_size)
            
            for i, point in enumerate(sampled_points):
                lat, lng = point[0], point[1]
                
                # Get comprehensive location information
                location_info = self._enhanced_reverse_geocode(lat, lng)
                terrain_type = self._determine_advanced_terrain_type(location_info)
                road_quality = self._assess_road_quality(location_info)
                
                segment = {
                    'segment_id': i + 1,
                    'coordinates': {'lat': lat, 'lng': lng},
                    'terrain_type': terrain_type,
                    'location_types': location_info.get('types', []),
                    'formatted_address': location_info.get('formatted_address', 'Unknown'),
                    'road_quality': road_quality,
                    'population_density': self._estimate_population_density(location_info),
                    'infrastructure_level': self._assess_infrastructure_level(location_info),
                    'distance_from_start': self._calculate_distance_from_start(point, route_points[0])
                }
                
                terrain_analysis['terrain_segments'].append(segment)
                terrain_analysis['terrain_distribution'][terrain_type] += 1
                
                time.sleep(0.1)  # Rate limiting
            
            # Advanced classification
            terrain_analysis['overall_classification'] = self._classify_overall_terrain(
                terrain_analysis['terrain_distribution'], len(sampled_points)
            )
            
            terrain_analysis['detailed_analysis'] = self._generate_detailed_terrain_analysis(
                terrain_analysis['terrain_segments']
            )
            
            print(f"✅ Advanced terrain classification: {terrain_analysis['overall_classification']}")
            return terrain_analysis
            
        except Exception as e:
            logger.error(f"Error in terrain classification: {e}")
            terrain_analysis['error'] = str(e)
            return terrain_analysis
    
    def identify_major_highways(self, route_data: Dict) -> Dict:
        """Comprehensive highway identification using Google Roads and Directions APIs"""
        
        highway_analysis = {
            'major_highways': [],
            'highway_segments': [],
            'total_highway_distance': 0,
            'highway_percentage': 0,
            'highway_quality_assessment': {},
            'toll_information': {}
        }
        
        try:
            route_points = route_data.get('route_points', [])
            if not route_points:
                highway_analysis['error'] = 'No route points available'
                return highway_analysis
            
            # Use Google Directions API with detailed route information
            start_point = route_points[0]
            end_point = route_points[-1]
            
            directions = self._get_enhanced_directions(start_point, end_point)
            
            if directions and 'routes' in directions:
                route = directions['routes'][0]
                
                # Analyze each leg and step for highway information
                for leg_idx, leg in enumerate(route.get('legs', [])):
                    for step_idx, step in enumerate(leg.get('steps', [])):
                        highway_info = self._analyze_step_for_highways(step, leg_idx, step_idx)
                        
                        if highway_info:
                            highway_analysis['highway_segments'].append(highway_info)
                            
                            # Add to major highways list
                            highway_name = highway_info.get('highway_name')
                            if highway_name and not any(h['name'] == highway_name 
                                                      for h in highway_analysis['major_highways']):
                                highway_analysis['major_highways'].append({
                                    'name': highway_name,
                                    'type': highway_info.get('highway_type'),
                                    'classification': highway_info.get('classification'),
                                    'first_encounter_distance': highway_info.get('distance_from_start'),
                                    'total_distance_on_highway': highway_info.get('distance_km'),
                                    'speed_limit': highway_info.get('speed_limit'),
                                    'toll_status': highway_info.get('toll_status')
                                })
            
            # Calculate comprehensive highway statistics
            highway_analysis = self._calculate_highway_statistics(highway_analysis, route_data)
            
            print(f"✅ Major highways identified: {len(highway_analysis['major_highways'])} highways")
            return highway_analysis
            
        except Exception as e:
            logger.error(f"Error identifying major highways: {e}")
            highway_analysis['error'] = str(e)
            return highway_analysis
    
    def analyze_time_specific_congestion(self, route_points: List) -> Dict:
        """Advanced time-specific congestion analysis using Google Traffic APIs"""
        
        congestion_analysis = {
            'peak_hours': {
                'morning': {'start': '07:00', 'end': '10:00', 'segments': []},
                'afternoon': {'start': '12:00', 'end': '14:00', 'segments': []},
                'evening': {'start': '17:00', 'end': '20:00', 'segments': []},
                'night': {'start': '22:00', 'end': '06:00', 'segments': []}
            },
            'congestion_hotspots': [],
            'time_recommendations': [],
            'optimal_departure_times': {},
            'traffic_flow_analysis': {}
        }
        
        try:
            # Strategic sampling for traffic analysis
            sample_points = self._strategic_sample_points(route_points, max_points=15)
            
            # Analyze traffic for different time periods
            for period_name, period_data in congestion_analysis['peak_hours'].items():
                for i, point in enumerate(sample_points):
                    lat, lng = point[0], point[1]
                    
                    traffic_info = self._get_advanced_traffic_info(lat, lng, period_name)
                    
                    if traffic_info:
                        segment = {
                            'segment_id': i + 1,
                            'location': f"Segment {i+1}",
                            'coordinates': {'lat': lat, 'lng': lng},
                            'traffic_level': traffic_info.get('traffic_level', 'unknown'),
                            'speed_reduction': traffic_info.get('speed_reduction_percent', 0),
                            'delay_minutes': traffic_info.get('delay_minutes', 0),
                            'congestion_score': traffic_info.get('congestion_score', 0),
                            'recommended_speed': traffic_info.get('recommended_speed', 'normal'),
                            'alternative_available': traffic_info.get('alternative_routes', False)
                        }
                        period_data['segments'].append(segment)
                
                time.sleep(0.1)  # Rate limiting between periods
            
            # Generate comprehensive analysis
            congestion_analysis['optimal_departure_times'] = self._calculate_optimal_departure_times(
                congestion_analysis['peak_hours']
            )
            
            congestion_analysis['time_recommendations'] = self._generate_advanced_time_recommendations(
                congestion_analysis
            )
            
            print("✅ Advanced time-specific congestion analysis complete")
            return congestion_analysis
            
        except Exception as e:
            logger.error(f"Error in congestion analysis: {e}")
            congestion_analysis['error'] = str(e)
            return congestion_analysis
    
    def generate_enhanced_elevation_analysis(self, route_points: List) -> Dict:
        """Enhanced elevation analysis with gradient calculations and risk assessment"""
        
        elevation_analysis = {
            'elevation_profile': [],
            'gradient_analysis': [],
            'elevation_risks': [],
            'ascent_descent_summary': {},
            'fuel_efficiency_impact': {},
            'vehicle_stress_points': []
        }
        
        try:
            # Get high-resolution elevation data
            elevation_data = self._get_enhanced_elevation_data(route_points)
            
            if not elevation_data:
                elevation_analysis['error'] = 'Unable to retrieve elevation data'
                return elevation_analysis
            
            # Calculate gradients and analyze risks
            for i in range(1, len(elevation_data)):
                current = elevation_data[i]
                previous = elevation_data[i-1]
                
                gradient_info = self._calculate_gradient_info(previous, current)
                elevation_analysis['gradient_analysis'].append(gradient_info)
                
                # Identify elevation risks
                if abs(gradient_info['gradient_percent']) > 6:
                    risk_info = self._assess_elevation_risk(gradient_info, current)
                    elevation_analysis['elevation_risks'].append(risk_info)
                
                # Vehicle stress assessment
                if abs(gradient_info['gradient_percent']) > 8:
                    stress_point = self._assess_vehicle_stress(gradient_info, current)
                    elevation_analysis['vehicle_stress_points'].append(stress_point)
            
            # Generate summary analyses
            elevation_analysis['ascent_descent_summary'] = self._generate_elevation_summary(
                elevation_analysis['gradient_analysis']
            )
            
            elevation_analysis['fuel_efficiency_impact'] = self._calculate_fuel_impact(
                elevation_analysis['gradient_analysis']
            )
            
            print(f"✅ Enhanced elevation analysis: {len(elevation_analysis['elevation_risks'])} risk points identified")
            return elevation_analysis
            
        except Exception as e:
            logger.error(f"Error in enhanced elevation analysis: {e}")
            elevation_analysis['error'] = str(e)
            return elevation_analysis
    
    # Helper Methods
    
    def _enhanced_reverse_geocode(self, lat: float, lng: float) -> Dict:
        """Enhanced reverse geocoding with comprehensive place information"""
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'latlng': f"{lat},{lng}",
                'result_type': 'street_address|route|intersection|political',
                'key': self.google_api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK' and data.get('results'):
                    return data['results'][0]
            
            return {}
            
        except Exception as e:
            logger.error(f"Enhanced reverse geocoding error: {e}")
            return {}
    
    def _determine_advanced_terrain_type(self, location_info: Dict) -> str:
        """Advanced terrain classification with multiple factors"""
        types = location_info.get('types', [])
        address_components = location_info.get('address_components', [])
        
        # Score-based classification
        urban_score = 0
        semi_urban_score = 0
        rural_score = 0
        
        for place_type in types:
            if place_type in self.terrain_classifiers['urban']:
                urban_score += 2
            elif place_type in self.terrain_classifiers['semi_urban']:
                semi_urban_score += 1
            elif place_type in self.terrain_classifiers['rural']:
                rural_score += 1
        
        # Additional scoring from address components
        for component in address_components:
            component_types = component.get('types', [])
            if 'locality' in component_types or 'sublocality' in component_types:
                urban_score += 1
            elif 'administrative_area_level_3' in component_types:
                semi_urban_score += 1
        
        # Determine terrain based on highest score
        if urban_score >= semi_urban_score and urban_score >= rural_score:
            return 'urban'
        elif semi_urban_score >= rural_score:
            return 'semi_urban'
        else:
            return 'rural'
    
    def _assess_location_accessibility(self, location_info: Dict) -> Dict:
        """Assess accessibility of supply location"""
        types = location_info.get('types', [])
        
        accessibility = {
            'vehicle_access': 'good',
            'loading_facilities': 'unknown',
            'parking_availability': 'limited',
            'business_hours': 'check_required'
        }
        
        if 'establishment' in types:
            accessibility['vehicle_access'] = 'excellent'
            accessibility['loading_facilities'] = 'likely_available'
        
        if 'parking' in types:
            accessibility['parking_availability'] = 'available'
        
        return accessibility
    
    def _assess_delivery_accessibility(self, location_info: Dict) -> Dict:
        """Assess delivery accessibility for customer location"""
        types = location_info.get('types', [])
        
        accessibility = {
            'delivery_access': 'good',
            'unloading_space': 'limited',
            'location_type': 'standard',
            'special_instructions': []
        }
        
        if 'establishment' in types or 'point_of_interest' in types:
            accessibility['delivery_access'] = 'excellent'
            accessibility['unloading_space'] = 'likely_available'
            accessibility['location_type'] = 'commercial'
        
        if 'sublocality' in types:
            accessibility['special_instructions'].append('Residential area - follow local traffic rules')
        
        return accessibility
    
    def _get_nearby_landmarks(self, lat: float, lng: float) -> List[Dict]:
        """Get nearby landmarks for navigation assistance"""
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': 1000,
                'type': 'establishment|point_of_interest',
                'key': self.google_api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                landmarks = []
                
                for place in data.get('results', [])[:5]:  # Top 5 landmarks
                    landmarks.append({
                        'name': place.get('name', 'Unknown'),
                        'type': place.get('types', []),
                        'rating': place.get('rating', 0),
                        'distance': place.get('geometry', {}).get('location', {})
                    })
                
                return landmarks
            
            return []
            
        except Exception as e:
            logger.error(f"Nearby landmarks error: {e}")
            return []
    
    def _strategic_sample_points(self, route_points: List, max_points: int) -> List:
        """Strategic sampling of route points for optimal API usage"""
        if len(route_points) <= max_points:
            return route_points
        
        # Include start, end, and evenly distributed middle points
        sampled = [route_points[0]]  # Start point
        
        if max_points > 2:
            # Middle points
            step = len(route_points) // (max_points - 2)
            for i in range(step, len(route_points) - step, step):
                sampled.append(route_points[i])
        
        sampled.append(route_points[-1])  # End point
        
        return sampled[:max_points]
    
    def _get_enhanced_directions(self, start_point: List, end_point: List) -> Dict:
        """Get enhanced directions with detailed route information"""
        try:
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': f"{start_point[0]},{start_point[1]}",
                'destination': f"{end_point[0]},{end_point[1]}",
                'alternatives': 'true',
                'units': 'metric',
                'region': 'in',
                'key': self.google_api_key
            }
            
            response = self.session.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                return response.json()
            
            return {}
            
        except Exception as e:
            logger.error(f"Enhanced directions error: {e}")
            return {}
    
    def _analyze_step_for_highways(self, step: Dict, leg_idx: int, step_idx: int) -> Optional[Dict]:
        """Analyze direction step for highway information"""
        try:
            instruction = step.get('html_instructions', '').lower()
            maneuver = step.get('maneuver', '')
            distance = step.get('distance', {}).get('value', 0) / 1000  # Convert to km
            duration = step.get('duration', {}).get('value', 0) / 60    # Convert to minutes
            
            # Enhanced highway detection patterns
            highway_patterns = {
                'national_highway': ['nh-', 'national highway', 'nh ', 'highway nh'],
                'state_highway': ['sh-', 'state highway', 'sh ', 'highway sh'],
                'expressway': ['expressway', 'express highway', 'freeway'],
                'arterial': ['arterial', 'main road', 'trunk road']
            }
            
            highway_type = None
            highway_name = None
            
            for category, patterns in highway_patterns.items():
                for pattern in patterns:
                    if pattern in instruction:
                        highway_type = category
                        highway_name = self._extract_highway_name(instruction, pattern)
                        break
                if highway_type:
                    break
            
            if highway_type and highway_name:
                return {
                    'highway_name': highway_name,
                    'highway_type': highway_type,
                    'classification': self._classify_highway_importance(highway_type, highway_name),
                    'distance_km': distance,
                    'duration_minutes': duration,
                    'speed_limit': self._estimate_highway_speed_limit(highway_type),
                    'toll_status': self._assess_toll_status(highway_name, highway_type),
                    'leg_index': leg_idx,
                    'step_index': step_idx,
                    'maneuver_type': maneuver
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Highway analysis error: {e}")
            return None
    
    def _extract_highway_name(self, instruction: str, pattern: str) -> str:
        """Extract highway name from instruction text"""
        try:
            # Find the pattern and extract the highway number/name
            pattern_index = instruction.find(pattern)
            if pattern_index == -1:
                return "Unknown Highway"
            
            # Extract text after the pattern
            after_pattern = instruction[pattern_index + len(pattern):].strip()
            
            # Extract highway number (first word/number after pattern)
            words = after_pattern.split()
            if words:
                highway_number = words[0].rstrip('.,;:')
                if pattern.startswith('nh'):
                    return f"NH-{highway_number}"
                elif pattern.startswith('sh'):
                    return f"SH-{highway_number}"
                else:
                    return highway_number
            
            return "Unknown Highway"
            
        except Exception:
            return "Unknown Highway"
    
    def _classify_highway_importance(self, highway_type: str, highway_name: str) -> str:
        """Classify highway importance based on type and name"""
        if highway_type == 'national_highway':
            # Major national highways
            major_nhs = ['NH-1', 'NH-2', 'NH-3', 'NH-4', 'NH-7', 'NH-8']
            if any(nh in highway_name for nh in major_nhs):
                return 'major_national'
            return 'national'
        elif highway_type == 'expressway':
            return 'expressway'
        elif highway_type == 'state_highway':
            return 'state'
        else:
            return 'arterial'
    
    def _estimate_highway_speed_limit(self, highway_type: str) -> str:
        """Estimate speed limit based on highway type"""
        speed_limits = {
            'national_highway': '80-100 km/h',
            'expressway': '100-120 km/h',
            'state_highway': '60-80 km/h',
            'arterial': '40-60 km/h'
        }
        return speed_limits.get(highway_type, '60 km/h')
    
    def _assess_toll_status(self, highway_name: str, highway_type: str) -> str:
        """Assess toll status of highway"""
        if highway_type in ['national_highway', 'expressway']:
            return 'toll_likely'
        elif highway_type == 'state_highway':
            return 'toll_possible'
        else:
            return 'toll_unlikely'
    
    def _calculate_highway_statistics(self, highway_analysis: Dict, route_data: Dict) -> Dict:
        """Calculate comprehensive highway statistics"""
        try:
            segments = highway_analysis.get('highway_segments', [])
            
            # Calculate total highway distance
            total_highway_distance = sum(segment.get('distance_km', 0) for segment in segments)
            highway_analysis['total_highway_distance'] = total_highway_distance
            
            # Calculate highway percentage
            total_route_distance = self._parse_distance_to_km(route_data.get('distance', '0 km'))
            if total_route_distance > 0:
                highway_analysis['highway_percentage'] = (total_highway_distance / total_route_distance) * 100
            
            # Highway quality assessment
            highway_analysis['highway_quality_assessment'] = {
                'expressway_km': sum(s.get('distance_km', 0) for s in segments 
                                   if s.get('highway_type') == 'expressway'),
                'national_highway_km': sum(s.get('distance_km', 0) for s in segments 
                                         if s.get('highway_type') == 'national_highway'),
                'state_highway_km': sum(s.get('distance_km', 0) for s in segments 
                                      if s.get('highway_type') == 'state_highway'),
                'overall_quality': self._assess_overall_highway_quality(segments)
            }
            
            # Toll information summary
            toll_segments = [s for s in segments if s.get('toll_status') == 'toll_likely']
            highway_analysis['toll_information'] = {
                'toll_segments': len(toll_segments),
                'estimated_toll_distance': sum(s.get('distance_km', 0) for s in toll_segments),
                'fastag_recommended': len(toll_segments) > 2
            }
            
            return highway_analysis
            
        except Exception as e:
            logger.error(f"Highway statistics calculation error: {e}")
            return highway_analysis
    
    def _assess_overall_highway_quality(self, segments: List[Dict]) -> str:
        """Assess overall highway quality"""
        if not segments:
            return 'unknown'
        
        expressway_count = len([s for s in segments if s.get('highway_type') == 'expressway'])
        national_count = len([s for s in segments if s.get('highway_type') == 'national_highway'])
        
        total_segments = len(segments)
        
        if expressway_count / total_segments > 0.5:
            return 'excellent'
        elif national_count / total_segments > 0.4:
            return 'good'
        else:
            return 'moderate'
    
    def _get_advanced_traffic_info(self, lat: float, lng: float, time_period: str) -> Dict:
        """Get advanced traffic information for specific time period"""
        try:
            # Simulate advanced traffic analysis
            # In production, use Google Traffic API or Roads API
            
            base_congestion = {
                'morning': 0.7,    # 70% congestion in morning
                'afternoon': 0.4,  # 40% congestion in afternoon  
                'evening': 0.8,    # 80% congestion in evening
                'night': 0.2       # 20% congestion at night
            }
            
            congestion_level = base_congestion.get(time_period, 0.5)
            
            # Adjust based on location characteristics
            location_info = self._enhanced_reverse_geocode(lat, lng)
            types = location_info.get('types', [])
            
            if any(t in types for t in ['locality', 'sublocality', 'establishment']):
                congestion_level += 0.2  # Higher congestion in urban areas
            
            congestion_level = min(1.0, congestion_level)  # Cap at 100%
            
            return {
                'traffic_level': self._classify_traffic_level(congestion_level),
                'congestion_score': int(congestion_level * 100),
                'speed_reduction_percent': int(congestion_level * 50),  # Up to 50% speed reduction
                'delay_minutes': int(congestion_level * 20),  # Up to 20 minutes delay
                'recommended_speed': self._get_recommended_speed(congestion_level),
                'alternative_routes': congestion_level > 0.6
            }
            
        except Exception as e:
            logger.error(f"Advanced traffic info error: {e}")
            return {}
    
    def _classify_traffic_level(self, congestion_score: float) -> str:
        """Classify traffic level based on congestion score"""
        if congestion_score > 0.8:
            return 'severe'
        elif congestion_score > 0.6:
            return 'heavy'
        elif congestion_score > 0.4:
            return 'moderate'
        elif congestion_score > 0.2:
            return 'light'
        else:
            return 'free_flow'
    
    def _get_recommended_speed(self, congestion_level: float) -> str:
        """Get recommended speed based on congestion"""
        if congestion_level > 0.8:
            return '20-30 km/h'
        elif congestion_level > 0.6:
            return '30-40 km/h'
        elif congestion_level > 0.4:
            return '40-60 km/h'
        else:
            return 'normal_speed'
    
    def _calculate_optimal_departure_times(self, peak_hours: Dict) -> Dict:
        """Calculate optimal departure times based on traffic analysis"""
        optimal_times = {}
        
        try:
            # Analyze each period's congestion
            period_scores = {}
            for period, data in peak_hours.items():
                segments = data.get('segments', [])
                if segments:
                    avg_congestion = sum(s.get('congestion_score', 0) for s in segments) / len(segments)
                    period_scores[period] = avg_congestion
            
            # Find best and worst periods
            if period_scores:
                best_period = min(period_scores.items(), key=lambda x: x[1])
                worst_period = max(period_scores.items(), key=lambda x: x[1])
                
                optimal_times['best_departure_period'] = {
                    'period': best_period[0],
                    'congestion_score': best_period[1],
                    'time_window': peak_hours[best_period[0]],
                    'advantages': self._get_period_advantages(best_period[0])
                }
                
                optimal_times['avoid_departure_period'] = {
                    'period': worst_period[0],
                    'congestion_score': worst_period[1],
                    'time_window': peak_hours[worst_period[0]],
                    'disadvantages': self._get_period_disadvantages(worst_period[0])
                }
            
            return optimal_times
            
        except Exception as e:
            logger.error(f"Optimal departure times calculation error: {e}")
            return {}
    
    def _get_period_advantages(self, period: str) -> List[str]:
        """Get advantages of traveling during specific period"""
        advantages = {
            'morning': ['Less traffic than evening', 'Good visibility', 'Fresh driving conditions'],
            'afternoon': ['Moderate traffic', 'Good weather', 'Services open'],
            'evening': ['All services available', 'Cooler temperatures'],
            'night': ['Minimal traffic', 'Faster travel', 'Cooler weather', 'Less pollution']
        }
        return advantages.get(period, [])
    
    def _get_period_disadvantages(self, period: str) -> List[str]:
        """Get disadvantages of traveling during specific period"""
        disadvantages = {
            'morning': ['Morning rush hour', 'School traffic', 'Fog possibility'],
            'afternoon': ['Peak heat in summer', 'Moderate congestion'],
            'evening': ['Heavy rush hour traffic', 'Longest delays', 'Stress conditions'],
            'night': ['Reduced visibility', 'Limited services', 'Safety concerns', 'Driver fatigue']
        }
        return disadvantages.get(period, [])
    
    def _generate_advanced_time_recommendations(self, congestion_analysis: Dict) -> List[str]:
        """Generate advanced time-based recommendations"""
        recommendations = []
        
        optimal_times = congestion_analysis.get('optimal_departure_times', {})
        
        if optimal_times.get('best_departure_period'):
            best = optimal_times['best_departure_period']
            recommendations.append(
                f"OPTIMAL DEPARTURE: {best['period'].title()} period "
                f"({best['time_window']['start']}-{best['time_window']['end']}) "
                f"- {best['congestion_score']:.0f}% congestion"
            )
        
        if optimal_times.get('avoid_departure_period'):
            worst = optimal_times['avoid_departure_period']
            recommendations.append(
                f"AVOID DEPARTURE: {worst['period'].title()} period "
                f"({worst['time_window']['start']}-{worst['time_window']['end']}) "
                f"- {worst['congestion_score']:.0f}% congestion"
            )
        
        # General recommendations
        recommendations.extend([
            "Monitor real-time traffic before departure",
            "Consider flexible departure times to avoid peak congestion",
            "Use traffic apps for live updates during travel",
            "Plan buffer time for unexpected delays",
            "Check for special events that might affect traffic"
        ])
        
        return recommendations
    
    def _get_enhanced_elevation_data(self, route_points: List) -> List[Dict]:
        """Get enhanced elevation data with Google Elevation API"""
        try:
            # Sample points for elevation API (limit for cost efficiency)
            sample_points = self._strategic_sample_points(route_points, max_points=50)
            
            locations = '|'.join([f"{point[0]},{point[1]}" for point in sample_points])
            
            url = "https://maps.googleapis.com/maps/api/elevation/json"
            params = {
                'locations': locations,
                'key': self.google_api_key
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for i, result in enumerate(data.get('results', [])):
                    enhanced_result = {
                        'location': result.get('location', {}),
                        'elevation': result.get('elevation', 0),
                        'resolution': result.get('resolution', 0),
                        'distance_from_start': self._calculate_distance_from_start(
                            [result.get('location', {}).get('lat', 0), 
                             result.get('location', {}).get('lng', 0)], 
                            route_points[0]
                        ),
                        'point_index': i
                    }
                    results.append(enhanced_result)
                
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Enhanced elevation data error: {e}")
            return []
    
    def _calculate_gradient_info(self, previous: Dict, current: Dict) -> Dict:
        """Calculate detailed gradient information between two elevation points"""
        try:
            prev_elevation = previous.get('elevation', 0)
            curr_elevation = current.get('elevation', 0)
            prev_distance = previous.get('distance_from_start', 0)
            curr_distance = current.get('distance_from_start', 0)
            
            elevation_change = curr_elevation - prev_elevation
            distance_change = curr_distance - prev_distance
            
            gradient_percent = 0
            if distance_change > 0:
                gradient_percent = (elevation_change / (distance_change * 1000)) * 100
            
            return {
                'start_point': previous.get('location', {}),
                'end_point': current.get('location', {}),
                'elevation_change': elevation_change,
                'distance_km': distance_change,
                'gradient_percent': gradient_percent,
                'gradient_category': self._classify_gradient(gradient_percent),
                'start_elevation': prev_elevation,
                'end_elevation': curr_elevation
            }
            
        except Exception as e:
            logger.error(f"Gradient calculation error: {e}")
            return {}
    
    def _classify_gradient(self, gradient_percent: float) -> str:
        """Classify gradient steepness"""
        abs_gradient = abs(gradient_percent)
        
        if abs_gradient > 12:
            return 'extreme'
        elif abs_gradient > 8:
            return 'steep'
        elif abs_gradient > 5:
            return 'moderate'
        elif abs_gradient > 2:
            return 'gentle'
        else:
            return 'flat'
    
    def _assess_elevation_risk(self, gradient_info: Dict, elevation_point: Dict) -> Dict:
        """Assess risks associated with elevation changes"""
        gradient = gradient_info.get('gradient_percent', 0)
        elevation = elevation_point.get('elevation', 0)
        
        risk_factors = []
        risk_level = 'low'
        
        if abs(gradient) > 8:
            risk_level = 'high'
            if gradient > 0:
                risk_factors.extend(['Engine strain', 'Overheating risk', 'Fuel consumption increase'])
            else:
                risk_factors.extend(['Brake strain', 'Speed control required', 'Brake fade risk'])
        elif abs(gradient) > 5:
            risk_level = 'moderate'
            risk_factors.append('Moderate vehicle stress')
        
        if elevation > 1500:
            risk_factors.append('High altitude effects')
        
        return {
            'location': elevation_point.get('location', {}),
            'gradient_percent': gradient,
            'elevation_meters': elevation,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendations': self._get_elevation_recommendations(gradient, elevation)
        }
    
    def _assess_vehicle_stress(self, gradient_info: Dict, elevation_point: Dict) -> Dict:
        """Assess vehicle stress points on steep gradients"""
        gradient = gradient_info.get('gradient_percent', 0)
        
        stress_factors = {
            'engine_stress': abs(gradient) > 6,
            'brake_stress': gradient < -6,
            'transmission_stress': abs(gradient) > 8,
            'cooling_stress': gradient > 8
        }
        
        return {
            'location': elevation_point.get('location', {}),
            'gradient_percent': gradient,
            'stress_factors': stress_factors,
            'maintenance_recommendations': self._get_maintenance_recommendations(stress_factors)
        }
    
    def _get_elevation_recommendations(self, gradient: float, elevation: float) -> List[str]:
        """Get recommendations for elevation challenges"""
        recommendations = []
        
        if gradient > 8:
            recommendations.extend([
                'Use lower gear for steep ascents',
                'Monitor engine temperature closely',
                'Maintain steady speed, avoid sudden acceleration'
            ])
        elif gradient < -8:
            recommendations.extend([
                'Use engine braking on steep descents',
                'Avoid continuous brake application',
                'Check brake condition before travel'
            ])
        
        if elevation > 1500:
            recommendations.append('Monitor vehicle performance at high altitude')
        
        return recommendations
    
    def _get_maintenance_recommendations(self, stress_factors: Dict) -> List[str]:
        """Get maintenance recommendations based on stress factors"""
        recommendations = []
        
        if stress_factors.get('engine_stress'):
            recommendations.append('Check engine oil and coolant levels')
        
        if stress_factors.get('brake_stress'):
            recommendations.append('Inspect brake pads and fluid')
        
        if stress_factors.get('transmission_stress'):
            recommendations.append('Check transmission fluid')
        
        if stress_factors.get('cooling_stress'):
            recommendations.append('Ensure cooling system is functioning properly')
        
        return recommendations
    
    # Utility Methods
    
    def _calculate_distance_from_start(self, point: List, start_point: List) -> float:
        """Calculate distance from start point using geodesic calculation"""
        try:
            from geopy.distance import geodesic
            return geodesic(start_point, point).kilometers
        except Exception:
            # Fallback to simple calculation if geopy not available
            import math
            
            lat1, lon1 = start_point[0], start_point[1]
            lat2, lon2 = point[0], point[1]
            
            # Haversine formula
            R = 6371  # Earth's radius in kilometers
            
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            
            a = (math.sin(dlat/2) * math.sin(dlat/2) + 
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
                 math.sin(dlon/2) * math.sin(dlon/2))
            
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            return distance
    
    def _parse_distance_to_km(self, distance_str: str) -> float:
        """Parse distance string to kilometers"""
        try:
            if not distance_str:
                return 0.0
            
            # Remove common suffixes and clean
            distance_str = distance_str.lower().replace('km', '').replace('kilometers', '')
            distance_str = distance_str.replace(',', '').strip()
            
            return float(distance_str)
        except:
            return 0.0
    
    def _assess_road_quality(self, location_info: Dict) -> str:
        """Assess road quality based on location information"""
        types = location_info.get('types', [])
        
        if 'route' in types:
            return 'highway_standard'
        elif any(t in types for t in ['locality', 'sublocality']):
            return 'urban_standard'
        else:
            return 'rural_standard'
    
    def _estimate_population_density(self, location_info: Dict) -> str:
        """Estimate population density from location data"""
        types = location_info.get('types', [])
        
        urban_indicators = ['locality', 'sublocality', 'neighborhood', 'establishment']
        if any(indicator in types for indicator in urban_indicators):
            return 'high'
        
        semi_urban_indicators = ['administrative_area_level_3', 'postal_town']
        if any(indicator in types for indicator in semi_urban_indicators):
            return 'medium'
        
        return 'low'
    
    def _assess_infrastructure_level(self, location_info: Dict) -> str:
        """Assess infrastructure development level"""
        types = location_info.get('types', [])
        
        if 'establishment' in types or 'point_of_interest' in types:
            return 'developed'
        elif 'locality' in types or 'sublocality' in types:
            return 'developing'
        else:
            return 'basic'
    
    def _classify_overall_terrain(self, distribution: Dict, total_points: int) -> str:
        """Classify overall terrain based on distribution"""
        if total_points == 0:
            return 'unknown'
        
        urban_pct = (distribution.get('urban', 0) / total_points) * 100
        rural_pct = (distribution.get('rural', 0) / total_points) * 100
        semi_urban_pct = (distribution.get('semi_urban', 0) / total_points) * 100
        
        if urban_pct > 60:
            return 'predominantly_urban'
        elif rural_pct > 60:
            return 'predominantly_rural'
        elif urban_pct > 40:
            return 'mixed_urban_dominant'
        elif rural_pct > 40:
            return 'mixed_rural_dominant'
        else:
            return 'balanced_mixed'
    
    def _generate_detailed_terrain_analysis(self, segments: List[Dict]) -> Dict:
        """Generate detailed terrain analysis from segments"""
        analysis = {
            'terrain_transitions': [],
            'infrastructure_quality': {},
            'population_centers': [],
            'road_quality_distribution': {}
        }
        
        try:
            # Analyze terrain transitions
            for i in range(1, len(segments)):
                prev_terrain = segments[i-1].get('terrain_type')
                curr_terrain = segments[i].get('terrain_type')
                
                if prev_terrain != curr_terrain:
                    analysis['terrain_transitions'].append({
                        'from': prev_terrain,
                        'to': curr_terrain,
                        'location': segments[i].get('coordinates'),
                        'transition_point': i
                    })
            
            # Infrastructure quality summary
            infrastructure_levels = [s.get('infrastructure_level') for s in segments]
            analysis['infrastructure_quality'] = {
                'developed_areas': infrastructure_levels.count('developed'),
                'developing_areas': infrastructure_levels.count('developing'),
                'basic_areas': infrastructure_levels.count('basic'),
                'overall_assessment': self._assess_overall_infrastructure(infrastructure_levels)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Detailed terrain analysis error: {e}")
            return analysis
    
    def _assess_overall_infrastructure(self, levels: List[str]) -> str:
        """Assess overall infrastructure quality"""
        if not levels:
            return 'unknown'
        
        developed_pct = levels.count('developed') / len(levels) * 100
        
        if developed_pct > 60:
            return 'good'
        elif developed_pct > 30:
            return 'moderate'
        else:
            return 'basic'
    
    def _generate_elevation_summary(self, gradient_analysis: List[Dict]) -> Dict:
        """Generate elevation change summary"""
        if not gradient_analysis:
            return {}
        
        total_ascent = sum(g.get('elevation_change', 0) for g in gradient_analysis 
                          if g.get('elevation_change', 0) > 0)
        total_descent = abs(sum(g.get('elevation_change', 0) for g in gradient_analysis 
                              if g.get('elevation_change', 0) < 0))
        
        steep_ascents = len([g for g in gradient_analysis 
                           if g.get('gradient_percent', 0) > 6])
        steep_descents = len([g for g in gradient_analysis 
                            if g.get('gradient_percent', 0) < -6])
        
        return {
            'total_ascent_meters': total_ascent,
            'total_descent_meters': total_descent,
            'net_elevation_change': total_ascent - total_descent,
            'steep_ascent_sections': steep_ascents,
            'steep_descent_sections': steep_descents,
            'overall_difficulty': self._assess_route_difficulty(steep_ascents, steep_descents)
        }
    
    def _assess_route_difficulty(self, steep_ascents: int, steep_descents: int) -> str:
        """Assess overall route difficulty based on elevation changes"""
        total_steep = steep_ascents + steep_descents
        
        if total_steep > 8:
            return 'very_challenging'
        elif total_steep > 4:
            return 'challenging'
        elif total_steep > 2:
            return 'moderate'
        else:
            return 'easy'
    
    def _calculate_fuel_impact(self, gradient_analysis: List[Dict]) -> Dict:
        """Calculate fuel efficiency impact of elevation changes"""
        if not gradient_analysis:
            return {}
        
        # Simplified fuel impact calculation
        ascent_impact = sum(max(0, g.get('gradient_percent', 0)) * g.get('distance_km', 0) 
                          for g in gradient_analysis)
        descent_benefit = sum(abs(min(0, g.get('gradient_percent', 0))) * g.get('distance_km', 0) 
                            for g in gradient_analysis)
        
        net_impact = ascent_impact - (descent_benefit * 0.3)  # Descent provides some benefit
        
        return {
            'ascent_fuel_penalty_percent': min(30, ascent_impact * 2),  # Cap at 30%
            'descent_fuel_benefit_percent': min(10, descent_benefit * 0.5),  # Cap at 10%
            'net_fuel_impact_percent': max(0, net_impact * 1.5),
            'fuel_efficiency_advice': self._get_fuel_efficiency_advice(net_impact)
        }
    
    def _get_fuel_efficiency_advice(self, net_impact: float) -> List[str]:
        """Get fuel efficiency advice based on elevation impact"""
        advice = []
        
        if net_impact > 10:
            advice.extend([
                'Expect 15-25% higher fuel consumption due to elevation changes',
                'Plan additional fuel stops for long ascents',
                'Use cruise control on flat sections to optimize efficiency'
            ])
        elif net_impact > 5:
            advice.extend([
                'Moderate elevation impact on fuel consumption',
                'Maintain steady speeds on inclines'
            ])
        else:
            advice.append('Minimal elevation impact on fuel efficiency')
        
        return advice
    
    def _analyze_route_optimization(self, start_point: List, end_point: List, route_points: List) -> Dict:
        """Analyze potential route optimizations"""
        optimization = {
            'current_route_efficiency': 0,
            'potential_improvements': [],
            'alternative_suggestions': [],
            'optimization_score': 0
        }
        
        try:
            # Calculate route efficiency
            direct_distance = self._calculate_distance_from_start(end_point, start_point)
            actual_distance = sum(self._calculate_distance_from_start(route_points[i], route_points[i-1])
                                for i in range(1, len(route_points)))
            
            if direct_distance > 0:
                efficiency = (direct_distance / actual_distance) * 100
                optimization['current_route_efficiency'] = efficiency
                
                if efficiency < 80:
                    optimization['potential_improvements'].append('Route appears indirect - check for shortcuts')
                elif efficiency > 90:
                    optimization['potential_improvements'].append('Route is well-optimized')
            
            optimization['optimization_score'] = min(100, efficiency + 10)  # Bonus for completion
            
            return optimization
            
        except Exception as e:
            logger.error(f"Route optimization analysis error: {e}")
            optimization['error'] = str(e)
            return optimization