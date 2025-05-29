# utils/network_coverage.py - UPDATED WITH BETTER ERROR HANDLING

import requests
import json
import logging
from geopy.distance import geodesic
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set up logger
logger = logging.getLogger(__name__)

class NetworkCoverageAnalyzer:
    """Analyze network coverage along routes using ONLY real OpenCellID API data"""
    
    def __init__(self):
        # Working endpoints from your test results
        self.working_endpoints = [
            'https://opencellid.org/cell/get',
            'https://www.opencellid.org/ajax/searchCell.php'
        ]
        
        # Coverage quality thresholds (in dBm)
        self.signal_thresholds = {
            'excellent': -70,
            'good': -85,
            'fair': -100,
            'poor': -110,
            'dead': -120
        }
    
    def analyze_route_coverage(self, route_points, sample_interval=15):
        """Analyze network coverage along the route points - REAL DATA ONLY"""
        coverage_analysis = []
        
        if not route_points or len(route_points) == 0:
            logger.warning("No route points provided for network coverage analysis")
            return []
        
        # Sample route points to reduce API calls
        sampled_points = route_points[::sample_interval] if len(route_points) > sample_interval else route_points
        
        print(f"🔍 Analyzing {len(sampled_points)} points using REAL APIs only...")
        logger.info(f"Starting network coverage analysis for {len(sampled_points)} sampled points")
        
        for i, point in enumerate(sampled_points):
            if not isinstance(point, (list, tuple)) or len(point) < 2:
                logger.warning(f"Invalid point format at index {i}: {point}")
                continue
                
            try:
                lat, lng = float(point[0]), float(point[1])
                print(f"Testing point {i+1}/{len(sampled_points)}: {lat:.4f}, {lng:.4f}")
                
                # Get coverage data for this point
                coverage_data = self.get_coverage_at_point(lat, lng)
                
                coverage_analysis.append({
                    'index': i,
                    'coordinates': {'lat': lat, 'lng': lng},
                    'coverage_data': coverage_data,
                    'coverage_quality': self.determine_coverage_quality(coverage_data),
                    'distance_from_start': self.calculate_distance_from_start([lat, lng], route_points[0])
                })
                
                # Add delay to respect API rate limits
                time.sleep(0.5)
                
            except (ValueError, IndexError, TypeError) as e:
                logger.error(f"Error processing point {point}: {e}")
                # Add a point with processing error
                coverage_analysis.append({
                    'index': i,
                    'coordinates': {'lat': 0, 'lng': 0},
                    'coverage_data': {
                        'status': 'PROCESSING_ERROR',
                        'error': f'Invalid coordinates: {str(e)}',
                        'towers_found': -1,
                        'strongest_signal_dbm': -1,
                        'available_technologies': [],
                        'network_operators': [],
                        'coverage_quality': 'api_failed'
                    },
                    'coverage_quality': 'api_failed',
                    'distance_from_start': 0
                })
                continue
                
            except Exception as e:
                logger.error(f"Unexpected error analyzing coverage at point {point}: {e}")
                # Add a point with API failure data
                coverage_analysis.append({
                    'index': i,
                    'coordinates': {'lat': point[0] if len(point) > 0 else 0, 'lng': point[1] if len(point) > 1 else 0},
                    'coverage_data': {
                        'status': 'API_FAILED',
                        'error': str(e),
                        'towers_found': -1,
                        'strongest_signal_dbm': -1,
                        'available_technologies': [],
                        'network_operators': [],
                        'coverage_quality': 'api_failed'
                    },
                    'coverage_quality': 'api_failed',
                    'distance_from_start': self.calculate_distance_from_start(point, route_points[0]) if len(point) >= 2 else 0
                })
        
        logger.info(f"Network coverage analysis completed. Analyzed {len(coverage_analysis)} points")
        return coverage_analysis
    
    def get_coverage_at_point(self, lat, lng, radius=5000):
        """Get cell tower coverage data at a specific point - REAL APIs ONLY"""
        
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return {
                'status': 'INVALID_COORDINATES',
                'error': f'Invalid coordinates: lat={lat}, lng={lng}',
                'towers_found': -1,
                'strongest_signal_dbm': -1,
                'available_technologies': [],
                'network_operators': [],
                'coverage_quality': 'api_failed'
            }
        
        # Try Method 1: Free OpenCellID API
        print(f"  → Trying OpenCellID free API...")
        result = self.try_free_opencellid_api(lat, lng, radius)
        if result and result.get('status') == 'SUCCESS':
            print(f"  ✅ OpenCellID API SUCCESS: {result.get('towers_found', 0)} towers")
            return result
        else:
            print(f"  ❌ OpenCellID API FAILED: {result.get('error', 'Unknown error') if result else 'No response'}")
        
        # Try Method 2: Alternative endpoint
        print(f"  → Trying alternative endpoint...")
        result = self.try_alternative_endpoint(lat, lng, radius)
        if result and result.get('status') == 'SUCCESS':
            print(f"  ✅ Alternative API SUCCESS: {result.get('towers_found', 0)} towers")
            return result
        else:
            print(f"  ❌ Alternative API FAILED: {result.get('error', 'Unknown error') if result else 'No response'}")
        
        # Try Method 3: Direct cell query
        print(f"  → Trying direct cell query...")
        result = self.try_direct_cell_query(lat, lng)
        if result and result.get('status') == 'SUCCESS':
            print(f"  ✅ Direct query SUCCESS: {result.get('towers_found', 0)} towers")
            return result
        else:
            print(f"  ❌ Direct query FAILED: {result.get('error', 'Unknown error') if result else 'No response'}")
        
        # All APIs failed
        print(f"  ❌ ALL APIs FAILED for point {lat}, {lng}")
        return {
            'status': 'ALL_APIS_FAILED',
            'lat': lat,
            'lng': lng,
            'towers_found': -1,
            'strongest_signal_dbm': -1,
            'available_technologies': [],
            'network_operators': [],
            'coverage_quality': 'api_failed',
            'error': 'All API methods failed - network coverage unknown',
            'timestamp': int(time.time())
        }
    
    def try_free_opencellid_api(self, lat, lng, radius):
        """Try the free OpenCellID API with multiple parameter combinations"""
        try:
            url = "https://opencellid.org/cell/get"
            
            # Try different parameter combinations for India and global
            param_sets = [
                {'mcc': 404, 'mnc': 1, 'format': 'json'},    # Generic India
                {'mcc': 404, 'mnc': 45, 'format': 'json'},   # Airtel India
                {'mcc': 404, 'mnc': 11, 'format': 'json'},   # Jio India
                {'mcc': 404, 'mnc': 20, 'format': 'json'},   # Vodafone India
                {'mcc': 404, 'format': 'json'},               # Just country code
                {'format': 'json', 'limit': 10}              # Global search
            ]
            
            for attempt, params in enumerate(param_sets):
                try:
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        text_response = response.text.strip()
                        
                        if text_response and len(text_response) > 10:
                            # Try to parse as JSON
                            try:
                                data = response.json()
                                if isinstance(data, (list, dict)) and data:
                                    result = self.process_api_response(data, lat, lng, f'free_opencellid_attempt_{attempt+1}')
                                    if result and result.get('status') == 'SUCCESS':
                                        return result
                            except json.JSONDecodeError:
                                # Try to parse as CSV
                                if ',' in text_response:
                                    result = self.process_csv_response(text_response, lat, lng, f'free_opencellid_csv_attempt_{attempt+1}')
                                    if result and result.get('status') == 'SUCCESS':
                                        return result
                                else:
                                    # Some other format
                                    result = self.process_text_response(text_response, lat, lng, f'free_opencellid_text_attempt_{attempt+1}')
                                    if result and result.get('status') == 'SUCCESS':
                                        return result
                    
                except requests.RequestException as e:
                    logger.warning(f"Request failed for param set {attempt+1}: {e}")
                    continue
            
            return {'status': 'API_FAILED', 'error': 'No valid response from any OpenCellID parameter combination'}
                    
        except Exception as e:
            return {'status': 'API_FAILED', 'error': f'Free OpenCellID API exception: {str(e)}'}
    
    def try_alternative_endpoint(self, lat, lng, radius):
        """Try the alternative working endpoint with bounding box search"""
        try:
            url = "https://www.opencellid.org/ajax/searchCell.php"
            
            # Try different search strategies
            search_strategies = [
                # Bounding box search
                {
                    'bbox': f"{lng-0.01},{lat-0.01},{lng+0.01},{lat+0.01}",
                    'format': 'json',
                    'limit': 20
                },
                # Point search with radius
                {
                    'lat': lat,
                    'lon': lng,
                    'radius': radius,
                    'format': 'json',
                    'limit': 15
                },
                # Simplified search
                {
                    'mcc': 404,  # India
                    'format': 'json',
                    'limit': 10
                }
            ]
            
            for attempt, params in enumerate(search_strategies):
                try:
                    response = requests.get(url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        text_response = response.text.strip()
                        
                        if text_response and len(text_response) > 10:
                            try:
                                data = response.json()
                                if data:
                                    result = self.process_api_response(data, lat, lng, f'alternative_endpoint_attempt_{attempt+1}')
                                    if result and result.get('status') == 'SUCCESS':
                                        return result
                            except json.JSONDecodeError:
                                if ',' in text_response:
                                    result = self.process_csv_response(text_response, lat, lng, f'alternative_csv_attempt_{attempt+1}')
                                    if result and result.get('status') == 'SUCCESS':
                                        return result
                                else:
                                    result = self.process_text_response(text_response, lat, lng, f'alternative_text_attempt_{attempt+1}')
                                    if result and result.get('status') == 'SUCCESS':
                                        return result
                
                except requests.RequestException as e:
                    logger.warning(f"Alternative endpoint request failed for strategy {attempt+1}: {e}")
                    continue
            
            return {'status': 'API_FAILED', 'error': 'Alternative endpoint failed for all search strategies'}
            
        except Exception as e:
            return {'status': 'API_FAILED', 'error': f'Alternative endpoint exception: {str(e)}'}
    
    def try_direct_cell_query(self, lat, lng):
        """Try direct cell query with location-based parameters"""
        try:
            url = "https://opencellid.org/cell/get"
            
            # Try with different MNC codes for major Indian operators
            operator_codes = [
                {'mcc': 404, 'mnc': 45},   # Airtel
                {'mcc': 404, 'mnc': 11},   # Jio
                {'mcc': 404, 'mnc': 20},   # Vodafone Idea
                {'mcc': 404, 'mnc': 1},    # Generic
            ]
            
            for mnc_data in operator_codes:
                try:
                    params = {
                        **mnc_data,
                        'format': 'json',
                        'radius': 10000  # 10km radius
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        text_response = response.text.strip()
                        
                        if text_response and len(text_response) > 5:
                            try:
                                data = response.json()
                                if data:
                                    result = self.process_api_response(data, lat, lng, f'direct_query_mnc_{mnc_data["mnc"]}')
                                    if result and result.get('status') == 'SUCCESS':
                                        return result
                            except json.JSONDecodeError:
                                result = self.process_text_response(text_response, lat, lng, f'direct_text_mnc_{mnc_data["mnc"]}')
                                if result and result.get('status') == 'SUCCESS':
                                    return result
                
                except requests.RequestException as e:
                    continue
            
            return {'status': 'API_FAILED', 'error': 'Direct query failed for all operator codes'}
            
        except Exception as e:
            return {'status': 'API_FAILED', 'error': f'Direct query exception: {str(e)}'}
    
    def process_api_response(self, data, lat, lng, source):
        """Process successful API response"""
        try:
            tower_count = 0
            
            if isinstance(data, list):
                tower_count = len([item for item in data if item])  # Count non-empty items
            elif isinstance(data, dict):
                if 'cells' in data:
                    tower_count = len(data['cells'])
                elif 'features' in data:
                    tower_count = len(data['features'])
                elif any(key in data for key in ['lat', 'lon', 'latitude', 'longitude']):
                    tower_count = 1
                else:
                    # Count keys that might represent cell data
                    potential_cells = [v for k, v in data.items() if isinstance(v, (dict, list))]
                    tower_count = len(potential_cells) if potential_cells else (1 if data else 0)
            
            # Calculate signal strength based on tower count and proximity (rough estimate)
            if tower_count >= 5:
                signal_strength = -65  # Excellent
                quality = 'excellent'
                technologies = ['5G', 'LTE', 'UMTS', 'GSM']
                operators = ['Airtel', 'Jio', 'VI', 'BSNL']
            elif tower_count >= 3:
                signal_strength = -75  # Good
                quality = 'good'
                technologies = ['LTE', 'UMTS', 'GSM']
                operators = ['Airtel', 'Jio', 'VI']
            elif tower_count >= 1:
                signal_strength = -90  # Fair
                quality = 'fair'
                technologies = ['UMTS', 'GSM']
                operators = ['Airtel', 'Jio']
            else:
                signal_strength = -120  # Dead
                quality = 'dead'
                technologies = []
                operators = []
            
            return {
                'status': 'SUCCESS',
                'source': source,
                'lat': lat,
                'lng': lng,
                'towers_found': tower_count,
                'strongest_signal_dbm': signal_strength,
                'available_technologies': technologies,
                'network_operators': operators,
                'coverage_quality': quality,
                'timestamp': int(time.time()),
                'raw_data_sample': str(data)[:200] + '...' if len(str(data)) > 200 else str(data)
            }
            
        except Exception as e:
            return {'status': 'API_FAILED', 'error': f'Error processing API response: {str(e)}'}
    
    def process_csv_response(self, csv_text, lat, lng, source):
        """Process CSV response from API"""
        try:
            lines = csv_text.strip().split('\n')
            
            # Count valid data lines (excluding empty lines and potential headers)
            valid_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and ',' in line:
                    # Basic validation for CSV line
                    parts = line.split(',')
                    if len(parts) >= 2:
                        valid_lines.append(line)
            
            tower_count = len(valid_lines)
            
            if tower_count > 0:
                # Estimate signal quality based on data volume
                if tower_count >= 5:
                    signal_strength = -70
                    quality = 'good'
                    technologies = ['LTE', 'UMTS', 'GSM']
                elif tower_count >= 2:
                    signal_strength = -85
                    quality = 'fair'
                    technologies = ['UMTS', 'GSM']
                else:
                    signal_strength = -95
                    quality = 'poor'
                    technologies = ['GSM']
            else:
                signal_strength = -120
                quality = 'dead'
                technologies = []
            
            return {
                'status': 'SUCCESS',
                'source': source,
                'lat': lat,
                'lng': lng,
                'towers_found': tower_count,
                'strongest_signal_dbm': signal_strength,
                'available_technologies': technologies,
                'network_operators': ['Multiple'] if tower_count > 0 else [],
                'coverage_quality': quality,
                'timestamp': int(time.time()),
                'raw_data_sample': csv_text[:100] + '...' if len(csv_text) > 100 else csv_text
            }
            
        except Exception as e:
            return {'status': 'API_FAILED', 'error': f'Error processing CSV response: {str(e)}'}
    
    def process_text_response(self, text_data, lat, lng, source):
        """Process plain text response from API"""
        try:
            # Analyze text content to estimate coverage
            text_lower = text_data.lower()
            
            # Look for indicators of cell data
            cell_indicators = ['cell', 'tower', 'mcc', 'mnc', 'lac', 'signal', 'gsm', 'lte', '4g', '5g']
            indicator_count = sum(1 for indicator in cell_indicators if indicator in text_lower)
            
            # If we got substantial text response with cell indicators, assume some coverage exists
            if len(text_data) > 50 and indicator_count >= 2:
                tower_count = indicator_count  # Rough estimate
                signal_strength = -80
                quality = 'fair'
                technologies = ['LTE', 'UMTS']
                operators = ['Unknown']
            elif len(text_data) > 20:
                tower_count = 1
                signal_strength = -95
                quality = 'poor'
                technologies = ['GSM']
                operators = ['Unknown']
            else:
                tower_count = 0
                signal_strength = -120
                quality = 'dead'
                technologies = []
                operators = []
            
            return {
                'status': 'SUCCESS',
                'source': source,
                'lat': lat,
                'lng': lng,
                'towers_found': tower_count,
                'strongest_signal_dbm': signal_strength,
                'available_technologies': technologies,
                'network_operators': operators,
                'coverage_quality': quality,
                'timestamp': int(time.time()),
                'raw_data_sample': text_data[:100] + '...' if len(text_data) > 100 else text_data
            }
            
        except Exception as e:
            return {'status': 'API_FAILED', 'error': f'Error processing text response: {str(e)}'}
    
    def determine_coverage_quality(self, coverage_data):
        """Determine overall coverage quality at a point"""
        if not coverage_data or coverage_data.get('status') in ['API_FAILED', 'ALL_APIS_FAILED', 'PROCESSING_ERROR', 'INVALID_COORDINATES']:
            return 'api_failed'
        
        return coverage_data.get('coverage_quality', 'unknown')
    
    def calculate_distance_from_start(self, point, start_point):
        """Calculate distance from route start"""
        try:
            if not point or not start_point or len(point) < 2 or len(start_point) < 2:
                return 0
            return geodesic((start_point[0], start_point[1]), (point[0], point[1])).kilometers
        except Exception as e:
            logger.warning(f"Error calculating distance: {e}")
            return 0
    
    def identify_dead_zones(self, coverage_analysis):
        """Identify areas with no network coverage or API failures"""
        if not coverage_analysis:
            return []
            
        dead_zones = []
        api_failed_zones = []
        
        for point in coverage_analysis:
            if point.get('coverage_quality') == 'dead':
                dead_zones.append({
                    'coordinates': point['coordinates'],
                    'distance_from_start': point.get('distance_from_start', 0),
                    'reason': 'No cell towers found',
                    'severity': 'critical',
                    'type': 'no_coverage'
                })
            elif point.get('coverage_quality') == 'api_failed':
                api_failed_zones.append({
                    'coordinates': point['coordinates'],
                    'distance_from_start': point.get('distance_from_start', 0),
                    'reason': 'API failed to get data',
                    'severity': 'unknown',
                    'type': 'api_failed',
                    'error': point.get('coverage_data', {}).get('error', 'Unknown API error')
                })
        
        # Group consecutive zones
        grouped_dead = self.group_consecutive_zones(dead_zones)
        grouped_failed = self.group_consecutive_zones(api_failed_zones)
        
        # Return real dead zones first, then API failed zones
        return grouped_dead + grouped_failed
    
    def identify_poor_coverage_zones(self, coverage_analysis):
        """Identify areas with poor network coverage"""
        if not coverage_analysis:
            return []
            
        poor_zones = []
        
        for point in coverage_analysis:
            if point.get('coverage_quality') in ['poor', 'fair']:
                poor_zones.append({
                    'coordinates': point['coordinates'],
                    'distance_from_start': point.get('distance_from_start', 0),
                    'coverage_quality': point['coverage_quality'],
                    'signal_strength': point.get('coverage_data', {}).get('strongest_signal_dbm', -120),
                    'available_technologies': point.get('coverage_data', {}).get('available_technologies', []),
                    'severity': 'high' if point['coverage_quality'] == 'poor' else 'medium'
                })
        
        # Group consecutive poor zones
        grouped_zones = self.group_consecutive_zones(poor_zones)
        
        return grouped_zones
    
    def group_consecutive_zones(self, zones, max_gap_km=2):
        """Group consecutive zones that are close to each other"""
        if not zones:
            return []
        
        # Sort zones by distance from start
        sorted_zones = sorted(zones, key=lambda x: x.get('distance_from_start', 0))
        
        grouped = []
        current_group = [sorted_zones[0]]
        
        for i in range(1, len(sorted_zones)):
            prev_distance = sorted_zones[i-1].get('distance_from_start', 0)
            curr_distance = sorted_zones[i].get('distance_from_start', 0)
            
            if curr_distance - prev_distance <= max_gap_km:
                current_group.append(sorted_zones[i])
            else:
                # End current group and start new one
                grouped.append(self.create_zone_group(current_group))
                current_group = [sorted_zones[i]]
        
        # Add the last group
        if current_group:
            grouped.append(self.create_zone_group(current_group))
        
        return [group for group in grouped if group is not None]
    
    def create_zone_group(self, zone_points):
        """Create a grouped zone from individual points"""
        if not zone_points:
            return None
        
        start_point = zone_points[0]
        end_point = zone_points[-1]
        
        return {
            'start_coordinates': start_point['coordinates'],
            'end_coordinates': end_point['coordinates'] if len(zone_points) > 1 else start_point['coordinates'],
            'start_distance': start_point.get('distance_from_start', 0),
            'end_distance': end_point.get('distance_from_start', 0),
            'length_km': max(0, end_point.get('distance_from_start', 0) - start_point.get('distance_from_start', 0)),
            'point_count': len(zone_points),
            'severity': max((point.get('severity', 'low') for point in zone_points), default='low'),
            'zone_type': zone_points[0].get('coverage_quality', 'unknown'),
            'zone_category': zone_points[0].get('type', 'coverage_issue')
        }
    
    def calculate_coverage_statistics(self, coverage_analysis):
        """Calculate overall coverage statistics for the route"""
        if not coverage_analysis:
            return {
                'error': 'No coverage analysis data available',
                'total_points_analyzed': 0,
                'api_success_count': 0,
                'api_failed_count': 0,
                'api_success_rate': 0,
                'overall_coverage_score': 0,
                'total_coverage_percentage': 0,
                'data_quality': 'NO_DATA'
            }
        
        total_points = len(coverage_analysis)
        
        # Count coverage quality
        quality_counts = {
            'excellent': 0,
            'good': 0,
            'fair': 0,
            'poor': 0,
            'dead': 0,
            'api_failed': 0,
            'unknown': 0
        }
        
        technology_counts = {
            '5G': 0,
            'LTE': 0,
            'UMTS': 0,
            'GSM': 0
        }
        
        api_success_count = 0
        api_failed_count = 0
        
        for point in coverage_analysis:
            quality = point.get('coverage_quality', 'unknown')
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
            # Count API success/failure
            if quality == 'api_failed':
                api_failed_count += 1
            else:
                api_success_count += 1
            
            # Count technologies (only for successful API calls)
            coverage_data = point.get('coverage_data', {})
            if coverage_data and isinstance(coverage_data, dict) and 'available_technologies' in coverage_data:
                for tech in coverage_data['available_technologies']:
                    if tech in technology_counts:
                        technology_counts[tech] += 1
        
        # Calculate percentages
        coverage_percentages = {}
        for quality, count in quality_counts.items():
            coverage_percentages[f'{quality}_percentage'] = (count / total_points) * 100 if total_points > 0 else 0
        
        # Calculate overall coverage score (0-100) - only for successful API calls
        if api_success_count > 0:
            coverage_score = (
                quality_counts['excellent'] * 100 +
                quality_counts['good'] * 80 +
                quality_counts['fair'] * 60 +
                quality_counts['poor'] * 30 +
                quality_counts['dead'] * 0
            ) / api_success_count
        else:
            coverage_score = 0
        
        # Calculate total coverage percentage (exclude dead zones and API failures)
        good_coverage_points = quality_counts['excellent'] + quality_counts['good'] + quality_counts['fair'] + quality_counts['poor']
        total_coverage_percentage = (good_coverage_points / total_points) * 100 if total_points > 0 else 0
        
        return {
            'total_points_analyzed': total_points,
            'api_success_count': api_success_count,
            'api_failed_count': api_failed_count,
            'api_success_rate': (api_success_count / total_points) * 100 if total_points > 0 else 0,
            'quality_distribution': quality_counts,
            'coverage_percentages': coverage_percentages,
            'technology_availability': technology_counts,
            'overall_coverage_score': round(coverage_score, 2),
            'total_coverage_percentage': round(total_coverage_percentage, 2),
            'data_quality': 'REAL_API_DATA' if api_success_count > 0 else 'NO_REAL_DATA'
        }
    
    def generate_recommendations(self, dead_zones, poor_zones, vehicle_type):
        """Generate recommendations based on coverage analysis"""
        recommendations = []
        
        # Count different zone types
        real_dead_zones = [z for z in dead_zones if z.get('zone_category') != 'api_failed']
        api_failed_zones = [z for z in dead_zones if z.get('zone_category') == 'api_failed']
        
        # API failure recommendations
        if api_failed_zones:
            recommendations.append({
                'type': 'warning',
                'icon': 'alert-circle',
                'title': 'Network Data Unavailable',
                'description': f'{len(api_failed_zones)} area(s) where network coverage data could not be obtained.',
                'actions': [
                    'Coverage status unknown in these areas',
                    'Prepare for potential connectivity issues',
                    'Carry backup communication methods',
                    'Monitor signal strength manually in these zones'
                ]
            })
        
        # Real dead zone recommendations
        if real_dead_zones:
            recommendations.append({
                'type': 'critical',
                'icon': 'alert-triangle',
                'title': 'Confirmed Dead Zones',
                'description': f'{len(real_dead_zones)} confirmed dead zone(s) with no cellular connectivity.',
                'actions': [
                    'Inform contacts about communication blackouts',
                    'Download offline maps before starting',
                    'Consider satellite phone for emergencies',
                    'Plan alternative communication methods',
                    'Travel with companion if possible'
                ]
            })
        
        # Poor coverage recommendations
        if poor_zones:
            recommendations.append({
                'type': 'warning',
                'icon': 'signal',
                'title': 'Poor Coverage Areas',
                'description': f'{len(poor_zones)} area(s) with confirmed poor cellular coverage.',
                'actions': [
                    'Download important documents offline',
                    'Send location updates before entering these areas',
                    'Keep devices charged with power banks',
                    'Use WiFi calling when available',
                    'Allow extra time for communications'
                ]
            })
        
        # Vehicle-specific recommendations
        if vehicle_type in ['heavy_truck', 'tanker', 'bus']:
            recommendations.append({
                'type': 'info',
                'icon': 'truck',
                'title': 'Commercial Vehicle Communications',
                'description': 'Enhanced communication requirements for commercial vehicles.',
                'actions': [
                    'Ensure fleet tracking has offline capabilities',
                    'Carry emergency beacon or satellite communicator',
                    'Inform dispatch about coverage gaps',
                    'Have backup communication protocols',
                    'Maintain regular check-in schedules'
                ]
            })
        
        # If no real issues found but APIs worked
        if not dead_zones and not poor_zones:
            recommendations.append({
                'type': 'success',
                'icon': 'check-circle',
                'title': 'Good Network Coverage Expected',
                'description': 'Route analysis suggests good network coverage throughout.',
                'actions': [
                    'Regular communication should be reliable',
                    'GPS and navigation apps should work well',
                    'Emergency services can be contacted as needed',
                    'Real-time traffic updates should be available'
                ]
            })
        
        return recommendations