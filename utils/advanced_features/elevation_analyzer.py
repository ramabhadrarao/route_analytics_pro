# utils/advanced_features/elevation_analyzer.py - FULLY IMPLEMENTABLE

import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple
import tempfile
import os

class ElevationAnalyzer:
    """Advanced elevation analysis using Google Elevation API and Open Elevation API"""
    
    def __init__(self, google_api_key=None):
        self.google_api_key = google_api_key
        self.open_elevation_url = "https://api.open-elevation.com/api/v1/lookup"
    
    def analyze_route_elevation(self, route_points: List) -> Dict:
        """Complete elevation analysis with gradient risk assessment"""
        
        if not route_points:
            return {'error': 'No route points provided'}
        
        print("⛰️ Starting Advanced Elevation Analysis...")
        
        # Sample points for elevation analysis (max 512 for Google API)
        sampled_points = self.sample_route_points(route_points, max_points=100)
        
        # Get elevation data
        elevation_data = self.get_elevation_data(sampled_points)
        
        if not elevation_data:
            return {'error': 'Failed to retrieve elevation data'}
        
        # Advanced analysis
        analysis = {
            'elevation_profile': elevation_data,
            'gradient_analysis': self.analyze_gradients(elevation_data),
            'ascent_descent_mapping': self.map_ascent_descent(elevation_data),
            'risk_assessment': self.assess_gradient_risks(elevation_data),
            'elevation_statistics': self.calculate_elevation_stats(elevation_data),
            'driving_recommendations': self.generate_elevation_recommendations(elevation_data)
        }
        
        return analysis
    
    def sample_route_points(self, route_points: List, max_points: int = 100) -> List:
        """Sample route points evenly for elevation analysis"""
        if len(route_points) <= max_points:
            return route_points
        
        step = len(route_points) // max_points
        return route_points[::step]
    
    def get_elevation_data(self, route_points: List) -> List[Dict]:
        """Get elevation data using Google API first, fallback to Open Elevation"""
        
        if self.google_api_key:
            print("🔄 Using Google Elevation API...")
            elevation_data = self.get_google_elevation(route_points)
            if elevation_data:
                return elevation_data
        
        print("🔄 Using Open Elevation API (free)...")
        return self.get_open_elevation(route_points)
    
    def get_google_elevation(self, route_points: List) -> List[Dict]:
        """Get elevation using Google Elevation API"""
        try:
            # Process in batches of 100 points
            all_elevation_data = []
            batch_size = 100
            
            for i in range(0, len(route_points), batch_size):
                batch = route_points[i:i + batch_size]
                locations = '|'.join([f"{point[0]},{point[1]}" for point in batch])
                
                url = "https://maps.googleapis.com/maps/api/elevation/json"
                params = {
                    'locations': locations,
                    'key': self.google_api_key
                }
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('status') == 'OK':
                        for j, result in enumerate(data.get('results', [])):
                            route_index = i + j
                            elevation_data = {
                                'index': route_index,
                                'location': result.get('location', {}),
                                'elevation': result.get('elevation', 0),
                                'resolution': result.get('resolution', 0),
                                'distance_from_start': self.calculate_distance_from_start(route_points, route_index)
                            }
                            all_elevation_data.append(elevation_data)
            
            print(f"✅ Google Elevation API: Retrieved {len(all_elevation_data)} elevation points")
            return all_elevation_data
            
        except Exception as e:
            print(f"❌ Google Elevation API error: {e}")
            return None
    
    def get_open_elevation(self, route_points: List) -> List[Dict]:
        """Get elevation using Open Elevation API (free)"""
        try:
            # Process in smaller batches for free API
            all_elevation_data = []
            batch_size = 50  # Smaller batches for free API
            
            for i in range(0, len(route_points), batch_size):
                batch = route_points[i:i + batch_size]
                
                locations = [{"latitude": point[0], "longitude": point[1]} for point in batch]
                
                payload = {"locations": locations}
                response = requests.post(self.open_elevation_url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for j, result in enumerate(data.get('results', [])):
                        route_index = i + j
                        elevation_data = {
                            'index': route_index,
                            'location': {
                                'lat': result.get('latitude'),
                                'lng': result.get('longitude')
                            },
                            'elevation': result.get('elevation', 0),
                            'resolution': 30,  # SRTM resolution
                            'distance_from_start': self.calculate_distance_from_start(route_points, route_index)
                        }
                        all_elevation_data.append(elevation_data)
                
                # Rate limiting for free API
                import time
                time.sleep(0.5)
            
            print(f"✅ Open Elevation API: Retrieved {len(all_elevation_data)} elevation points")
            return all_elevation_data
            
        except Exception as e:
            print(f"❌ Open Elevation API error: {e}")
            return []
    
    def calculate_distance_from_start(self, route_points: List, index: int) -> float:
        """Calculate cumulative distance from route start"""
        try:
            from geopy.distance import geodesic
            
            if index == 0:
                return 0.0
            
            total_distance = 0.0
            for i in range(1, min(index + 1, len(route_points))):
                prev_point = route_points[i-1]
                curr_point = route_points[i]
                segment_distance = geodesic(prev_point, curr_point).kilometers
                total_distance += segment_distance
            
            return total_distance
            
        except Exception:
            return float(index) * 0.1  # Fallback estimation
    
    def analyze_gradients(self, elevation_data: List[Dict]) -> Dict:
        """Analyze route gradients and slopes"""
        if len(elevation_data) < 2:
            return {'error': 'Insufficient elevation data for gradient analysis'}
        
        gradients = []
        steep_climbs = []
        steep_descents = []
        
        for i in range(1, len(elevation_data)):
            prev_point = elevation_data[i-1]
            curr_point = elevation_data[i]
            
            elevation_diff = curr_point['elevation'] - prev_point['elevation']
            distance_diff = curr_point['distance_from_start'] - prev_point['distance_from_start']
            
            if distance_diff > 0:
                gradient_percent = (elevation_diff / (distance_diff * 1000)) * 100  # Convert to percentage
                
                gradient_info = {
                    'segment_start': prev_point['distance_from_start'],
                    'segment_end': curr_point['distance_from_start'],
                    'elevation_change': elevation_diff,
                    'gradient_percent': gradient_percent,
                    'location': curr_point['location']
                }
                
                gradients.append(gradient_info)
                
                # Classify steep sections
                if gradient_percent > 8:  # Steep climb
                    steep_climbs.append(gradient_info)
                elif gradient_percent < -8:  # Steep descent
                    steep_descents.append(gradient_info)
        
        return {
            'total_gradients': len(gradients),
            'steep_climbs': steep_climbs,
            'steep_descents': steep_descents,
            'max_climb_gradient': max([g['gradient_percent'] for g in gradients]) if gradients else 0,
            'max_descent_gradient': min([g['gradient_percent'] for g in gradients]) if gradients else 0,
            'gradient_distribution': self.categorize_gradients(gradients)
        }
    
    def categorize_gradients(self, gradients: List[Dict]) -> Dict:
        """Categorize gradients by severity"""
        categories = {
            'flat': 0,          # 0-2%
            'gentle': 0,        # 2-5%
            'moderate': 0,      # 5-8%
            'steep': 0,         # 8-12%
            'very_steep': 0     # >12%
        }
        
        for gradient in gradients:
            percent = abs(gradient['gradient_percent'])
            
            if percent <= 2:
                categories['flat'] += 1
            elif percent <= 5:
                categories['gentle'] += 1
            elif percent <= 8:
                categories['moderate'] += 1
            elif percent <= 12:
                categories['steep'] += 1
            else:
                categories['very_steep'] += 1
        
        return categories
    
    def map_ascent_descent(self, elevation_data: List[Dict]) -> Dict:
        """Map detailed ascent and descent sections"""
        if len(elevation_data) < 2:
            return {'error': 'Insufficient data for ascent/descent mapping'}
        
        ascent_sections = []
        descent_sections = []
        
        current_section = None
        section_type = None
        
        for i in range(1, len(elevation_data)):
            prev_elev = elevation_data[i-1]['elevation']
            curr_elev = elevation_data[i]['elevation']
            elevation_diff = curr_elev - prev_elev
            
            if elevation_diff > 1:  # Ascending
                if section_type != 'ascent':
                    # Start new ascent section
                    if current_section:
                        if section_type == 'descent':
                            descent_sections.append(current_section)
                    
                    current_section = {
                        'start_distance': elevation_data[i-1]['distance_from_start'],
                        'start_elevation': prev_elev,
                        'start_location': elevation_data[i-1]['location']
                    }
                    section_type = 'ascent'
                
                # Update current ascent section
                current_section.update({
                    'end_distance': elevation_data[i]['distance_from_start'],
                    'end_elevation': curr_elev,
                    'end_location': elevation_data[i]['location'],
                    'total_elevation_gain': curr_elev - current_section['start_elevation'],
                    'section_length': elevation_data[i]['distance_from_start'] - current_section['start_distance']
                })
                
            elif elevation_diff < -1:  # Descending
                if section_type != 'descent':
                    # Start new descent section
                    if current_section:
                        if section_type == 'ascent':
                            ascent_sections.append(current_section)
                    
                    current_section = {
                        'start_distance': elevation_data[i-1]['distance_from_start'],
                        'start_elevation': prev_elev,
                        'start_location': elevation_data[i-1]['location']
                    }
                    section_type = 'descent'
                
                # Update current descent section
                current_section.update({
                    'end_distance': elevation_data[i]['distance_from_start'],
                    'end_elevation': curr_elev,
                    'end_location': elevation_data[i]['location'],
                    'total_elevation_loss': current_section['start_elevation'] - curr_elev,
                    'section_length': elevation_data[i]['distance_from_start'] - current_section['start_distance']
                })
        
        # Add final section
        if current_section:
            if section_type == 'ascent':
                ascent_sections.append(current_section)
            elif section_type == 'descent':
                descent_sections.append(current_section)
        
        return {
            'ascent_sections': ascent_sections,
            'descent_sections': descent_sections,
            'total_ascent_sections': len(ascent_sections),
            'total_descent_sections': len(descent_sections),
            'major_climbs': [section for section in ascent_sections if section.get('total_elevation_gain', 0) > 100],
            'major_descents': [section for section in descent_sections if section.get('total_elevation_loss', 0) > 100]
        }
    
    def assess_gradient_risks(self, elevation_data: List[Dict]) -> Dict:
        """Assess risks based on elevation gradients"""
        gradient_analysis = self.analyze_gradients(elevation_data)
        
        if 'error' in gradient_analysis:
            return gradient_analysis
        
        risk_segments = []
        recommendations = []
        
        # Analyze steep climbs
        for climb in gradient_analysis['steep_climbs']:
            if climb['gradient_percent'] > 12:
                risk_level = 'CRITICAL'
                risk_description = f"Extremely steep climb: {climb['gradient_percent']:.1f}% gradient"
            elif climb['gradient_percent'] > 8:
                risk_level = 'HIGH'
                risk_description = f"Steep climb: {climb['gradient_percent']:.1f}% gradient"
            else:
                continue
            
            risk_segments.append({
                'location': climb['location'],
                'distance_km': climb['segment_start'],
                'risk_level': risk_level,
                'risk_type': 'STEEP_CLIMB',
                'description': risk_description,
                'gradient_percent': climb['gradient_percent']
            })
        
        # Analyze steep descents
        for descent in gradient_analysis['steep_descents']:
            if descent['gradient_percent'] < -12:
                risk_level = 'CRITICAL'
                risk_description = f"Extremely steep descent: {abs(descent['gradient_percent']):.1f}% gradient"
            elif descent['gradient_percent'] < -8:
                risk_level = 'HIGH'
                risk_description = f"Steep descent: {abs(descent['gradient_percent']):.1f}% gradient"
            else:
                continue
            
            risk_segments.append({
                'location': descent['location'],
                'distance_km': descent['segment_start'],
                'risk_level': risk_level,
                'risk_type': 'STEEP_DESCENT',
                'description': risk_description,
                'gradient_percent': descent['gradient_percent']
            })
        
        return {
            'total_risk_segments': len(risk_segments),
            'critical_segments': len([r for r in risk_segments if r['risk_level'] == 'CRITICAL']),
            'high_risk_segments': len([r for r in risk_segments if r['risk_level'] == 'HIGH']),
            'risk_segments': sorted(risk_segments, key=lambda x: x.get('gradient_percent', 0), reverse=True),
            'overall_risk_level': self.calculate_overall_elevation_risk(risk_segments)
        }
    
    def calculate_overall_elevation_risk(self, risk_segments: List[Dict]) -> str:
        """Calculate overall elevation risk level"""
        if not risk_segments:
            return 'LOW'
        
        critical_count = len([r for r in risk_segments if r['risk_level'] == 'CRITICAL'])
        high_count = len([r for r in risk_segments if r['risk_level'] == 'HIGH'])
        
        if critical_count > 2:
            return 'EXTREME'
        elif critical_count > 0 or high_count > 3:
            return 'HIGH'
        elif high_count > 0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def calculate_elevation_stats(self, elevation_data: List[Dict]) -> Dict:
        """Calculate elevation statistics"""
        if not elevation_data:
            return {'error': 'No elevation data available'}
        
        elevations = [point['elevation'] for point in elevation_data]
        
        return {
            'min_elevation': min(elevations),
            'max_elevation': max(elevations),
            'elevation_range': max(elevations) - min(elevations),
            'average_elevation': sum(elevations) / len(elevations),
            'total_ascent': sum([max(0, elevation_data[i]['elevation'] - elevation_data[i-1]['elevation']) 
                               for i in range(1, len(elevation_data))]),
            'total_descent': sum([max(0, elevation_data[i-1]['elevation'] - elevation_data[i]['elevation']) 
                                for i in range(1, len(elevation_data))]),
            'elevation_variance': np.var(elevations) if len(elevations) > 1 else 0
        }
    
    def generate_elevation_recommendations(self, elevation_data: List[Dict]) -> List[Dict]:
        """Generate driving recommendations based on elevation analysis"""
        gradient_analysis = self.analyze_gradients(elevation_data)
        risk_assessment = self.assess_gradient_risks(elevation_data)
        elevation_stats = self.calculate_elevation_stats(elevation_data)
        
        recommendations = []
        
        # Critical gradient recommendations
        if risk_assessment.get('critical_segments', 0) > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Extreme Gradients',
                'title': f"{risk_assessment['critical_segments']} Critical Steep Sections",
                'description': 'Route contains extremely steep gradients requiring special precautions',
                'actions': [
                    'Use low gear for steep climbs and descents',
                    'Check brake system before journey',
                    'Avoid overloading vehicle for steep sections',
                    'Plan additional fuel for steep climbs',
                    'Consider alternate route if vehicle not suitable'
                ]
            })
        
        # High elevation change recommendation
        if elevation_stats.get('elevation_range', 0) > 1000:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Significant Elevation Change',
                'title': f"Major Elevation Change: {elevation_stats['elevation_range']:.0f}m",
                'description': 'Route involves significant altitude changes',
                'actions': [
                    'Monitor engine temperature on climbs',
                    'Check tire pressure at different altitudes',
                    'Carry extra coolant and brake fluid',
                    'Plan for reduced engine performance at high altitude'
                ]
            })
        
        # General elevation recommendations
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'General Elevation Precautions',
            'title': 'Standard Mountain/Hill Driving Precautions',
            'description': 'Route elevation profile requires standard hill driving techniques',
            'actions': [
                'Maintain steady speed on gradients',
                'Use engine braking on descents',
                'Keep adequate following distance',
                'Monitor vehicle temperature gauges',
                'Plan rest stops at safe locations'
            ]
        })
        
        return recommendations

    def create_elevation_graph(self, elevation_data: List[Dict]) -> str:
        """Create elevation profile graph and return file path"""
        try:
            if not elevation_data:
                return None
            
            distances = [point['distance_from_start'] for point in elevation_data]
            elevations = [point['elevation'] for point in elevation_data]
            
            plt.figure(figsize=(12, 6))
            plt.plot(distances, elevations, 'b-', linewidth=2, label='Elevation Profile')
            plt.fill_between(distances, elevations, alpha=0.3)
            
            plt.xlabel('Distance from Start (km)')
            plt.ylabel('Elevation (m)')
            plt.title('Route Elevation Profile')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                plt.savefig(temp_file.name, dpi=300, bbox_inches='tight')
                plt.close()
                return temp_file.name
                
        except Exception as e:
            print(f"Error creating elevation graph: {e}")
            return None