# utils/fleet_intelligence.py - FLEET MANAGEMENT & VEHICLE INTELLIGENCE

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class FleetIntelligence:
    """Advanced fleet management and vehicle intelligence for commercial operations"""
    
    def __init__(self, telematics_api_key: str = None, obd_api_key: str = None):
        self.telematics_api_key = telematics_api_key
        self.obd_api_key = obd_api_key
        self.session = requests.Session()
    
    def analyze_vehicle_performance(self, route_data: Dict, vehicle_info: Dict) -> Dict:
        """Comprehensive vehicle performance analysis for the route"""
        
        performance_analysis = {
            'fuel_efficiency_analysis': {},
            'engine_performance': {},
            'maintenance_recommendations': [],
            'route_optimization_suggestions': [],
            'cost_analysis': {},
            'environmental_impact': {}
        }
        
        try:
            vehicle_type = vehicle_info.get('type', 'heavy_goods_vehicle')
            vehicle_weight = vehicle_info.get('weight', 18000)
            route_distance = self._parse_distance_to_km(route_data.get('distance', '0 km'))
            
            # Fuel efficiency analysis
            performance_analysis['fuel_efficiency_analysis'] = self._analyze_fuel_efficiency(
                route_data, vehicle_type, vehicle_weight, route_distance
            )
            
            # Engine performance assessment
            performance_analysis['engine_performance'] = self._assess_engine_performance(
                route_data, vehicle_info
            )
            
            # Maintenance recommendations
            performance_analysis['maintenance_recommendations'] = self._generate_maintenance_recommendations(
                route_data, vehicle_info, route_distance
            )
            
            # Route optimization for vehicle type
            performance_analysis['route_optimization_suggestions'] = self._suggest_route_optimizations(
                route_data, vehicle_info
            )
            
            # Cost analysis
            performance_analysis['cost_analysis'] = self._calculate_trip_costs(
                route_distance, vehicle_type, performance_analysis['fuel_efficiency_analysis']
            )
            
            # Environmental impact
            performance_analysis['environmental_impact'] = self._calculate_environmental_impact(
                route_distance, vehicle_type, performance_analysis['fuel_efficiency_analysis']
            )
            
            print(f"✅ Vehicle performance analysis completed for {vehicle_type}")
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Vehicle performance analysis error: {e}")
            performance_analysis['error'] = str(e)
            return performance_analysis
    
    def monitor_driver_behavior(self, route_data: Dict) -> Dict:
        """Monitor and analyze driver behavior patterns"""
        
        behavior_analysis = {
            'driving_patterns': {},
            'safety_scores': {},
            'efficiency_metrics': {},
            'risk_factors': [],
            'recommendations': [],
            'training_suggestions': []
        }
        
        try:
            # Analyze driving patterns from route data
            sharp_turns = route_data.get('sharp_turns', [])
            route_points = route_data.get('route_points', [])
            
            # Driving pattern analysis
            behavior_analysis['driving_patterns'] = self._analyze_driving_patterns(
                route_data, sharp_turns
            )
            
            # Safety scoring
            behavior_analysis['safety_scores'] = self._calculate_safety_scores(
                sharp_turns, route_data
            )
            
            # Efficiency metrics
            behavior_analysis['efficiency_metrics'] = self._calculate_efficiency_metrics(
                route_data
            )
            
            # Risk factor identification
            behavior_analysis['risk_factors'] = self._identify_risk_factors(
                behavior_analysis['driving_patterns'], sharp_turns
            )
            
            # Generate recommendations
            behavior_analysis['recommendations'] = self._generate_driver_recommendations(
                behavior_analysis['safety_scores'], behavior_analysis['risk_factors']
            )
            
            # Training suggestions
            behavior_analysis['training_suggestions'] = self._suggest_driver_training(
                behavior_analysis['risk_factors']
            )
            
            print("✅ Driver behavior analysis completed")
            return behavior_analysis
            
        except Exception as e:
            logger.error(f"Driver behavior analysis error: {e}")
            behavior_analysis['error'] = str(e)
            return behavior_analysis
    
    def optimize_fleet_operations(self, route_data: Dict, fleet_info: Dict) -> Dict:
        """Optimize fleet operations for multiple vehicles"""
        
        fleet_optimization = {
            'vehicle_allocation': {},
            'route_efficiency': {},
            'maintenance_scheduling': {},
            'cost_optimization': {},
            'performance_benchmarks': {},
            'fleet_recommendations': []
        }
        
        try:
            fleet_size = fleet_info.get('fleet_size', 1)
            vehicle_types = fleet_info.get('vehicle_types', ['heavy_goods_vehicle'])
            
            # Vehicle allocation optimization
            fleet_optimization['vehicle_allocation'] = self._optimize_vehicle_allocation(
                route_data, fleet_info
            )
            
            # Route efficiency analysis
            fleet_optimization['route_efficiency'] = self._analyze_fleet_route_efficiency(
                route_data, fleet_info
            )
            
            # Maintenance scheduling
            fleet_optimization['maintenance_scheduling'] = self._optimize_maintenance_scheduling(
                fleet_info
            )
            
            # Cost optimization
            fleet_optimization['cost_optimization'] = self._optimize_fleet_costs(
                route_data, fleet_info
            )
            
            # Performance benchmarks
            fleet_optimization['performance_benchmarks'] = self._establish_performance_benchmarks(
                fleet_info
            )
            
            # Fleet recommendations
            fleet_optimization['fleet_recommendations'] = self._generate_fleet_recommendations(
                fleet_optimization
            )
            
            print(f"✅ Fleet optimization completed for {fleet_size} vehicles")
            return fleet_optimization
            
        except Exception as e:
            logger.error(f"Fleet optimization error: {e}")
            fleet_optimization['error'] = str(e)
            return fleet_optimization
    
    def track_compliance_metrics(self, route_data: Dict, vehicle_info: Dict) -> Dict:
        """Track regulatory and safety compliance metrics"""
        
        compliance_tracking = {
            'regulatory_compliance': {},
            'safety_compliance': {},
            'environmental_compliance': {},
            'documentation_status': {},
            'compliance_score': 0,
            'action_items': []
        }
        
        try:
            vehicle_type = vehicle_info.get('type', 'heavy_goods_vehicle')
            vehicle_weight = vehicle_info.get('weight', 18000)
            
            # Regulatory compliance (CMVR, AIS-140, etc.)
            compliance_tracking['regulatory_compliance'] = self._check_regulatory_compliance(
                vehicle_info, route_data
            )
            
            # Safety compliance
            compliance_tracking['safety_compliance'] = self._check_safety_compliance(
                route_data, vehicle_info
            )
            
            # Environmental compliance
            compliance_tracking['environmental_compliance'] = self._check_environmental_compliance(
                vehicle_info, route_data
            )
            
            # Documentation status
            compliance_tracking['documentation_status'] = self._check_documentation_status(
                vehicle_info
            )
            
            # Calculate overall compliance score
            compliance_tracking['compliance_score'] = self._calculate_compliance_score(
                compliance_tracking
            )
            
            # Generate action items
            compliance_tracking['action_items'] = self._generate_compliance_action_items(
                compliance_tracking
            )
            
            print(f"✅ Compliance tracking completed - Score: {compliance_tracking['compliance_score']}/100")
            return compliance_tracking
            
        except Exception as e:
            logger.error(f"Compliance tracking error: {e}")
            compliance_tracking['error'] = str(e)
            return compliance_tracking
    
    # Helper Methods
    
    def _parse_distance_to_km(self, distance_str: str) -> float:
        """Parse distance string to kilometers"""
        try:
            if not distance_str:
                return 0.0
            distance_str = distance_str.lower().replace('km', '').replace(',', '').strip()
            return float(distance_str)
        except:
            return 0.0
    
    def _analyze_fuel_efficiency(self, route_data: Dict, vehicle_type: str, vehicle_weight: int, distance_km: float) -> Dict:
        """Analyze fuel efficiency for the specific route and vehicle"""
        
        # Base fuel consumption rates (liters per 100km)
        base_consumption_rates = {
            'heavy_goods_vehicle': 25.0,
            'medium_goods_vehicle': 18.0,
            'light_motor_vehicle': 12.0,
            'bus': 22.0
        }
        
        base_rate = base_consumption_rates.get(vehicle_type, 25.0)
        
        # Adjust for vehicle weight
        if vehicle_weight > 20000:
            weight_factor = 1.2
        elif vehicle_weight > 15000:
            weight_factor = 1.1
        elif vehicle_weight > 10000:
            weight_factor = 1.0
        else:
            weight_factor = 0.9
        
        # Adjust for route characteristics
        sharp_turns = len(route_data.get('sharp_turns', []))
        elevation_data = route_data.get('elevation', [])
        
        # Route difficulty factor
        route_factor = 1.0
        if sharp_turns > 20:
            route_factor += 0.15  # 15% increase for many turns
        elif sharp_turns > 10:
            route_factor += 0.10  # 10% increase for moderate turns
        
        if elevation_data:
            # Estimate elevation impact
            route_factor += 0.05  # 5% increase for elevation changes
        
        # Calculate adjusted consumption
        adjusted_rate = base_rate * weight_factor * route_factor
        total_fuel_needed = (adjusted_rate / 100) * distance_km
        
        return {
            'base_consumption_rate': base_rate,
            'weight_adjustment_factor': weight_factor,
            'route_difficulty_factor': route_factor,
            'adjusted_consumption_rate': adjusted_rate,
            'estimated_fuel_consumption': total_fuel_needed,
            'fuel_efficiency_rating': self._rate_fuel_efficiency(adjusted_rate),
            'efficiency_recommendations': self._get_efficiency_recommendations(route_factor, sharp_turns)
        }
    
    def _rate_fuel_efficiency(self, consumption_rate: float) -> str:
        """Rate fuel efficiency based on consumption rate"""
        if consumption_rate < 15:
            return 'excellent'
        elif consumption_rate < 20:
            return 'good'
        elif consumption_rate < 25:
            return 'average'
        elif consumption_rate < 30:
            return 'poor'
        else:
            return 'very_poor'
    
    def _get_efficiency_recommendations(self, route_factor: float, sharp_turns: int) -> List[str]:
        """Get fuel efficiency recommendations"""
        recommendations = []
        
        if route_factor > 1.1:
            recommendations.append("Route has challenging conditions - use cruise control on straight sections")
        
        if sharp_turns > 15:
            recommendations.append("Many sharp turns detected - practice smooth acceleration and braking")
        
        recommendations.extend([
            "Maintain steady speeds for optimal fuel efficiency",
            "Plan route to avoid heavy traffic and stop-and-go conditions",
            "Regular vehicle maintenance improves fuel efficiency by 10-15%",
            "Proper tire pressure can improve efficiency by 3-5%"
        ])
        
        return recommendations
    
    def _assess_engine_performance(self, route_data: Dict, vehicle_info: Dict) -> Dict:
        """Assess engine performance requirements for the route"""
        
        route_distance = self._parse_distance_to_km(route_data.get('distance', '0 km'))
        sharp_turns = len(route_data.get('sharp_turns', []))
        elevation_data = route_data.get('elevation', [])
        
        # Estimate engine stress factors
        stress_factors = {
            'distance_stress': min(1.0, route_distance / 1000),  # Normalize to 1000km max
            'turning_stress': min(1.0, sharp_turns / 50),  # Normalize to 50 turns max
            'elevation_stress': 0.5 if elevation_data else 0.2,  # Estimate based on elevation data
            'overall_stress_level': 'moderate'
        }
        
        overall_stress = (stress_factors['distance_stress'] + 
                         stress_factors['turning_stress'] + 
                         stress_factors['elevation_stress']) / 3
        
        if overall_stress > 0.7:
            stress_factors['overall_stress_level'] = 'high'
        elif overall_stress > 0.4:
            stress_factors['overall_stress_level'] = 'moderate'
        else:
            stress_factors['overall_stress_level'] = 'low'
        
        return {
            'stress_factors': stress_factors,
            'engine_load_estimate': f"{overall_stress * 100:.0f}%",
            'cooling_requirements': 'enhanced' if overall_stress > 0.6 else 'standard',
            'maintenance_urgency': self._assess_maintenance_urgency(overall_stress),
            'performance_recommendations': self._get_engine_recommendations(overall_stress)
        }
    
    def _assess_maintenance_urgency(self, stress_level: float) -> str:
        """Assess maintenance urgency based on stress level"""
        if stress_level > 0.8:
            return 'immediate'
        elif stress_level > 0.6:
            return 'within_week'
        elif stress_level > 0.4:
            return 'within_month'
        else:
            return 'routine'
    
    def _get_engine_recommendations(self, stress_level: float) -> List[str]:
        """Get engine performance recommendations"""
        recommendations = []
        
        if stress_level > 0.7:
            recommendations.extend([
                "HIGH STRESS ROUTE: Check engine oil level before departure",
                "Monitor engine temperature closely during travel",
                "Consider shorter driving intervals with cooling breaks"
            ])
        elif stress_level > 0.4:
            recommendations.extend([
                "MODERATE STRESS: Ensure cooling system is functioning properly",
                "Check fluid levels before long journey"
            ])
        
        recommendations.extend([
            "Use appropriate engine oil grade for operating conditions",
            "Schedule post-trip inspection for high-stress routes",
            "Monitor unusual sounds or vibrations during travel"
        ])
        
        return recommendations
    
    def _generate_maintenance_recommendations(self, route_data: Dict, vehicle_info: Dict, distance_km: float) -> List[str]:
        """Generate comprehensive maintenance recommendations"""
        
        recommendations = []
        vehicle_type = vehicle_info.get('type', 'heavy_goods_vehicle')
        
        # Distance-based recommendations
        if distance_km > 1000:
            recommendations.extend([
                "LONG DISTANCE TRIP: Comprehensive pre-trip inspection required",
                "Check tire condition and tread depth thoroughly",
                "Verify brake system functionality",
                "Ensure spare parts and tools are available"
            ])
        elif distance_km > 500:
            recommendations.extend([
                "MEDIUM DISTANCE: Standard pre-trip inspection",
                "Check fluid levels and tire pressure"
            ])
        
        # Vehicle type specific recommendations
        if vehicle_type == 'heavy_goods_vehicle':
            recommendations.extend([
                "Heavy vehicle specific: Check air brake system",
                "Verify suspension system for heavy loads",
                "Inspect trailer coupling and safety chains"
            ])
        
        # Route-specific recommendations
        sharp_turns = len(route_data.get('sharp_turns', []))
        if sharp_turns > 20:
            recommendations.append("Many turns detected: Pay special attention to steering components")
        
        # General recommendations
        recommendations.extend([
            "Check all lights and electrical systems",
            "Verify emergency equipment is present and functional",
            "Document all maintenance checks for compliance"
        ])
        
        return recommendations
    
    def _suggest_route_optimizations(self, route_data: Dict, vehicle_info: Dict) -> List[str]:
        """Suggest route optimizations for specific vehicle type"""
        
        suggestions = []
        vehicle_type = vehicle_info.get('type', 'heavy_goods_vehicle')
        sharp_turns = len(route_data.get('sharp_turns', []))
        
        # Heavy vehicle specific optimizations
        if vehicle_type in ['heavy_goods_vehicle', 'bus']:
            if sharp_turns > 15:
                suggestions.append("Consider alternate route with fewer sharp turns for heavy vehicle")
            
            suggestions.extend([
                "Plan fuel stops at truck-friendly stations",
                "Identify weigh stations and inspection points",
                "Plan rest stops every 4 hours for driver fatigue management"
            ])
        
        # General optimizations
        suggestions.extend([
            "Avoid peak traffic hours for better fuel efficiency",
            "Plan overnight stops for long journeys",
            "Consider toll road benefits vs. cost for time savings"
        ])
        
        return suggestions
    
    def _calculate_trip_costs(self, distance_km: float, vehicle_type: str, fuel_analysis: Dict) -> Dict:
        """Calculate comprehensive trip costs"""
        
        # Fuel cost calculation
        fuel_price_per_liter = 95.0  # Average petrol/diesel price in Rs
        fuel_consumption = fuel_analysis.get('estimated_fuel_consumption', 0)
        fuel_cost = fuel_consumption * fuel_price_per_liter
        
        # Other cost factors
        driver_cost_per_km = {
            'heavy_goods_vehicle': 2.5,
            'medium_goods_vehicle': 2.0,
            'light_motor_vehicle': 1.5,
            'bus': 2.2
        }
        
        driver_cost = distance_km * driver_cost_per_km.get(vehicle_type, 2.0)
        
        # Maintenance cost (estimated)
        maintenance_cost_per_km = {
            'heavy_goods_vehicle': 1.5,
            'medium_goods_vehicle': 1.0,
            'light_motor_vehicle': 0.8,
            'bus': 1.3
        }
        
        maintenance_cost = distance_km * maintenance_cost_per_km.get(vehicle_type, 1.0)
        
        # Toll estimation (if applicable)
        estimated_toll_cost = distance_km * 0.5 if distance_km > 100 else 0  # Rs 0.5 per km for highways
        
        total_cost = fuel_cost + driver_cost + maintenance_cost + estimated_toll_cost
        
        return {
            'fuel_cost': fuel_cost,
            'driver_cost': driver_cost,
            'maintenance_cost': maintenance_cost,
            'toll_cost': estimated_toll_cost,
            'total_trip_cost': total_cost,
            'cost_per_km': total_cost / distance_km if distance_km > 0 else 0,
            'cost_breakdown_percentage': {
                'fuel': (fuel_cost / total_cost * 100) if total_cost > 0 else 0,
                'driver': (driver_cost / total_cost * 100) if total_cost > 0 else 0,
                'maintenance': (maintenance_cost / total_cost * 100) if total_cost > 0 else 0,
                'toll': (estimated_toll_cost / total_cost * 100) if total_cost > 0 else 0
            }
        }
    
    def _calculate_environmental_impact(self, distance_km: float, vehicle_type: str, fuel_analysis: Dict) -> Dict:
        """Calculate environmental impact of the trip"""
        
        # CO2 emission factors (kg CO2 per liter of fuel)
        co2_per_liter = 2.68  # Diesel/petrol average
        
        fuel_consumption = fuel_analysis.get('estimated_fuel_consumption', 0)
        total_co2_emissions = fuel_consumption * co2_per_liter
        
        # Other pollutants (estimated)
        nox_emissions = fuel_consumption * 0.015  # kg NOx per liter
        pm_emissions = fuel_consumption * 0.002   # kg PM per liter
        
        # Carbon offset calculation
        trees_needed_for_offset = total_co2_emissions / 22  # 1 tree absorbs ~22kg CO2/year
        
        return {
            'co2_emissions_kg': total_co2_emissions,
            'co2_emissions_per_km': total_co2_emissions / distance_km if distance_km > 0 else 0,
            'nox_emissions_kg': nox_emissions,
            'pm_emissions_kg': pm_emissions,
            'trees_for_offset': trees_needed_for_offset,
            'environmental_rating': self._rate_environmental_impact(total_co2_emissions),
            'eco_recommendations': self._get_eco_recommendations(fuel_analysis)
        }
    
    def _rate_environmental_impact(self, co2_emissions: float) -> str:
        """Rate environmental impact based on CO2 emissions"""
        if co2_emissions < 50:
            return 'low_impact'
        elif co2_emissions < 150:
            return 'moderate_impact'
        elif co2_emissions < 300:
            return 'high_impact'
        else:
            return 'very_high_impact'
    
    def _get_eco_recommendations(self, fuel_analysis: Dict) -> List[str]:
        """Get environmental recommendations"""
        recommendations = [
            "Consider eco-driving techniques to reduce fuel consumption",
            "Plan efficient routes to minimize total distance traveled",
            "Regular vehicle maintenance reduces emissions by 10-15%"
        ]
        
        efficiency_rating = fuel_analysis.get('fuel_efficiency_rating', 'average')
        if efficiency_rating in ['poor', 'very_poor']:
            recommendations.extend([
                "Vehicle shows poor fuel efficiency - consider maintenance or upgrade",
                "Implement driver training for eco-friendly driving techniques"
            ])
        
        return recommendations
    
    def _analyze_driving_patterns(self, route_data: Dict, sharp_turns: List) -> Dict:
        """Analyze driving patterns from route data"""
        
        # Simulate driving pattern analysis
        # In production, this would use real telematics data
        
        route_distance = self._parse_distance_to_km(route_data.get('distance', '0 km'))
        duration_str = route_data.get('duration', '2 hours')
        
        # Extract hours from duration (simplified)
        try:
            duration_hours = float(duration_str.split()[0])
        except:
            duration_hours = route_distance / 60  # Assume 60 km/h average
        
        average_speed = route_distance / duration_hours if duration_hours > 0 else 0
        
        patterns = {
            'average_speed': average_speed,
            'speed_consistency': 'good' if 40 <= average_speed <= 80 else 'variable',
            'turning_behavior': self._analyze_turning_behavior(sharp_turns),
            'route_efficiency': self._calculate_route_efficiency(route_distance, sharp_turns),
            'driving_style': self._classify_driving_style(average_speed, sharp_turns)
        }
        
        return patterns
    
    def _analyze_turning_behavior(self, sharp_turns: List) -> Dict:
        """Analyze turning behavior patterns"""
        if not sharp_turns:
            return {'assessment': 'no_significant_turns', 'risk_level': 'low'}
        
        extreme_turns = len([t for t in sharp_turns if t.get('angle', 0) > 80])
        sharp_danger_turns = len([t for t in sharp_turns if 70 <= t.get('angle', 0) <= 80])
        
        total_challenging_turns = extreme_turns + sharp_danger_turns
        
        if total_challenging_turns > 10:
            risk_level = 'high'
            assessment = 'many_challenging_turns'
        elif total_challenging_turns > 5:
            risk_level = 'moderate'
            assessment = 'some_challenging_turns'
        else:
            risk_level = 'low'
            assessment = 'manageable_turns'
        
        return {
            'total_sharp_turns': len(sharp_turns),
            'extreme_turns': extreme_turns,
            'sharp_danger_turns': sharp_danger_turns,
            'assessment': assessment,
            'risk_level': risk_level
        }
    
    def _calculate_route_efficiency(self, distance_km: float, sharp_turns: List) -> float:
        """Calculate route efficiency score"""
        # Base efficiency score
        efficiency = 100
        
        # Deduct for excessive turns
        turn_penalty = len(sharp_turns) * 2  # 2 points per sharp turn
        efficiency -= min(30, turn_penalty)  # Max 30 point deduction
        
        # Adjust for distance (longer routes may be less efficient)
        if distance_km > 1000:
            efficiency -= 10
        elif distance_km < 50:
            efficiency -= 5  # Very short routes may have inefficiencies
        
        return max(50, efficiency)  # Minimum 50% efficiency
    
    def _classify_driving_style(self, average_speed: float, sharp_turns: List) -> str:
        """Classify driving style based on patterns"""
        if average_speed > 80:
            return 'aggressive'
        elif average_speed < 40:
            return 'cautious'
        elif len(sharp_turns) > 20:
            return 'challenging_route'
        else:
            return 'normal'
    
    def _calculate_safety_scores(self, sharp_turns: List, route_data: Dict) -> Dict:
        """Calculate comprehensive safety scores"""
        
        # Base safety score
        base_score = 100
        
        # Deduct for sharp turns
        extreme_turns = len([t for t in sharp_turns if t.get('angle', 0) > 80])
        sharp_danger_turns = len([t for t in sharp_turns if 70 <= t.get('angle', 0) <= 80])
        
        base_score -= extreme_turns * 15  # 15 points per extreme turn
        base_score -= sharp_danger_turns * 10  # 10 points per sharp danger turn
        
        # Network coverage impact
        network_data = route_data.get('network_coverage', {})
        dead_zones = len(network_data.get('dead_zones', []))
        base_score -= dead_zones * 5  # 5 points per dead zone
        
        safety_score = max(0, base_score)
        
        return {
            'overall_safety_score': safety_score,
            'turn_safety_score': max(0, 100 - (extreme_turns * 20 + sharp_danger_turns * 15)),
            'communication_safety_score': max(0, 100 - dead_zones * 10),
            'safety_rating': self._rate_safety_score(safety_score),
            'critical_safety_factors': self._identify_critical_safety_factors(extreme_turns, dead_zones)
        }
    
    def _rate_safety_score(self, score: int) -> str:
        """Rate safety score"""
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'fair'
        elif score >= 40:
            return 'poor'
        else:
            return 'dangerous'
    
    def _identify_critical_safety_factors(self, extreme_turns: int, dead_zones: int) -> List[str]:
        """Identify critical safety factors"""
        factors = []
        
        if extreme_turns > 5:
            factors.append(f"CRITICAL: {extreme_turns} extreme blind spot turns")
        if dead_zones > 3:
            factors.append(f"CRITICAL: {dead_zones} communication dead zones")
        
        return factors
    
    def _calculate_efficiency_metrics(self, route_data: Dict) -> Dict:
        """Calculate efficiency metrics"""
        
        route_distance = self._parse_distance_to_km(route_data.get('distance', '0 km'))
        sharp_turns = len(route_data.get('sharp_turns', []))
        
        # Efficiency calculations
        metrics = {
            'route_directness': min(100, (1000 / max(route_distance, 1)) * 100),  # Inverse relationship
            'turn_efficiency': max(0, 100 - sharp_turns * 2),  # 2% penalty per turn
            'overall_efficiency': 0,
            'efficiency_rating': 'average'
        }
        
        # Calculate overall efficiency
        metrics['overall_efficiency'] = (metrics['route_directness'] + metrics['turn_efficiency']) / 2
        
        # Rate efficiency
        if metrics['overall_efficiency'] >= 80:
            metrics['efficiency_rating'] = 'excellent'
        elif metrics['overall_efficiency'] >= 65:
            metrics['efficiency_rating'] = 'good'
        elif metrics['overall_efficiency'] >= 50:
            metrics['efficiency_rating'] = 'average'
        else:
            metrics['efficiency_rating'] = 'poor'
        
        return metrics
    
    def _identify_risk_factors(self, driving_patterns: Dict, sharp_turns: List) -> List[str]:
        """Identify risk factors from driving patterns"""
        
        risk_factors = []
        
        # Speed-related risks
        avg_speed = driving_patterns.get('average_speed', 0)
        if avg_speed > 80:
            risk_factors.append("High average speed increases accident risk")
        elif avg_speed < 30:
            risk_factors.append("Very low average speed may indicate poor route planning")
        
        # Turn-related risks
        turning_behavior = driving_patterns.get('turning_behavior', {})
        if turning_behavior.get('risk_level') == 'high':
            risk_factors.append("High number of challenging turns requires extra caution")
        
        # Route efficiency risks
        route_efficiency = driving_patterns.get('route_efficiency', 0)
        if route_efficiency < 60:
            risk_factors.append("Poor route efficiency may lead to driver fatigue")
        
        # Driving style risks
        driving_style = driving_patterns.get('driving_style', 'normal')
        if driving_style == 'aggressive':
            risk_factors.append("Aggressive driving pattern detected")
        
        return risk_factors
    
    def _generate_driver_recommendations(self, safety_scores: Dict, risk_factors: List) -> List[str]:
        """Generate driver recommendations based on analysis"""
        
        recommendations = []
        
        safety_score = safety_scores.get('overall_safety_score', 100)
        
        if safety_score < 60:
            recommendations.extend([
                "CRITICAL: Route has significant safety challenges",
                "Reduce speed by 20% in challenging areas",
                "Take breaks every 2 hours to maintain alertness"
            ])
        elif safety_score < 80:
            recommendations.extend([
                "Route requires extra caution and attention",
                "Maintain safe following distances"
            ])
        
        # Risk-specific recommendations
        if "High average speed" in str(risk_factors):
            recommendations.append("Practice speed management techniques")
        
        if "challenging turns" in str(risk_factors):
            recommendations.append("Use proper turning techniques for sharp corners")
        
        # General recommendations
        recommendations.extend([
            "Follow defensive driving principles",
            "Monitor vehicle condition during travel",
            "Report any safety concerns immediately"
        ])
        
        return recommendations
    
    def _suggest_driver_training(self, risk_factors: List) -> List[str]:
        """Suggest driver training based on identified risks"""
        
        training_suggestions = []
        
        # Risk-based training suggestions
        if any("speed" in factor.lower() for factor in risk_factors):
            training_suggestions.append("Speed management and defensive driving course")
        
        if any("turn" in factor.lower() for factor in risk_factors):
            training_suggestions.append("Advanced vehicle handling and cornering techniques")
        
        if any("efficiency" in factor.lower() for factor in risk_factors):
            training_suggestions.append("Route planning and fuel-efficient driving techniques")
        
        # General training recommendations
        training_suggestions.extend([
            "Regular safety refresher training",
            "First aid and emergency response training",
            "Vehicle maintenance awareness training"
        ])
        
        return training_suggestions
    
    # Fleet Optimization Methods
    
    def _optimize_vehicle_allocation(self, route_data: Dict, fleet_info: Dict) -> Dict:
        """Optimize vehicle allocation for fleet operations"""
        
        route_distance = self._parse_distance_to_km(route_data.get('distance', '0 km'))
        sharp_turns = len(route_data.get('sharp_turns', []))
        vehicle_types = fleet_info.get('vehicle_types', ['heavy_goods_vehicle'])
        
        allocation = {
            'recommended_vehicle_type': '',
            'alternative_vehicles': [],
            'load_optimization': {},
            'allocation_reasoning': []
        }
        
        # Determine best vehicle type for route
        if route_distance > 1000:
            if sharp_turns < 10:
                allocation['recommended_vehicle_type'] = 'heavy_goods_vehicle'
                allocation['allocation_reasoning'].append("Long distance with few turns - suitable for heavy vehicle")
            else:
                allocation['recommended_vehicle_type'] = 'medium_goods_vehicle'
                allocation['allocation_reasoning'].append("Long distance with many turns - medium vehicle recommended")
        elif route_distance > 200:
            allocation['recommended_vehicle_type'] = 'medium_goods_vehicle'
            allocation['allocation_reasoning'].append("Medium distance route - optimal for medium vehicle")
        else:
            allocation['recommended_vehicle_type'] = 'light_motor_vehicle'
            allocation['allocation_reasoning'].append("Short distance route - light vehicle sufficient")
        
        # Load optimization suggestions
        allocation['load_optimization'] = {
            'max_recommended_load': '80% of vehicle capacity',
            'load_distribution': 'balanced_center_of_gravity',
            'loading_sequence': 'heavy_items_first'
        }
        
        return allocation
    
    def _analyze_fleet_route_efficiency(self, route_data: Dict, fleet_info: Dict) -> Dict:
        """Analyze route efficiency for fleet operations"""
        
        fleet_size = fleet_info.get('fleet_size', 1)
        route_distance = self._parse_distance_to_km(route_data.get('distance', '0 km'))
        
        efficiency = {
            'single_vehicle_efficiency': 100,
            'multi_vehicle_potential': False,
            'convoy_recommendations': [],
            'route_splitting_potential': False
        }
        
        # Multi-vehicle analysis
        if fleet_size > 1 and route_distance > 500:
            efficiency['multi_vehicle_potential'] = True
            efficiency['convoy_recommendations'] = [
                "Consider convoy travel for long distances",
                "Coordinate departure times for fuel efficiency",
                "Plan synchronized rest stops"
            ]
        
        if route_distance > 1500 and fleet_size > 2:
            efficiency['route_splitting_potential'] = True
            efficiency['convoy_recommendations'].append(
                "Consider splitting route into segments with different vehicles"
            )
        
        return efficiency
    
    def _optimize_maintenance_scheduling(self, fleet_info: Dict) -> Dict:
        """Optimize maintenance scheduling for fleet"""
        
        fleet_size = fleet_info.get('fleet_size', 1)
        
        scheduling = {
            'maintenance_intervals': {},
            'preventive_schedule': [],
            'resource_optimization': {}
        }
        
        # Standard maintenance intervals
        scheduling['maintenance_intervals'] = {
            'daily_checks': 'Before each trip',
            'weekly_inspection': 'Every 7 days or 1000 km',
            'monthly_service': 'Every 30 days or 5000 km',
            'quarterly_overhaul': 'Every 90 days or 15000 km'
        }
        
        # Fleet-specific scheduling
        if fleet_size > 3:
            scheduling['preventive_schedule'] = [
                "Stagger maintenance schedules to ensure vehicle availability",
                "Implement predictive maintenance using telematics data",
                "Maintain 20% fleet capacity for emergency replacements"
            ]
        
        return scheduling
    
    def _optimize_fleet_costs(self, route_data: Dict, fleet_info: Dict) -> Dict:
        """Optimize costs for fleet operations"""
        
        fleet_size = fleet_info.get('fleet_size', 1)
        route_distance = self._parse_distance_to_km(route_data.get('distance', '0 km'))
        
        cost_optimization = {
            'fuel_optimization': [],
            'maintenance_optimization': [],
            'operational_optimization': [],
            'potential_savings': {}
        }
        
        # Fuel optimization strategies
        cost_optimization['fuel_optimization'] = [
            "Bulk fuel purchasing for fleet discount",
            "Route optimization to minimize total fleet mileage",
            "Driver training for fuel-efficient driving techniques"
        ]
        
        # Maintenance optimization
        cost_optimization['maintenance_optimization'] = [
            "Group maintenance scheduling for bulk service discounts",
            "Preventive maintenance to avoid costly breakdowns",
            "Fleet-wide parts standardization"
        ]
        
        # Operational optimization
        cost_optimization['operational_optimization'] = [
            "Load consolidation to maximize vehicle utilization",
            "Optimal departure timing to avoid peak traffic",
            "Route sharing between multiple vehicles"
        ]
        
        # Calculate potential savings
        if fleet_size > 3:
            cost_optimization['potential_savings'] = {
                'fuel_savings': '10-15% through bulk purchasing and optimization',
                'maintenance_savings': '15-20% through preventive scheduling',
                'operational_savings': '5-10% through route and load optimization'
            }
        
        return cost_optimization
    
    def _establish_performance_benchmarks(self, fleet_info: Dict) -> Dict:
        """Establish performance benchmarks for fleet"""
        
        fleet_size = fleet_info.get('fleet_size', 1)
        vehicle_types = fleet_info.get('vehicle_types', ['heavy_goods_vehicle'])
        
        benchmarks = {
            'fuel_efficiency_targets': {},
            'safety_targets': {},
            'maintenance_targets': {},
            'operational_targets': {}
        }
        
        # Fuel efficiency targets by vehicle type
        efficiency_targets = {
            'heavy_goods_vehicle': '22-25 L/100km',
            'medium_goods_vehicle': '15-18 L/100km',
            'light_motor_vehicle': '10-12 L/100km',
            'bus': '20-22 L/100km'
        }
        
        for vehicle_type in vehicle_types:
            benchmarks['fuel_efficiency_targets'][vehicle_type] = efficiency_targets.get(
                vehicle_type, '20-25 L/100km'
            )
        
        # Safety targets
        benchmarks['safety_targets'] = {
            'accident_rate': '< 1 per 100,000 km',
            'safety_score': '> 85/100',
            'compliance_rate': '100%'
        }
        
        # Maintenance targets
        benchmarks['maintenance_targets'] = {
            'preventive_maintenance_rate': '> 90%',
            'unplanned_downtime': '< 5%',
            'maintenance_cost_per_km': '< Rs. 1.50'
        }
        
        # Operational targets
        benchmarks['operational_targets'] = {
            'on_time_delivery': '> 95%',
            'vehicle_utilization': '> 80%',
            'route_efficiency': '> 85%'
        }
        
        return benchmarks
    
    def _generate_fleet_recommendations(self, fleet_optimization: Dict) -> List[str]:
        """Generate comprehensive fleet recommendations"""
        
        recommendations = []
        
        # Vehicle allocation recommendations
        vehicle_allocation = fleet_optimization.get('vehicle_allocation', {})
        recommended_type = vehicle_allocation.get('recommended_vehicle_type', '')
        if recommended_type:
            recommendations.append(f"Optimal vehicle type for this route: {recommended_type}")
        
        # Route efficiency recommendations
        route_efficiency = fleet_optimization.get('route_efficiency', {})
        if route_efficiency.get('multi_vehicle_potential', False):
            recommendations.append("Consider multi-vehicle coordination for this route")
        
        # Cost optimization recommendations
        cost_optimization = fleet_optimization.get('cost_optimization', {})
        if cost_optimization.get('potential_savings'):
            recommendations.append("Implement fleet-wide cost optimization strategies")
        
        # General fleet recommendations
        recommendations.extend([
            "Implement telematics systems for real-time fleet monitoring",
            "Establish driver performance monitoring and feedback systems",
            "Create standardized operating procedures for all fleet operations",
            "Regular fleet performance reviews and optimization assessments"
        ])
        
        return recommendations
    
    # Compliance Methods
    
    def _check_regulatory_compliance(self, vehicle_info: Dict, route_data: Dict) -> Dict:
        """Check regulatory compliance status"""
        
        vehicle_type = vehicle_info.get('type', 'heavy_goods_vehicle')
        vehicle_weight = vehicle_info.get('weight', 18000)
        
        compliance = {
            'cmvr_compliance': 'required' if vehicle_weight > 3500 else 'not_required',
            'ais_140_compliance': 'required' if vehicle_weight > 3500 else 'not_required',
            'permits_required': [],
            'documentation_checklist': [],
            'compliance_status': 'pending_verification'
        }
        
        # Heavy vehicle specific requirements
        if vehicle_type == 'heavy_goods_vehicle':
            compliance['permits_required'] = [
                'Goods carriage permit',
                'Route permit for interstate travel',
                'Overload permit if applicable'
            ]
            
            compliance['documentation_checklist'] = [
                'Commercial vehicle registration',
                'Goods carriage permit',
                'Driver commercial license',
                'Insurance certificate',
                'Pollution under control certificate',
                'Fitness certificate',
                'AIS-140 compliance certificate'
            ]
        
        return compliance
    
    def _check_safety_compliance(self, route_data: Dict, vehicle_info: Dict) -> Dict:
        """Check safety compliance requirements"""
        
        sharp_turns = len(route_data.get('sharp_turns', []))
        route_distance = self._parse_distance_to_km(route_data.get('distance', '0 km'))
        
        safety_compliance = {
            'driver_rest_requirements': 'mandatory' if route_distance > 500 else 'recommended',
            'emergency_equipment': 'required',
            'safety_training': 'current_certification_required',
            'route_safety_assessment': 'completed' if sharp_turns < 20 else 'high_risk_route'
        }
        
        # Distance-based requirements
        if route_distance > 1000:
            safety_compliance['co_driver_requirement'] = 'recommended'
            safety_compliance['fatigue_management'] = 'mandatory_breaks_every_4_hours'
        
        return safety_compliance
    
    def _check_environmental_compliance(self, vehicle_info: Dict, route_data: Dict) -> Dict:
        """Check environmental compliance status"""
        
        vehicle_type = vehicle_info.get('type', 'heavy_goods_vehicle')
        
        environmental = {
            'emission_standards': 'BS6_required',
            'pollution_certificate': 'valid_required',
            'environmental_zones': 'check_route_restrictions',
            'carbon_reporting': 'voluntary' if vehicle_type == 'light_motor_vehicle' else 'recommended'
        }
        
        return environmental
    
    def _check_documentation_status(self, vehicle_info: Dict) -> Dict:
        """Check documentation completeness status"""
        
        documentation = {
            'registration_documents': 'required',
            'insurance_papers': 'required',
            'driver_documents': 'required',
            'permit_documents': 'required_for_commercial',
            'maintenance_records': 'recommended',
            'compliance_certificates': 'required_for_heavy_vehicles'
        }
        
        return documentation
    
    def _calculate_compliance_score(self, compliance_tracking: Dict) -> int:
        """Calculate overall compliance score"""
        
        base_score = 100
        
        # Check each compliance area
        regulatory = compliance_tracking.get('regulatory_compliance', {})
        safety = compliance_tracking.get('safety_compliance', {})
        environmental = compliance_tracking.get('environmental_compliance', {})
        documentation = compliance_tracking.get('documentation_status', {})
        
        # Deduct points for non-compliance issues
        if regulatory.get('ais_140_compliance') == 'required' and regulatory.get('compliance_status') != 'verified':
            base_score -= 20
        
        if safety.get('route_safety_assessment') == 'high_risk_route':
            base_score -= 15
        
        if environmental.get('emission_standards') != 'BS6_compliant':
            base_score -= 10
        
        # Documentation completeness check
        required_docs = len([d for d in documentation.values() if 'required' in str(d)])
        if required_docs > 4:  # Many required documents
            base_score -= 10  # Penalty for documentation complexity
        
        return max(60, base_score)  # Minimum score of 60
    
    def _generate_compliance_action_items(self, compliance_tracking: Dict) -> List[str]:
        """Generate compliance action items"""
        
        action_items = []
        
        regulatory = compliance_tracking.get('regulatory_compliance', {})
        safety = compliance_tracking.get('safety_compliance', {})
        environmental = compliance_tracking.get('environmental_compliance', {})
        
        # Regulatory action items
        if regulatory.get('ais_140_compliance') == 'required':
            action_items.append("CRITICAL: Verify AIS-140 compliance certification")
        
        if regulatory.get('permits_required'):
            action_items.append("Ensure all required permits are current and valid")
        
        # Safety action items
        if safety.get('route_safety_assessment') == 'high_risk_route':
            action_items.append("URGENT: Conduct detailed safety briefing for high-risk route")
        
        if safety.get('driver_rest_requirements') == 'mandatory':
            action_items.append("Plan mandatory driver rest stops every 4 hours")
        
        # Environmental action items
        if environmental.get('emission_standards') == 'BS6_required':
            action_items.append("Verify vehicle meets BS6 emission standards")
        
        # General action items
        action_items.extend([
            "Complete pre-trip documentation checklist",
            "Verify insurance coverage for commercial operations",
            "Ensure driver has valid commercial license",
            "Check vehicle fitness certificate validity"
        ])
        
        return action_items