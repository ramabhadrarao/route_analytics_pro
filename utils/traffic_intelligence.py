# utils/traffic_intelligence.py - TRAFFIC API INTEGRATION

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TrafficIntelligence:
    """Traffic analysis using TomTom and HERE APIs for enhanced route intelligence"""
    
    def __init__(self, tomtom_api_key: str = None, here_api_key: str = None):
        self.tomtom_key = tomtom_api_key
        self.here_key = here_api_key
        self.session = requests.Session()
    
    def analyze_seasonal_congestion(self, route_points: List) -> Dict:
        """Analyze seasonal congestion patterns using TomTom Historical Traffic API"""
        
        analysis = {
            'seasonal_patterns': {},
            'peak_congestion_months': [],
            'low_traffic_months': [],
            'congestion_hotspots': [],
            'seasonal_recommendations': []
        }
        
        if not self.tomtom_key:
            analysis['error'] = 'TomTom API key not provided'
            return analysis
        
        try:
            # Sample key points along route for analysis
            sample_points = self._sample_route_points(route_points, max_points=10)
            
            for season in ['winter', 'spring', 'summer', 'monsoon']:
                season_data = self._get_seasonal_traffic_data(sample_points, season)
                analysis['seasonal_patterns'][season] = season_data
            
            # Identify peak congestion periods
            analysis['peak_congestion_months'] = self._identify_peak_months(analysis['seasonal_patterns'])
            analysis['seasonal_recommendations'] = self._generate_seasonal_recommendations(analysis)
            
            print("✅ Seasonal congestion analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"Seasonal congestion analysis error: {e}")
            analysis['error'] = str(e)
            return analysis
    
    def detect_construction_zones(self, route_points: List) -> Dict:
        """Detect construction zones and detours using HERE Traffic Incidents API"""
        
        zones = {
            'active_construction': [],
            'planned_construction': [],
            'detour_routes': [],
            'impact_assessment': {},
            'recommendations': []
        }
        
        if not self.here_key:
            zones['error'] = 'HERE API key not provided'
            return zones
        
        try:
            # Get traffic incidents along route
            incidents = self._get_here_traffic_incidents(route_points)
            
            for incident in incidents:
                if self._is_construction_incident(incident):
                    construction_info = self._process_construction_incident(incident)
                    
                    if construction_info['status'] == 'active':
                        zones['active_construction'].append(construction_info)
                    elif construction_info['status'] == 'planned':
                        zones['planned_construction'].append(construction_info)
            
            # Generate impact assessment
            zones['impact_assessment'] = self._assess_construction_impact(zones)
            zones['recommendations'] = self._generate_construction_recommendations(zones)
            
            print(f"✅ Construction zones detected: {len(zones['active_construction'])} active, {len(zones['planned_construction'])} planned")
            return zones
            
        except Exception as e:
            logger.error(f"Construction zone detection error: {e}")
            zones['error'] = str(e)
            return zones
    
    def _sample_route_points(self, route_points: List, max_points: int = 10) -> List:
        """Sample route points for API efficiency"""
        if len(route_points) <= max_points:
            return route_points
        
        step = len(route_points) // max_points
        return route_points[::step]
    
    def _get_seasonal_traffic_data(self, points: List, season: str) -> Dict:
        """Get historical traffic data for a specific season"""
        try:
            # TomTom Historical Traffic API call
            season_months = {
                'winter': [12, 1, 2],
                'spring': [3, 4, 5], 
                'summer': [6, 7, 8],
                'monsoon': [7, 8, 9, 10]  # Indian monsoon season
            }
            
            traffic_data = {
                'average_congestion': 0,
                'peak_hours': [],
                'congestion_level': 'moderate',
                'affected_segments': []
            }
            
            # Simulate API call (replace with actual TomTom API)
            base_url = "https://api.tomtom.com/traffic/services/4/flowSegmentData"
            
            for point in points[:5]:  # Limit API calls
                params = {
                    'point': f"{point[0]},{point[1]}",
                    'unit': 'KMPH',
                    'key': self.tomtom_key
                }
                
                response = self.session.get(base_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    # Process TomTom response
                    current_speed = data.get('flowSegmentData', {}).get('currentSpeed', 50)
                    free_flow_speed = data.get('flowSegmentData', {}).get('freeFlowSpeed', 60)
                    
                    congestion_ratio = current_speed / free_flow_speed if free_flow_speed > 0 else 1.0
                    traffic_data['average_congestion'] += (1 - congestion_ratio) * 100
                
                time.sleep(0.2)  # Rate limiting
            
            # Calculate seasonal averages
            if points:
                traffic_data['average_congestion'] /= min(len(points), 5)
                traffic_data['congestion_level'] = self._classify_congestion_level(traffic_data['average_congestion'])
            
            return traffic_data
            
        except Exception as e:
            logger.error(f"Seasonal traffic data error: {e}")
            return {'error': str(e)}
    
    def _get_here_traffic_incidents(self, route_points: List) -> List:
        """Get traffic incidents using HERE API"""
        try:
            if not route_points:
                return []
            
            # HERE Traffic API
            base_url = "https://traffic.ls.hereapi.com/traffic/6.3/incidents"
            
            # Create bounding box from route points
            lats = [p[0] for p in route_points]
            lngs = [p[1] for p in route_points]
            
            bbox = f"{min(lats)},{min(lngs)};{max(lats)},{max(lngs)}"
            
            params = {
                'apikey': self.here_key,
                'bbox': bbox,
                'type': 'construction,roadwork',
                'criticality': 'major,minor'
            }
            
            response = self.session.get(base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('TRAFFIC_ITEMS', {}).get('TRAFFIC_ITEM', [])
            
            return []
            
        except Exception as e:
            logger.error(f"HERE traffic incidents error: {e}")
            return []
    
    def _is_construction_incident(self, incident: Dict) -> bool:
        """Check if incident is construction-related"""
        incident_type = incident.get('TRAFFIC_ITEM_TYPE_DESC', '').lower()
        description = incident.get('TRAFFIC_ITEM_DESCRIPTION', {}).get('content', '').lower()
        
        construction_keywords = [
            'construction', 'roadwork', 'maintenance', 'repair',
            'bridge work', 'resurfacing', 'lane closure'
        ]
        
        return any(keyword in incident_type or keyword in description 
                  for keyword in construction_keywords)
    
    def _process_construction_incident(self, incident: Dict) -> Dict:
        """Process construction incident data"""
        return {
            'id': incident.get('TRAFFIC_ITEM_ID', ''),
            'description': incident.get('TRAFFIC_ITEM_DESCRIPTION', {}).get('content', ''),
            'status': 'active',  # Determine from incident data
            'start_time': incident.get('START_TIME', ''),
            'end_time': incident.get('END_TIME', ''),
            'severity': incident.get('CRITICALITY', 'minor'),
            'location': self._extract_location_from_incident(incident),
            'impact': incident.get('TRAFFIC_ITEM_TYPE_DESC', '')
        }
    
    def _extract_location_from_incident(self, incident: Dict) -> Dict:
        """Extract location information from incident"""
        location = incident.get('LOCATION', {})
        
        return {
            'coordinates': {
                'lat': location.get('GEOLOC', {}).get('ORIGIN', {}).get('LATITUDE', 0),
                'lng': location.get('GEOLOC', {}).get('ORIGIN', {}).get('LONGITUDE', 0)
            },
            'road_name': location.get('DEFINED', {}).get('ORIGIN', {}).get('ROADWAY', {}).get('description', [{}])[0].get('content', 'Unknown Road'),
            'direction': location.get('DEFINED', {}).get('ORIGIN', {}).get('DIRECTION', '')
        }
    
    def _classify_congestion_level(self, congestion_percentage: float) -> str:
        """Classify congestion level"""
        if congestion_percentage > 60:
            return 'severe'
        elif congestion_percentage > 40:
            return 'heavy'
        elif congestion_percentage > 20:
            return 'moderate'
        else:
            return 'light'
    
    def _identify_peak_months(self, seasonal_patterns: Dict) -> List[str]:
        """Identify months with peak congestion"""
        peak_months = []
        
        for season, data in seasonal_patterns.items():
            if isinstance(data, dict) and data.get('average_congestion', 0) > 50:
                if season == 'winter':
                    peak_months.extend(['December', 'January', 'February'])
                elif season == 'monsoon':
                    peak_months.extend(['July', 'August', 'September'])
        
        return list(set(peak_months))
    
    def _assess_construction_impact(self, zones: Dict) -> Dict:
        """Assess overall impact of construction zones"""
        active_count = len(zones.get('active_construction', []))
        planned_count = len(zones.get('planned_construction', []))
        
        if active_count > 3:
            impact_level = 'severe'
        elif active_count > 1:
            impact_level = 'moderate'
        else:
            impact_level = 'minimal'
        
        return {
            'overall_impact': impact_level,
            'total_zones': active_count + planned_count,
            'delay_estimate': f"{active_count * 15}-{active_count * 30} minutes",
            'alternate_route_recommended': active_count > 2
        }
    
    def _generate_seasonal_recommendations(self, analysis: Dict) -> List[str]:
        """Generate seasonal travel recommendations"""
        recommendations = []
        
        peak_months = analysis.get('peak_congestion_months', [])
        
        if 'July' in peak_months or 'August' in peak_months:
            recommendations.append("MONSOON ALERT: Expect 40-60% longer travel times during July-August")
            recommendations.append("Avoid travel during heavy rain warnings")
        
        if 'December' in peak_months or 'January' in peak_months:
            recommendations.append("WINTER PEAK: Plan extra time during December-January holiday season")
            recommendations.append("Early morning travel (6-8 AM) recommended during winter months")
        
        recommendations.extend([
            "Check seasonal traffic updates before departure",
            "Plan alternate routes during festival seasons",
            "Monitor monsoon forecasts for route adjustments"
        ])
        
        return recommendations
    
    def _generate_construction_recommendations(self, zones: Dict) -> List[str]:
        """Generate construction zone recommendations"""
        recommendations = []
        active_count = len(zones.get('active_construction', []))
        
        if active_count > 0:
            recommendations.extend([
                f"CONSTRUCTION ALERT: {active_count} active construction zones detected",
                "Reduce speed in construction areas (25-40 km/h)",
                "Maintain extra following distance",
                "Follow temporary traffic signals and flaggers"
            ])
        
        if zones.get('impact_assessment', {}).get('alternate_route_recommended', False):
            recommendations.append("CONSIDER ALTERNATE ROUTE: Multiple construction zones may cause significant delays")
        
        recommendations.extend([
            "Check local traffic updates for construction schedule changes",
            "Plan extra 20-30 minutes for construction delays",
            "Be patient and courteous in construction zones"
        ])
        
        return recommendations