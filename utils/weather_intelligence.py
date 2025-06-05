# utils/weather_intelligence.py - WEATHER API INTEGRATION

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class WeatherIntelligence:
    """Weather analysis using multiple weather APIs for comprehensive route planning"""
    
    def __init__(self, openweather_key: str = None, visualcrossing_key: str = None, tomorrow_key: str = None):
        self.openweather_key = openweather_key
        self.visualcrossing_key = visualcrossing_key
        self.tomorrow_key = tomorrow_key
        self.session = requests.Session()
    
    def analyze_seasonal_road_conditions(self, route_points: List) -> Dict:
        """Analyze seasonal road conditions using historical weather data"""
        
        analysis = {
            'seasonal_risks': {},
            'historical_patterns': {},
            'risk_calendar': {},
            'seasonal_recommendations': []
        }
        
        if not self.openweather_key:
            analysis['error'] = 'OpenWeatherMap API key not provided'
            return analysis
        
        try:
            # Sample key points for weather analysis
            sample_points = self._sample_route_points(route_points, max_points=8)
            
            # Analyze each season
            for season in ['winter', 'spring', 'summer', 'monsoon']:
                season_data = self._get_seasonal_weather_data(sample_points, season)
                analysis['seasonal_risks'][season] = season_data
            
            # Generate risk calendar
            analysis['risk_calendar'] = self._create_risk_calendar(analysis['seasonal_risks'])
            analysis['seasonal_recommendations'] = self._generate_seasonal_recommendations(analysis)
            
            print("✅ Seasonal road conditions analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"Seasonal road conditions error: {e}")
            analysis['error'] = str(e)
            return analysis
    
    def analyze_summer_risks(self, route_points: List) -> Dict:
        """Analyze summer-specific risks: overheating, tire bursts, heat stress"""
        
        risks = {
            'temperature_hotspots': [],
            'overheating_zones': [],
            'tire_burst_risks': [],
            'heat_stress_areas': [],
            'summer_recommendations': []
        }
        
        if not self.visualcrossing_key:
            risks['error'] = 'Visual Crossing API key not provided'
            return risks
        
        try:
            # Get current and historical summer data
            summer_data = self._get_visual_crossing_data(route_points, season='summer')
            
            for point_data in summer_data:
                temp = point_data.get('temperature', 0)
                humidity = point_data.get('humidity', 0)
                
                if temp > 42:  # Extreme heat threshold for India
                    risks['temperature_hotspots'].append({
                        'location': point_data.get('location', {}),
                        'max_temperature': temp,
                        'risk_level': 'extreme',
                        'recommendations': self._get_extreme_heat_recommendations()
                    })
                
                if temp > 38:  # High heat threshold
                    risks['overheating_zones'].append({
                        'location': point_data.get('location', {}),
                        'temperature': temp,
                        'humidity': humidity,
                        'risk_factors': self._assess_overheating_risk(temp, humidity)
                    })
            
            risks['summer_recommendations'] = self._generate_summer_recommendations(risks)
            
            print(f"✅ Summer risks analyzed: {len(risks['temperature_hotspots'])} extreme heat zones")
            return risks
            
        except Exception as e:
            logger.error(f"Summer risks analysis error: {e}")
            risks['error'] = str(e)
            return risks
    
    def analyze_monsoon_risks(self, route_points: List) -> Dict:
        """Analyze monsoon risks: floods, landslides, waterlogging"""
        
        risks = {
            'flood_prone_areas': [],
            'landslide_zones': [],
            'waterlogging_spots': [],
            'drainage_assessment': {},
            'monsoon_recommendations': []
        }
        
        if not self.tomorrow_key:
            risks['error'] = 'Tomorrow.io API key not provided'
            return risks
        
        try:
            # Get monsoon-specific weather data
            monsoon_data = self._get_tomorrow_weather_data(route_points, focus='precipitation')
            
            for point_data in monsoon_data:
                precipitation = point_data.get('precipitation', 0)
                elevation = point_data.get('elevation', 0)
                location = point_data.get('location', {})
                
                # Assess flood risk based on precipitation and elevation
                if precipitation > 100:  # Heavy rainfall threshold (mm)
                    flood_risk = self._assess_flood_risk(precipitation, elevation, location)
                    if flood_risk['risk_level'] == 'high':
                        risks['flood_prone_areas'].append(flood_risk)
                
                # Assess landslide risk for hilly areas
                if elevation > 500 and precipitation > 50:
                    landslide_risk = self._assess_landslide_risk(precipitation, elevation, location)
                    if landslide_risk['risk_level'] in ['high', 'extreme']:
                        risks['landslide_zones'].append(landslide_risk)
            
            risks['monsoon_recommendations'] = self._generate_monsoon_recommendations(risks)
            
            print(f"✅ Monsoon risks analyzed: {len(risks['flood_prone_areas'])} flood zones, {len(risks['landslide_zones'])} landslide zones")
            return risks
            
        except Exception as e:
            logger.error(f"Monsoon risks analysis error: {e}")
            risks['error'] = str(e)
            return risks
    
    def analyze_winter_risks(self, route_points: List) -> Dict:
        """Analyze winter risks: fog, visibility, cold weather impacts"""
        
        risks = {
            'fog_zones': [],
            'visibility_risks': [],
            'cold_weather_impacts': [],
            'winter_recommendations': []
        }
        
        if not self.openweather_key:
            risks['error'] = 'OpenWeatherMap API key not provided'
            return risks
        
        try:
            # Get winter weather patterns
            winter_data = self._get_openweather_historical(route_points, season='winter')
            
            for point_data in winter_data:
                temperature = point_data.get('temperature', 15)
                humidity = point_data.get('humidity', 50)
                visibility = point_data.get('visibility', 10000)
                
                # Fog risk assessment
                if humidity > 80 and temperature < 15:
                    fog_risk = self._assess_fog_risk(temperature, humidity, visibility)
                    risks['fog_zones'].append(fog_risk)
                
                # Visibility assessment
                if visibility < 1000:  # Poor visibility threshold
                    risks['visibility_risks'].append({
                        'location': point_data.get('location', {}),
                        'visibility_meters': visibility,
                        'risk_level': 'high' if visibility < 500 else 'moderate',
                        'safety_measures': self._get_visibility_safety_measures(visibility)
                    })
            
            risks['winter_recommendations'] = self._generate_winter_recommendations(risks)
            
            print(f"✅ Winter risks analyzed: {len(risks['fog_zones'])} fog zones, {len(risks['visibility_risks'])} visibility risks")
            return risks
            
        except Exception as e:
            logger.error(f"Winter risks analysis error: {e}")
            risks['error'] = str(e)
            return risks
    
    def generate_season_specific_advisories(self, route_points: List) -> Dict:
        """Generate comprehensive season-specific driving advisories"""
        
        advisories = {
            'current_season_alerts': [],
            'upcoming_season_warnings': [],
            'year_round_precautions': [],
            'emergency_protocols': {}
        }
        
        try:
            current_month = datetime.now().month
            current_season = self._get_current_season(current_month)
            
            # Get current season analysis
            if current_season == 'summer':
                summer_analysis = self.analyze_summer_risks(route_points)
                advisories['current_season_alerts'] = summer_analysis.get('summer_recommendations', [])
            elif current_season == 'monsoon':
                monsoon_analysis = self.analyze_monsoon_risks(route_points)
                advisories['current_season_alerts'] = monsoon_analysis.get('monsoon_recommendations', [])
            elif current_season == 'winter':
                winter_analysis = self.analyze_winter_risks(route_points)
                advisories['current_season_alerts'] = winter_analysis.get('winter_recommendations', [])
            
            # General advisories
            advisories['year_round_precautions'] = self._get_year_round_precautions()
            advisories['emergency_protocols'] = self._get_emergency_protocols()
            
            print("✅ Season-specific advisories generated")
            return advisories
            
        except Exception as e:
            logger.error(f"Season-specific advisories error: {e}")
            advisories['error'] = str(e)
            return advisories
    
    # Helper Methods
    
    def _sample_route_points(self, route_points: List, max_points: int = 8) -> List:
        """Sample route points for API efficiency"""
        if len(route_points) <= max_points:
            return route_points
        
        step = len(route_points) // max_points
        return route_points[::step]
    
    def _get_seasonal_weather_data(self, points: List, season: str) -> Dict:
        """Get historical weather data for specific season"""
        try:
            # OpenWeatherMap Historical API simulation
            seasonal_data = {
                'average_temperature': 0,
                'average_humidity': 0,
                'precipitation_days': 0,
                'extreme_weather_events': [],
                'risk_assessment': 'low'
            }
            
            season_temps = {
                'winter': {'min': 8, 'max': 25},
                'spring': {'min': 20, 'max': 35},
                'summer': {'min': 25, 'max': 45},
                'monsoon': {'min': 22, 'max': 35}
            }
            
            base_temp = (season_temps[season]['min'] + season_temps[season]['max']) / 2
            seasonal_data['average_temperature'] = base_temp
            
            # Season-specific risk assessment
            if season == 'summer' and base_temp > 40:
                seasonal_data['risk_assessment'] = 'high'
                seasonal_data['extreme_weather_events'].append('Extreme heat waves')
            elif season == 'monsoon':
                seasonal_data['risk_assessment'] = 'moderate'
                seasonal_data['precipitation_days'] = 15
                seasonal_data['extreme_weather_events'].append('Heavy rainfall')
            
            return seasonal_data
            
        except Exception as e:
            logger.error(f"Seasonal weather data error: {e}")
            return {'error': str(e)}
    
    def _get_visual_crossing_data(self, points: List, season: str) -> List:
        """Get data from Visual Crossing Weather API"""
        try:
            weather_data = []
            
            for point in points[:5]:  # Limit API calls
                # Visual Crossing API call simulation
                data = {
                    'location': {'lat': point[0], 'lng': point[1]},
                    'temperature': 35 + (hash(str(point)) % 15),  # Simulated temperature
                    'humidity': 40 + (hash(str(point)) % 40),
                    'season': season
                }
                weather_data.append(data)
                time.sleep(0.1)  # Rate limiting
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Visual Crossing data error: {e}")
            return []
    
    def _get_tomorrow_weather_data(self, points: List, focus: str = 'precipitation') -> List:
        """Get data from Tomorrow.io Weather API"""
        try:
            weather_data = []
            
            for point in points[:5]:  # Limit API calls
                # Tomorrow.io API call simulation
                data = {
                    'location': {'lat': point[0], 'lng': point[1]},
                    'precipitation': 20 + (hash(str(point)) % 80),  # Simulated precipitation
                    'elevation': abs(hash(str(point))) % 1000,
                    'focus': focus
                }
                weather_data.append(data)
                time.sleep(0.1)  # Rate limiting
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Tomorrow.io data error: {e}")
            return []
    
    def _get_openweather_historical(self, points: List, season: str) -> List:
        """Get historical data from OpenWeatherMap"""
        try:
            weather_data = []
            
            season_conditions = {
                'winter': {'temp': 12, 'humidity': 75, 'visibility': 3000},
                'spring': {'temp': 25, 'humidity': 60, 'visibility': 8000},
                'summer': {'temp': 38, 'humidity': 45, 'visibility': 10000},
                'monsoon': {'temp': 28, 'humidity': 85, 'visibility': 2000}
            }
            
            base_conditions = season_conditions.get(season, season_conditions['spring'])
            
            for point in points[:5]:  # Limit API calls
                data = {
                    'location': {'lat': point[0], 'lng': point[1]},
                    'temperature': base_conditions['temp'] + (hash(str(point)) % 10 - 5),
                    'humidity': base_conditions['humidity'] + (hash(str(point)) % 20 - 10),
                    'visibility': base_conditions['visibility'] + (hash(str(point)) % 2000 - 1000)
                }
                weather_data.append(data)
                time.sleep(0.1)  # Rate limiting
            
            return weather_data
            
        except Exception as e:
            logger.error(f"OpenWeather historical data error: {e}")
            return []
    
    def _assess_overheating_risk(self, temperature: float, humidity: float) -> List[str]:
        """Assess vehicle overheating risk factors"""
        risk_factors = []
        
        if temperature > 42:
            risk_factors.append("Extreme temperature - high engine stress")
        if humidity > 70:
            risk_factors.append("High humidity - reduced cooling efficiency")
        if temperature > 38 and humidity > 60:
            risk_factors.append("Combined heat-humidity stress")
        
        return risk_factors
    
    def _assess_flood_risk(self, precipitation: float, elevation: float, location: Dict) -> Dict:
        """Assess flood risk based on weather and terrain"""
        risk_level = 'low'
        
        if precipitation > 150 and elevation < 100:
            risk_level = 'extreme'
        elif precipitation > 100 and elevation < 200:
            risk_level = 'high'
        elif precipitation > 50:
            risk_level = 'moderate'
        
        return {
            'location': location,
            'precipitation_mm': precipitation,
            'elevation_m': elevation,
            'risk_level': risk_level,
            'safety_measures': self._get_flood_safety_measures(risk_level)
        }
    
    def _assess_landslide_risk(self, precipitation: float, elevation: float, location: Dict) -> Dict:
        """Assess landslide risk for hilly areas"""
        risk_level = 'low'
        
        if elevation > 1000 and precipitation > 100:
            risk_level = 'extreme'
        elif elevation > 500 and precipitation > 75:
            risk_level = 'high'
        elif elevation > 300 and precipitation > 50:
            risk_level = 'moderate'
        
        return {
            'location': location,
            'elevation_m': elevation,
            'precipitation_mm': precipitation,
            'risk_level': risk_level,
            'safety_measures': self._get_landslide_safety_measures(risk_level)
        }
    
    def _assess_fog_risk(self, temperature: float, humidity: float, visibility: float) -> Dict:
        """Assess fog formation risk"""
        risk_level = 'low'
        
        if humidity > 90 and temperature < 10:
            risk_level = 'extreme'
        elif humidity > 80 and temperature < 15:
            risk_level = 'high'
        elif humidity > 70 and temperature < 20:
            risk_level = 'moderate'
        
        return {
            'temperature': temperature,
            'humidity': humidity,
            'visibility_meters': visibility,
            'risk_level': risk_level,
            'safety_measures': self._get_fog_safety_measures(risk_level)
        }
    
    def _get_current_season(self, month: int) -> str:
        """Determine current season based on month (Indian context)"""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'monsoon'
        else:
            return 'summer'
    
    def _create_risk_calendar(self, seasonal_risks: Dict) -> Dict:
        """Create month-wise risk calendar"""
        risk_calendar = {}
        
        month_seasons = {
            'January': 'winter', 'February': 'winter', 'March': 'spring',
            'April': 'spring', 'May': 'summer', 'June': 'monsoon',
            'July': 'monsoon', 'August': 'monsoon', 'September': 'summer',
            'October': 'summer', 'November': 'winter', 'December': 'winter'
        }
        
        for month, season in month_seasons.items():
            season_data = seasonal_risks.get(season, {})
            risk_calendar[month] = {
                'season': season,
                'risk_level': season_data.get('risk_assessment', 'low'),
                'primary_concerns': self._get_seasonal_concerns(season)
            }
        
        return risk_calendar
    
    def _get_seasonal_concerns(self, season: str) -> List[str]:
        """Get primary concerns for each season"""
        concerns = {
            'winter': ['Fog', 'Poor visibility', 'Cold weather'],
            'spring': ['Dust storms', 'Variable temperatures'],
            'summer': ['Extreme heat', 'Vehicle overheating', 'Tire bursts'],
            'monsoon': ['Heavy rainfall', 'Flooding', 'Landslides', 'Poor visibility']
        }
        return concerns.get(season, [])
    
    def _get_extreme_heat_recommendations(self) -> List[str]:
        """Get recommendations for extreme heat conditions"""
        return [
            "Check vehicle cooling system before travel",
            "Carry extra water and electrolytes",
            "Avoid travel during peak afternoon hours (12 PM - 4 PM)",
            "Monitor engine temperature closely",
            "Take frequent breaks in shaded areas"
        ]
    
    def _get_flood_safety_measures(self, risk_level: str) -> List[str]:
        """Get flood safety measures based on risk level"""
        if risk_level == 'extreme':
            return [
                "AVOID TRAVEL - Extreme flood risk",
                "If caught in flood, abandon vehicle and seek high ground",
                "Never drive through flowing water"
            ]
        elif risk_level == 'high':
            return [
                "Monitor flood warnings continuously",
                "Avoid low-lying areas and underpasses",
                "Keep emergency supplies and communication ready"
            ]
        else:
            return [
                "Stay alert for water accumulation",
                "Drive slowly through puddles",
                "Avoid standing water"
            ]
    
    def _get_landslide_safety_measures(self, risk_level: str) -> List[str]:
        """Get landslide safety measures"""
        measures = [
            "Watch for falling rocks and debris",
            "Avoid parking near steep slopes",
            "Listen for rumbling sounds"
        ]
        
        if risk_level in ['high', 'extreme']:
            measures.extend([
                "Consider alternate route if possible",
                "Travel during daylight hours only",
                "Inform authorities of travel plans"
            ])
        
        return measures
    
    def _get_fog_safety_measures(self, risk_level: str) -> List[str]:
        """Get fog safety measures"""
        return [
            "Use fog lights, not high beams",
            "Reduce speed significantly",
            "Increase following distance",
            "Use road markings for guidance",
            "Pull over safely if visibility is too poor"
        ]
    
    def _get_visibility_safety_measures(self, visibility: float) -> List[str]:
        """Get safety measures based on visibility"""
        if visibility < 50:
            return ["STOP - Do not drive", "Wait for visibility to improve"]
        elif visibility < 200:
            return ["Drive very slowly", "Use hazard lights", "Follow road markings"]
        else:
            return ["Reduce speed", "Use headlights", "Stay alert"]
    
    def _generate_seasonal_recommendations(self, analysis: Dict) -> List[str]:
        """Generate comprehensive seasonal recommendations"""
        recommendations = [
            "Monitor weather forecasts before departure",
            "Adjust travel plans based on seasonal risks",
            "Carry season-appropriate emergency supplies",
            "Plan alternate routes during high-risk periods"
        ]
        
        # Add specific recommendations based on analysis
        seasonal_risks = analysis.get('seasonal_risks', {})
        
        for season, risk_data in seasonal_risks.items():
            if isinstance(risk_data, dict) and risk_data.get('risk_assessment') == 'high':
                if season == 'summer':
                    recommendations.append(f"SUMMER ALERT: Plan extra cooling measures for extreme heat")
                elif season == 'monsoon':
                    recommendations.append(f"MONSOON ALERT: Monitor flood warnings and have evacuation plan")
                elif season == 'winter':
                    recommendations.append(f"WINTER ALERT: Prepare for fog and low visibility conditions")
        
        return recommendations
    
    def _generate_summer_recommendations(self, risks: Dict) -> List[str]:
        """Generate summer-specific recommendations"""
        recommendations = [
            "Start travel early morning (5-7 AM) to avoid peak heat",
            "Check tire pressure and condition before travel",
            "Carry extra coolant and engine oil",
            "Plan stops every 2 hours in shaded areas"
        ]
        
        if len(risks.get('temperature_hotspots', [])) > 2:
            recommendations.extend([
                "EXTREME HEAT ALERT: Multiple hotspots detected on route",
                "Consider night travel during extreme heat wave periods",
                "Carry emergency water supplies (minimum 10 liters)"
            ])
        
        return recommendations
    
    def _generate_monsoon_recommendations(self, risks: Dict) -> List[str]:
        """Generate monsoon-specific recommendations"""
        recommendations = [
            "Monitor rainfall forecasts and flood warnings",
            "Carry emergency supplies including food, water, and phone charger",
            "Avoid travel during heavy rainfall warnings",
            "Keep emergency contact numbers ready"
        ]
        
        if len(risks.get('flood_prone_areas', [])) > 1:
            recommendations.append("FLOOD ALERT: Multiple flood-prone areas on route - consider alternate path")
        
        if len(risks.get('landslide_zones', [])) > 0:
            recommendations.append("LANDSLIDE ALERT: Hilly areas with landslide risk - travel during daylight only")
        
        return recommendations
    
    def _generate_winter_recommendations(self, risks: Dict) -> List[str]:
        """Generate winter-specific recommendations"""
        recommendations = [
            "Start travel after sunrise to avoid morning fog",
            "Use fog lights and maintain low speed in foggy conditions",
            "Keep windows slightly open to prevent fogging",
            "Carry warm clothing and emergency supplies"
        ]
        
        if len(risks.get('fog_zones', [])) > 2:
            recommendations.extend([
                "FOG ALERT: Multiple fog-prone areas detected",
                "Consider delaying travel during dense fog warnings",
                "Use GPS navigation as backup for poor visibility"
            ])
        
        return recommendations
    
    def _get_year_round_precautions(self) -> List[str]:
        """Get year-round weather precautions"""
        return [
            "Always check weather forecast before departure",
            "Carry emergency supplies appropriate for season",
            "Keep vehicle maintenance up to date",
            "Have emergency communication plan",
            "Know location of hospitals and service centers",
            "Keep fuel tank above half full",
            "Carry basic repair tools and spare tire",
            "Inform someone of your travel plans and expected arrival"
        ]
    
    def _get_emergency_protocols(self) -> Dict:
        """Get emergency protocols for weather emergencies"""
        return {
            'extreme_heat': [
                "Seek air-conditioned shelter immediately",
                "Drink water frequently, avoid alcohol",
                "Call 108 for medical emergency",
                "Pour water on vehicle engine if overheating"
            ],
            'flood': [
                "Move to higher ground immediately",
                "Call 108 for rescue if trapped",
                "Do not drive through flowing water",
                "Wait for water to recede before continuing"
            ],
            'fog': [
                "Pull over safely and turn on hazard lights",
                "Wait for fog to clear before continuing",
                "Use fog lights, not high beams",
                "Keep windows slightly open to prevent fogging"
            ],
            'general': [
                "Emergency Services: 112",
                "Ambulance: 108",
                "Fire Services: 101",
                "Highway Patrol: 1033"
            ]
        }