# utils/regulatory_compliance.py - Regulatory Compliance Module

import json
import datetime
from typing import Dict, List, Tuple, Any

class RegulatoryComplianceAnalyzer:
    """Analyze route compliance with CMVR, AIS-140, RTSP and local regulations"""
    
    def __init__(self):
        self.compliance_data = self.load_compliance_database()
        
    def load_compliance_database(self) -> Dict:
        """Load regulatory compliance database"""
        # In production, this would load from the JSON file
        # For now, we'll include essential data inline
        return {
            "cmvr_compliance": {
                "speed_limits": {
                    "urban_areas": {"light_vehicles": 50, "heavy_vehicles": 40, "near_schools": 25},
                    "highways": {"light_vehicles": 100, "heavy_vehicles": 80, "expressways": 120},
                    "rural_roads": {"all_vehicles": 70, "heavy_vehicles": 60}
                },
                "vehicle_classification": {
                    "light_motor_vehicle": {"weight_limit": 3500, "license": "LMV"},
                    "medium_goods_vehicle": {"weight_range": "3501-12000", "license": "HMV"},
                    "heavy_goods_vehicle": {"weight_range": ">12000", "license": "HMV", "permits": True}
                }
            },
            "ais_140_requirements": {
                "mandatory_for": ["Commercial >3.5 tons", "Passenger >9 seats", "School buses", "Hazardous materials"],
                "devices": ["GPS tracking", "Panic button", "Emergency SOS", "Overspeed alerts"]
            },
            "rtsp_compliance": {
                "driving_hours": {"max_continuous": 4.5, "daily_max": 10, "weekly_max": 56},
                "rest_requirements": {"after_4_5_hours": 45, "daily_rest": 11, "weekly_rest": 45},
                "night_restrictions": {"start": "22:00", "end": "06:00", "speed_reduction": 10}
            }
        }
    
    def analyze_route_compliance(self, route_data: Dict, vehicle_info: Dict = None) -> Dict:
        """Analyze complete route compliance"""
        
        # Default vehicle info if not provided
        if not vehicle_info:
            vehicle_info = {
                "type": "heavy_goods_vehicle",
                "weight": 15000,  # kg
                "passenger_capacity": 2,
                "vehicle_category": "Transport Vehicle",
                "fuel_type": "Diesel"
            }
        
        compliance_analysis = {
            "route_summary": self.get_route_compliance_summary(route_data, vehicle_info),
            "cmvr_compliance": self.analyze_cmvr_compliance(route_data, vehicle_info),
            "ais_140_compliance": self.analyze_ais_140_compliance(vehicle_info),
            "rtsp_compliance": self.analyze_rtsp_compliance(route_data, vehicle_info),
            "state_permits": self.analyze_state_permits(route_data, vehicle_info),
            "compliance_score": 0,
            "critical_violations": [],
            "recommendations": []
        }
        
        # Calculate overall compliance score
        compliance_analysis["compliance_score"] = self.calculate_compliance_score(compliance_analysis)
        
        # Generate recommendations
        compliance_analysis["recommendations"] = self.generate_compliance_recommendations(compliance_analysis)
        
        return compliance_analysis
    
    def get_route_compliance_summary(self, route_data: Dict, vehicle_info: Dict) -> Dict:
        """Get basic route compliance summary"""
        route_points = route_data.get('route_points', [])
        distance = route_data.get('distance', 'Unknown')
        duration = route_data.get('duration', 'Unknown')
        
        # Estimate states crossed (simplified logic)
        states_crossed = self.estimate_states_from_coordinates(route_points)
        
        return {
            "route_distance": distance,
            "estimated_duration": duration,
            "vehicle_type": vehicle_info.get('type', 'Unknown'),
            "vehicle_weight": f"{vehicle_info.get('weight', 0)} kg",
            "states_crossed": states_crossed,
            "compliance_category": self.determine_compliance_category(vehicle_info),
            "permit_requirements": self.get_permit_requirements(vehicle_info, states_crossed)
        }
    
    def analyze_cmvr_compliance(self, route_data: Dict, vehicle_info: Dict) -> Dict:
        """Analyze CMVR 1989 and Amendment 2022 compliance"""
        
        weight = vehicle_info.get('weight', 0)
        vehicle_type = self.classify_vehicle_by_weight(weight)
        
        # Get applicable speed limits based on route type
        speed_limits = self.get_applicable_speed_limits(vehicle_type, route_data)
        
        # Check mandatory equipment based on 2022 amendment
        mandatory_equipment = self.get_mandatory_equipment_2022(vehicle_type)
        
        return {
            "vehicle_classification": {
                "category": vehicle_type,
                "weight_category": f"{weight} kg",
                "license_required": self.get_required_license(vehicle_type),
                "permit_required": weight > 12000
            },
            "speed_limits": speed_limits,
            "mandatory_equipment_2022": mandatory_equipment,
            "driver_requirements": {
                "training_hours": self.get_required_training_hours(vehicle_type),
                "medical_fitness": "Valid for 3 years",
                "mandatory_tests": ["Vision", "Hearing", "Coordination"]
            },
            "compliance_status": "Requires Verification",
            "critical_requirements": [
                "Valid driving license for vehicle category",
                "Vehicle registration certificate",
                "Insurance certificate",
                "Pollution Under Control (PUC) certificate"
            ]
        }
    
    def analyze_ais_140_compliance(self, vehicle_info: Dict) -> Dict:
        """Analyze AIS-140 compliance requirements"""
        
        weight = vehicle_info.get('weight', 0)
        passenger_capacity = vehicle_info.get('passenger_capacity', 0)
        
        # Determine if AIS-140 is mandatory
        is_mandatory = (
            weight > 3500 or  # >3.5 tons
            passenger_capacity > 9 or  # >9 passengers
            vehicle_info.get('type') == 'school_bus' or
            vehicle_info.get('cargo_type') == 'hazardous'
        )
        
        if is_mandatory:
            compliance_requirements = {
                "mandatory": True,
                "compliance_deadline": "April 1, 2023",
                "required_devices": {
                    "gps_tracking": {
                        "accuracy": "±3 meters",
                        "update_frequency": "10 seconds",
                        "data_storage": "30 days minimum"
                    },
                    "panic_button": {
                        "location": "Driver accessible",
                        "response_time": "<5 seconds",
                        "alert_recipients": ["Police", "Owner", "Control Center"]
                    },
                    "vehicle_tracking_terminal": {
                        "certification": "BIS certified mandatory",
                        "installation": "Authorized centers only",
                        "backup_power": "4 hours minimum"
                    }
                },
                "compliance_checklist": [
                    "✓ GPS device installed and functional",
                    "✓ Panic button accessible to driver",
                    "✓ Emergency SOS functionality active",
                    "✓ Overspeed alert system configured",
                    "✓ Data transmission to India-based servers",
                    "✓ Device certification from BIS"
                ]
            }
        else:
            compliance_requirements = {
                "mandatory": False,
                "reason": "Vehicle below AIS-140 threshold",
                "voluntary_adoption": "Recommended for safety"
            }
        
        return compliance_requirements
    
    def analyze_rtsp_compliance(self, route_data: Dict, vehicle_info: Dict) -> Dict:
        """Analyze Road Transport Safety Policy compliance"""
        
        # Estimate driving time
        duration_str = route_data.get('duration', '0 hours')
        estimated_hours = self.parse_duration_to_hours(duration_str)
        
        # Calculate required rest stops
        required_rest_stops = max(0, int(estimated_hours / 4.5))
        daily_compliance = estimated_hours <= 10
        
        return {
            "driving_time_analysis": {
                "estimated_driving_time": f"{estimated_hours:.1f} hours",
                "max_continuous_allowed": "4.5 hours",
                "daily_max_allowed": "10 hours", 
                "compliance": daily_compliance
            },
            "rest_requirements": {
                "mandatory_rest_stops": required_rest_stops,
                "rest_duration": "45 minutes minimum per stop",
                "daily_rest": "11 hours continuous",
                "weekly_rest": "45 hours"
            },
            "night_driving_restrictions": {
                "night_hours": "22:00 to 06:00",
                "speed_reduction": "10 km/h below daytime limits",
                "additional_safety": [
                    "Enhanced lighting systems required",
                    "Fatigue monitoring mandatory",
                    "Driver alertness checks"
                ]
            },
            "route_specific_requirements": self.get_route_specific_rtsp_requirements(route_data),
            "compliance_recommendations": [
                f"Plan {required_rest_stops} rest stops during journey",
                "Ensure driver gets 11 hours rest before journey",
                "Avoid night driving on mountain/ghat sections",
                "Use fatigue monitoring systems"
            ]
        }
    
    def analyze_state_permits(self, route_data: Dict, vehicle_info: Dict) -> Dict:
        """Analyze state-specific permit requirements"""
        
        route_points = route_data.get('route_points', [])
        states_crossed = self.estimate_states_from_coordinates(route_points)
        
        permits_analysis = {}
        
        for state in states_crossed:
            permits_analysis[state] = self.get_state_specific_requirements(state, vehicle_info)
        
        return {
            "states_crossed": states_crossed,
            "permit_requirements": permits_analysis,
            "inter_state_compliance": len(states_crossed) > 1,
            "critical_permits": [
                "All State Entry Permits" if len(states_crossed) > 1 else "Local State Permit",
                "Route Permit for Commercial Vehicles",
                "Environmental Clearance (if applicable)",
                "Temporary Permits for Special Zones"
            ]
        }
    
    def calculate_compliance_score(self, compliance_analysis: Dict) -> int:
        """Calculate overall compliance score (0-100)"""
        
        score = 100
        
        # Deduct points for non-compliance
        cmvr = compliance_analysis.get('cmvr_compliance', {})
        ais_140 = compliance_analysis.get('ais_140_compliance', {})
        rtsp = compliance_analysis.get('rtsp_compliance', {})
        
        # CMVR compliance deductions
        if not cmvr.get('vehicle_classification', {}).get('permit_required', False):
            score -= 15
        
        # AIS-140 compliance deductions
        if ais_140.get('mandatory', False):
            score -= 25  # Major deduction if mandatory but not addressed
        
        # RTSP compliance deductions
        rtsp_driving = rtsp.get('driving_time_analysis', {})
        if not rtsp_driving.get('compliance', True):
            score -= 20
        
        # State permits deductions
        states_count = len(compliance_analysis.get('state_permits', {}).get('states_crossed', []))
        if states_count > 1:
            score -= 10  # Inter-state complexity
        
        return max(0, min(100, score))
    
    def generate_compliance_recommendations(self, compliance_analysis: Dict) -> List[str]:
        """Generate compliance recommendations"""
        
        recommendations = []
        
        # CMVR recommendations
        cmvr = compliance_analysis.get('cmvr_compliance', {})
        if cmvr.get('vehicle_classification', {}).get('permit_required', False):
            recommendations.append("✓ Obtain Heavy Vehicle Permit before journey")
            recommendations.append("✓ Ensure driver has valid HMV license")
        
        # AIS-140 recommendations
        ais_140 = compliance_analysis.get('ais_140_compliance', {})
        if ais_140.get('mandatory', False):
            recommendations.append("🔴 CRITICAL: Install AIS-140 compliant GPS tracking system")
            recommendations.append("🔴 CRITICAL: Install panic button accessible to driver")
            recommendations.append("✓ Verify device certification from BIS")
        
        # RTSP recommendations
        rtsp = compliance_analysis.get('rtsp_compliance', {})
        rest_stops = rtsp.get('rest_requirements', {}).get('mandatory_rest_stops', 0)
        if rest_stops > 0:
            recommendations.append(f"⏰ Plan {rest_stops} mandatory rest stops (45 min each)")
        
        # State permits recommendations
        states = compliance_analysis.get('state_permits', {}).get('states_crossed', [])
        if len(states) > 1:
            recommendations.append("📋 Obtain inter-state permits for all states")
            for state in states:
                recommendations.append(f"📋 Check {state}-specific entry requirements")
        
        # General recommendations
        recommendations.extend([
            "✓ Carry all vehicle documents (RC, Insurance, PUC)",
            "✓ Ensure driver medical fitness certificate is valid",
            "✓ Check vehicle safety equipment (first aid, fire extinguisher)",
            "✓ Verify speed governor installation and calibration",
            "✓ Plan route to avoid restricted time zones"
        ])
        
        return recommendations
    
    # Helper methods
    def classify_vehicle_by_weight(self, weight: int) -> str:
        """Classify vehicle by weight"""
        if weight <= 3500:
            return "Light Motor Vehicle"
        elif weight <= 12000:
            return "Medium Goods Vehicle"
        else:
            return "Heavy Goods Vehicle"
    
    def get_required_license(self, vehicle_type: str) -> str:
        """Get required license type"""
        if vehicle_type == "Light Motor Vehicle":
            return "LMV (Light Motor Vehicle)"
        else:
            return "HMV (Heavy Motor Vehicle)"
    
    def get_required_training_hours(self, vehicle_type: str) -> str:
        """Get required training hours"""
        if vehicle_type == "Light Motor Vehicle":
            return "30 hours"
        elif vehicle_type == "Medium Goods Vehicle":
            return "60 hours"
        else:
            return "80 hours"
    
    def get_applicable_speed_limits(self, vehicle_type: str, route_data: Dict) -> Dict:
        """Get applicable speed limits"""
        if "Heavy" in vehicle_type:
            return {
                "Urban areas": "40 km/h",
                "Near schools": "25 km/h", 
                "Highways": "80 km/h",
                "Rural roads": "60 km/h",
                "Night driving": "Reduce by 10 km/h"
            }
        else:
            return {
                "Urban areas": "50 km/h",
                "Near schools": "25 km/h",
                "Highways": "100 km/h", 
                "Rural roads": "70 km/h",
                "Night driving": "Reduce by 10 km/h"
            }
    
    def get_mandatory_equipment_2022(self, vehicle_type: str) -> List[str]:
        """Get mandatory equipment per 2022 amendment"""
        base_equipment = [
            "GPS tracking system",
            "Emergency panic button", 
            "First aid kit",
            "Fire extinguisher",
            "Reflective triangles",
            "High visibility jacket"
        ]
        
        if "Heavy" in vehicle_type:
            base_equipment.extend([
                "Driver fatigue detection system",
                "Overspeed warning system",
                "Speed governor",
                "Reverse parking sensor"
            ])
        
        return base_equipment
    
    def estimate_states_from_coordinates(self, route_points: List) -> List[str]:
        """Estimate states crossed from route coordinates (simplified)"""
        if not route_points:
            return ["Unknown"]
        
        # Simplified logic - in production, use proper geocoding
        start_point = route_points[0]
        end_point = route_points[-1]
        
        # Sample mapping (would be more comprehensive in production)
        state_mapping = {
            (28.0, 29.0, 76.0, 78.0): "Delhi/Haryana",
            (18.0, 20.0, 72.0, 75.0): "Maharashtra", 
            (12.0, 14.0, 77.0, 79.0): "Karnataka",
            (10.0, 12.0, 78.0, 80.0): "Tamil Nadu"
        }
        
        # Simple estimation
        return ["Delhi", "Haryana"]  # Placeholder
    
    def get_state_specific_requirements(self, state: str, vehicle_info: Dict) -> Dict:
        """Get state-specific requirements"""
        # Sample requirements - would be more comprehensive in production
        state_requirements = {
            "Delhi": {
                "entry_restrictions": "BS-VI vehicles only",
                "permits": ["Entry permit for goods vehicles"],
                "timing": "Night entry only (22:00-06:00)",
                "special_requirements": ["Valid PUC certificate"]
            },
            "Maharashtra": {
                "toll_requirements": "FASTag mandatory",
                "permits": ["State goods permit"],
                "restrictions": ["Speed limit 30 km/h on ghats"],
                "penalties": "₹1000 per ton overweight"
            }
        }
        
        return state_requirements.get(state, {
            "permits": ["Standard state permit required"],
            "requirements": ["Valid vehicle documents"],
            "restrictions": ["Follow state traffic rules"]
        })
    
    def parse_duration_to_hours(self, duration_str: str) -> float:
        """Parse duration string to hours"""
        try:
            # Simple parsing - in production, use more robust parsing
            if "hour" in duration_str:
                return float(duration_str.split()[0])
            elif "min" in duration_str:
                return float(duration_str.split()[0]) / 60
            else:
                return 8.0  # Default assumption
        except:
            return 8.0
    
    def get_route_specific_rtsp_requirements(self, route_data: Dict) -> List[str]:
        """Get route-specific RTSP requirements"""
        requirements = []
        
        # Check for mountain roads
        sharp_turns = route_data.get('sharp_turns', [])
        if len(sharp_turns) > 10:
            requirements.append("Mountain road protocols: Rest every 2 hours")
            requirements.append("Speed reduction: 20 km/h below normal limits")
        
        # Check for high-density traffic areas
        if route_data.get('distance', '').replace('km', '').strip().isdigit():
            distance = float(route_data.get('distance', '0').replace('km', '').strip())
            if distance > 500:
                requirements.append("Long distance: Mandatory overnight rest")
        
        return requirements
    
    def determine_compliance_category(self, vehicle_info: Dict) -> str:
        """Determine compliance category"""
        weight = vehicle_info.get('weight', 0)
        
        if weight > 12000:
            return "HIGH RISK - Heavy Goods Vehicle"
        elif weight > 3500:
            return "MEDIUM RISK - Medium Goods Vehicle"
        else:
            return "LOW RISK - Light Motor Vehicle"
    
    def get_permit_requirements(self, vehicle_info: Dict, states: List[str]) -> List[str]:
        """Get permit requirements based on vehicle and states"""
        requirements = []
        
        weight = vehicle_info.get('weight', 0)
        
        if weight > 12000:
            requirements.append("Heavy Vehicle Permit")
        
        if len(states) > 1:
            requirements.append("Inter-State Permit")
        
        requirements.extend([
            "Route Permit",
            "Goods Carriage Permit" if weight > 3500 else "Standard Permit"
        ])
        
        return requirements