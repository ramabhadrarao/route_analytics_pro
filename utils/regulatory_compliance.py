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
                    "- GPS device installed and functional",
                    "- Panic button accessible to driver",
                    "- Emergency SOS functionality active",
                    "- Overspeed alert system configured",
                    "- Data transmission to India-based servers",
                    "- Device certification from BIS"
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
            recommendations.append("- Obtain Heavy Vehicle Permit before journey")
            recommendations.append("- Ensure driver has valid HMV license")
        
        # AIS-140 recommendations
        ais_140 = compliance_analysis.get('ais_140_compliance', {})
        if ais_140.get('mandatory', False):
            recommendations.append(" CRITICAL: Install AIS-140 compliant GPS tracking system")
            recommendations.append(" CRITICAL: Install panic button accessible to driver")
            recommendations.append("- Verify device certification from BIS")
        
        # RTSP recommendations
        rtsp = compliance_analysis.get('rtsp_compliance', {})
        rest_stops = rtsp.get('rest_requirements', {}).get('mandatory_rest_stops', 0)
        if rest_stops > 0:
            recommendations.append(f"⏰ Plan {rest_stops} mandatory rest stops (45 min each)")
        
        # State permits recommendations
        states = compliance_analysis.get('state_permits', {}).get('states_crossed', [])
        if len(states) > 1:
            recommendations.append(" Obtain inter-state permits for all states")
            for state in states:
                recommendations.append(f" Check {state}-specific entry requirements")
        
        # General recommendations
        recommendations.extend([
            "- Carry all vehicle documents (RC, Insurance, PUC)",
            "- Ensure driver medical fitness certificate is valid",
            "- Check vehicle safety equipment (first aid, fire extinguisher)",
            "- Verify speed governor installation and calibration",
            "- Plan route to avoid restricted time zones"
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
        """Estimate states crossed from route coordinates - COMPLETE INDIA COVERAGE"""
        if not route_points:
            return ["Unknown"]
        
        states_crossed = set()
        
        # Complete India state boundary mapping (28 States + 8 UTs)
        state_boundaries = {
            # NORTHERN STATES
            "Jammu and Kashmir": {"lat_range": (32.2, 37.1), "lng_range": (73.3, 80.3)},
            "Ladakh": {"lat_range": (32.2, 37.1), "lng_range": (75.9, 80.3)},
            "Himachal Pradesh": {"lat_range": (30.2, 33.2), "lng_range": (75.6, 79.0)},
            "Punjab": {"lat_range": (29.5, 32.5), "lng_range": (73.9, 76.9)},
            "Chandigarh": {"lat_range": (30.7, 30.8), "lng_range": (76.7, 76.8)},
            "Uttarakhand": {"lat_range": (28.4, 31.4), "lng_range": (77.6, 81.0)},
            "Haryana": {"lat_range": (27.4, 30.9), "lng_range": (74.4, 77.6)},
            "Delhi": {"lat_range": (28.4, 28.9), "lng_range": (76.8, 77.3)},
            "Uttar Pradesh": {"lat_range": (23.8, 30.4), "lng_range": (77.0, 84.6)},
            
            # WESTERN STATES
            "Rajasthan": {"lat_range": (23.0, 30.2), "lng_range": (69.5, 78.3)},
            "Gujarat": {"lat_range": (20.1, 24.7), "lng_range": (68.2, 74.5)},
            "Dadra and Nagar Haveli and Daman and Diu": {"lat_range": (20.0, 20.4), "lng_range": (72.8, 73.0)},
            "Maharashtra": {"lat_range": (15.6, 22.0), "lng_range": (72.6, 80.9)},
            "Goa": {"lat_range": (14.9, 15.8), "lng_range": (73.7, 74.3)},
            
            # CENTRAL STATES
            "Madhya Pradesh": {"lat_range": (21.1, 26.9), "lng_range": (74.0, 82.8)},
            "Chhattisgarh": {"lat_range": (17.8, 24.1), "lng_range": (80.2, 84.4)},
            
            # EASTERN STATES
            "Bihar": {"lat_range": (24.2, 27.5), "lng_range": (83.3, 88.3)},
            "Jharkhand": {"lat_range": (21.9, 25.3), "lng_range": (83.3, 87.9)},
            "West Bengal": {"lat_range": (21.5, 27.2), "lng_range": (85.8, 89.9)},
            "Odisha": {"lat_range": (17.8, 22.6), "lng_range": (81.3, 87.5)},
            "Sikkim": {"lat_range": (27.0, 28.1), "lng_range": (88.0, 88.9)},
            
            # NORTHEASTERN STATES
            "Assam": {"lat_range": (24.1, 28.2), "lng_range": (89.7, 96.0)},
            "Arunachal Pradesh": {"lat_range": (26.6, 29.5), "lng_range": (91.2, 97.4)},
            "Nagaland": {"lat_range": (25.2, 27.0), "lng_range": (93.3, 95.8)},
            "Manipur": {"lat_range": (23.8, 25.7), "lng_range": (93.0, 94.8)},
            "Mizoram": {"lat_range": (21.9, 24.6), "lng_range": (92.2, 93.4)},
            "Tripura": {"lat_range": (22.9, 24.5), "lng_range": (91.1, 92.7)},
            "Meghalaya": {"lat_range": (25.0, 26.1), "lng_range": (89.7, 92.8)},
            
            # SOUTHERN STATES
            "Karnataka": {"lat_range": (11.5, 18.4), "lng_range": (74.0, 78.6)},
            "Andhra Pradesh": {"lat_range": (12.6, 19.9), "lng_range": (76.7, 84.8)},
            "Telangana": {"lat_range": (15.8, 19.9), "lng_range": (77.2, 81.1)},
            "Tamil Nadu": {"lat_range": (8.0, 13.6), "lng_range": (76.2, 80.3)},
            "Kerala": {"lat_range": (8.2, 12.8), "lng_range": (74.9, 77.6)},
            "Puducherry": {"lat_range": (11.7, 12.0), "lng_range": (79.6, 79.9)},
            
            # UNION TERRITORIES & ISLANDS
            "Lakshadweep": {"lat_range": (8.0, 12.3), "lng_range": (71.0, 74.0)},
            "Andaman and Nicobar Islands": {"lat_range": (6.4, 13.7), "lng_range": (92.2, 94.3)}
        }
        
        # Check multiple points along the route for comprehensive detection
        total_points = len(route_points)
        if total_points <= 50:
            sample_points = route_points  # Use all points for small routes
        else:
            # Sample 50 points evenly distributed along the route
            step = total_points // 50
            sample_points = route_points[::step]
        
        for point in sample_points:
            if len(point) >= 2:
                try:
                    lat, lng = float(point[0]), float(point[1])
                    
                    # Check against all state boundaries
                    for state, boundaries in state_boundaries.items():
                        lat_min, lat_max = boundaries["lat_range"]
                        lng_min, lng_max = boundaries["lng_range"]
                        
                        if lat_min <= lat <= lat_max and lng_min <= lng <= lng_max:
                            states_crossed.add(state)
                except (ValueError, IndexError):
                    continue
        
        # Fallback: If no states detected, check start and end points with buffer
        if not states_crossed:
            try:
                start_lat, start_lng = float(route_points[0][0]), float(route_points[0][1])
                end_lat, end_lng = float(route_points[-1][0]), float(route_points[-1][1])
                
                # Check with ±0.5 degree buffer for boundary cases
                for state, boundaries in state_boundaries.items():
                    lat_min, lat_max = boundaries["lat_range"]
                    lng_min, lng_max = boundaries["lng_range"]
                    
                    buffer = 0.5
                    if ((lat_min - buffer) <= start_lat <= (lat_max + buffer) and 
                        (lng_min - buffer) <= start_lng <= (lng_max + buffer)) or \
                    ((lat_min - buffer) <= end_lat <= (lat_max + buffer) and 
                        (lng_min - buffer) <= end_lng <= (lng_max + buffer)):
                        states_crossed.add(state)
            except (ValueError, IndexError):
                pass
        
        # Return sorted list for consistent ordering
        result = sorted(list(states_crossed)) if states_crossed else ["Unknown Region"]
        print(f"🗺️ States detected from route coordinates: {result}")
        return result
    
    def get_state_specific_requirements(self, state: str, vehicle_info: Dict) -> Dict:
        """Get comprehensive state-specific requirements - ALL INDIA STATES"""
        
        # Complete India state requirements database
        state_requirements = {
            # NORTHERN STATES
            "Delhi": {
                "entry_restrictions": [
                    "BS-VI vehicles only (Diesel >10 years banned)",
                    "Heavy vehicles: 22:00-06:00 entry only",
                    "Even-Odd rule during pollution emergencies"
                ],
                "permits_required": [
                    "Entry permit for goods vehicles >3.5 tons (₹500-2000)",
                    "Route permit for passenger vehicles",
                    "Temporary permit for construction vehicles"
                ],
                "special_requirements": [
                    "PUC certificate renewed every 3 months",
                    "GPS tracking mandatory for commercial vehicles",
                    "Valid driving license with Delhi endorsement"
                ],
                "penalties": "No permit: ₹5,000 + seizure | Pollution: ₹10,000"
            },
            
            "Haryana": {
                "permits_required": [
                    "State goods permit (₹2,000-5,000)",
                    "Inter-state permit for cross-border travel",
                    "Mining material transport permit"
                ],
                "toll_requirements": ["FASTag mandatory", "Distance-based commercial tax"],
                "restrictions": ["Highway speed: 80 km/h", "Rural road weight: 25 tons max"],
                "fees": "State permit: ₹2,000-5,000 | Inter-state: ₹3,000-8,000"
            },
            
            "Punjab": {
                "permits_required": [
                    "Punjab state transport permit",
                    "Goods carriage permit for commercial vehicles",
                    "Agricultural produce transport permit"
                ],
                "restrictions": [
                    "Weight limit: 25 tons on state highways",
                    "Night travel restrictions in rural areas",
                    "Border area security clearance required"
                ],
                "agricultural_rules": ["Crop season transport permits", "Mandi entry permissions"]
            },
            
            "Uttar Pradesh": {
                "permits_required": [
                    "UP state goods permit (₹1,500-4,000)",
                    "City entry permits for major cities",
                    "Industrial area access permits"
                ],
                "city_restrictions": [
                    "Lucknow: Commercial vehicles banned 08:00-20:00",
                    "Kanpur: Weight restrictions on GT Road",
                    "Agra: Tourist area vehicle permits required"
                ],
                "fees": "State permit varies by district: ₹1,500-4,000"
            },
            
            "Uttarakhand": {
                "permits_required": [
                    "Hill area vehicle permit",
                    "Forest route clearance permit",
                    "Tourism vehicle registration"
                ],
                "mountain_rules": [
                    "Hill stations: Daylight travel only",
                    "Char Dham routes: Vehicle fitness <1 year",
                    "Monsoon restrictions: July-September"
                ],
                "environmental": "Emission norms strictly enforced in hill areas"
            },
            
            "Himachal Pradesh": {
                "permits_required": [
                    "Hill area permit for goods vehicles",
                    "Tourist vehicle permit",
                    "Apple/crop transport seasonal permit"
                ],
                "route_restrictions": [
                    "Mountain roads: 40 km/h speed limit",
                    "Rohtang Pass: Permit required (seasonal)",
                    "No night travel on hill roads"
                ],
                "seasonal": "Winter restrictions: December-March on high altitude routes"
            },
            
            "Jammu and Kashmir": {
                "permits_required": [
                    "J&K state permit (₹3,000-8,000)",
                    "Security clearance for certain routes",
                    "Tourist vehicle registration"
                ],
                "security_requirements": [
                    "Route approval from local authorities",
                    "Curfew compliance in sensitive areas",
                    "Identity verification at checkpoints"
                ],
                "restrictions": "Certain areas require escort | Weather-dependent closures"
            },
            
            "Ladakh": {
                "permits_required": [
                    "High altitude vehicle permit",
                    "Border area permit for certain routes",
                    "Environmental clearance"
                ],
                "special_conditions": [
                    "Altitude sickness precautions mandatory",
                    "Oxygen cylinders recommended >3500m",
                    "Vehicle winterization required"
                ],
                "seasonal": "Many routes closed October-May"
            },
            
            # WESTERN STATES
            "Rajasthan": {
                "permits_required": [
                    "Rajasthan state permit (₹2,000-6,000)",
                    "Desert area travel permit",
                    "Mining material transport permit"
                ],
                "route_restrictions": [
                    "Desert highways: 90 km/h limit",
                    "Border areas: Security clearance",
                    "Water scarcity areas: Restricted timings"
                ],
                "fees": "Varies by zone: ₹2,000-6,000 | Border permit: ₹1,000 extra"
            },
            
            "Gujarat": {
                "permits_required": [
                    "Gujarat state transport permit",
                    "Industrial area access permit",
                    "Port area clearance (Kandla/Mundra)"
                ],
                "industrial_zones": [
                    "Chemical transport: Special permits required",
                    "Hazardous material: PESO clearance",
                    "Port connectivity: Customs clearance"
                ],
                "restrictions": "Alcohol transport completely banned"
            },
            
            "Maharashtra": {
                "permits_required": [
                    "Maharashtra state permit (₹2,500-7,000)",
                    "Mumbai/Pune city entry permit",
                    "Ghat section travel permit"
                ],
                "city_restrictions": [
                    "Mumbai: Heavy vehicles banned 07:00-11:00",
                    "Pune: Odd-even for goods vehicles",
                    "Nashik: Industrial area permits"
                ],
                "ghat_rules": [
                    "Speed limit: 30 km/h on all ghats",
                    "Mandatory rest stops every 50km",
                    "Monsoon restrictions: June-September"
                ],
                "penalties": "Overweight: ₹1,000/ton | Ghat speed: ₹5,000 + suspension"
            },
            
            "Goa": {
                "permits_required": [
                    "Goa entry permit for commercial vehicles",
                    "Tourism vehicle registration",
                    "Beach area access permit"
                ],
                "environmental": [
                    "Strict emission norms near beaches",
                    "Noise pollution restrictions",
                    "Waste disposal compliance"
                ],
                "tourism_rules": "Peak season restrictions: December-February"
            },
            
            # CENTRAL STATES
            "Madhya Pradesh": {
                "permits_required": [
                    "MP state permit (₹1,800-5,000)",
                    "Forest route clearance",
                    "Mining area access permit"
                ],
                "forest_rules": [
                    "Tiger reserve routes: Daylight only",
                    "No idling in forest areas",
                    "Wildlife corridor speed limits: 40 km/h"
                ],
                "tribal_areas": "Special permits for scheduled area travel"
            },
            
            "Chhattisgarh": {
                "permits_required": [
                    "Chhattisgarh state permit",
                    "Mining transport permit",
                    "Tribal area travel permit"
                ],
                "mining_zones": [
                    "Coal transport: Special documentation",
                    "Iron ore: Weighment certificates",
                    "Forest clearance for mining routes"
                ],
                "security": "Naxal-affected areas: Police escort recommended"
            },
            
            # EASTERN STATES
            "West Bengal": {
                "permits_required": [
                    "West Bengal state permit (₹2,200-6,500)",
                    "Kolkata city entry permit",
                    "Border trade permit (Bangladesh border)"
                ],
                "city_restrictions": [
                    "Kolkata: Commercial vehicles banned 08:00-20:00",
                    "Salt Lake: IT sector vehicle permits",
                    "Port area: Customs clearance required"
                ],
                "border_rules": "International border: Additional security clearance"
            },
            
            "Bihar": {
                "permits_required": [
                    "Bihar state permit (₹1,500-4,500)",
                    "Patna city entry permit",
                    "Agricultural produce transport permit"
                ],
                "route_conditions": [
                    "Monsoon flooding: Route diversions common",
                    "Bridge weight restrictions",
                    "Rural area security considerations"
                ],
                "agricultural": "Crop season: Special permits for farm equipment"
            },
            
            "Jharkhand": {
                "permits_required": [
                    "Jharkhand state permit",
                    "Mining area access permit",
                    "Tribal belt travel permit"
                ],
                "mining_compliance": [
                    "Coal corridor permits",
                    "Mineral transport documentation",
                    "Environmental clearance certificates"
                ],
                "security": "Mining areas: Security clearance recommended"
            },
            
            "Odisha": {
                "permits_required": [
                    "Odisha state permit (₹1,800-5,200)",
                    "Coastal area vehicle permit",
                    "Mining transport permit"
                ],
                "coastal_rules": [
                    "Cyclone season restrictions: May-November",
                    "Port area clearances",
                    "Fishing zone vehicle permits"
                ],
                "mining": "Iron ore transport: Strict documentation required"
            },
            
            "Sikkim": {
                "permits_required": [
                    "Sikkim permit for all vehicles",
                    "High altitude vehicle clearance",
                    "Tourism vehicle registration"
                ],
                "altitude_rules": [
                    "Above 4000m: Special vehicle requirements",
                    "Border area: Military clearance",
                    "Eco-sensitive zones: Restricted access"
                ],
                "fees": "Entry permit: ₹200-500 | Tourism: ₹1,000-3,000"
            },
            
            # NORTHEASTERN STATES
            "Assam": {
                "permits_required": [
                    "Assam state permit",
                    "Inner Line Permit for certain areas",
                    "Tea garden area access permit"
                ],
                "flood_restrictions": [
                    "Monsoon season: Route diversions",
                    "Brahmaputra bridge timings",
                    "Flood-prone area vehicle restrictions"
                ],
                "ethnic_areas": "Tribal belt: Special permissions required"
            },
            
            "Arunachal Pradesh": {
                "permits_required": [
                    "Inner Line Permit (mandatory for all)",
                    "Border area permit",
                    "High altitude vehicle clearance"
                ],
                "border_security": [
                    "China border: Military escort required",
                    "Photography restrictions",
                    "Route approval from local authorities"
                ],
                "fees": "ILP: ₹300-500 | Vehicle permit: ₹1,000-2,500"
            },
            
            "Nagaland": {
                "permits_required": [
                    "Inner Line Permit",
                    "Vehicle registration in state",
                    "Tribal area travel permit"
                ],
                "cultural_restrictions": [
                    "Festival periods: Movement restrictions",
                    "Sunday restrictions in Christian areas",
                    "Traditional area permissions"
                ],
                "fees": "ILP: ₹100-300 | Vehicle: ₹500-1,500"
            },
            
            "Manipur": {
                "permits_required": [
                    "Manipur permit for non-residents",
                    "Restricted Area Permit",
                    "Border area clearance"
                ],
                "security_zones": [
                    "Disturbed area: Security clearance",
                    "Border areas: Military permission",
                    "Curfew compliance required"
                ],
                "restrictions": "Certain roads: Daylight travel only"
            },
            
            "Mizoram": {
                "permits_required": [
                    "Inner Line Permit (mandatory)",
                    "Vehicle entry permit",
                    "Liquor transport ban compliance"
                ],
                "local_laws": [
                    "Alcohol completely banned",
                    "Sunday movement restrictions",
                    "Local customs compliance"
                ],
                "fees": "ILP: ₹50-200 | Vehicle: ₹300-800"
            },
            
            "Tripura": {
                "permits_required": [
                    "Tripura state permit",
                    "Bangladesh border area permit",
                    "Tribal area access permit"
                ],
                "border_compliance": [
                    "International border security",
                    "Customs clearance for goods",
                    "Identity verification at checkpoints"
                ],
                "fees": "State permit: ₹500-1,500"
            },
            
            "Meghalaya": {
                "permits_required": [
                    "Meghalaya entry permit",
                    "Coal mining area permit",
                    "Tribal belt travel permit"
                ],
                "environmental": [
                    "Coal transport: Environmental clearance",
                    "Forest route permissions",
                    "Eco-sensitive area restrictions"
                ],
                "fees": "Entry permit: ₹200-600"
            },
            
            # SOUTHERN STATES
            "Karnataka": {
                "permits_required": [
                    "Karnataka state permit (₹2,000-6,000)",
                    "Bangalore city entry permit",
                    "Ghat section travel permit"
                ],
                "city_restrictions": [
                    "Bangalore: Heavy vehicles banned 06:00-10:00 & 17:00-21:00",
                    "Mysore: Palace area vehicle restrictions",
                    "Mangalore: Port area clearances"
                ],
                "ghat_rules": "Western Ghats: Speed 40 km/h | Monsoon restrictions"
            },
            
            "Andhra Pradesh": {
                "permits_required": [
                    "AP state permit (₹1,800-5,500)",
                    "Hyderabad-Secunderabad entry permit",
                    "Port connectivity permit"
                ],
                "industrial_zones": [
                    "IT corridor: Special vehicle permits",
                    "Pharma zone: Material transport clearance",
                    "Port areas: Customs documentation"
                ],
                "fees": "State permit varies by region: ₹1,800-5,500"
            },
            
            "Telangana": {
                "permits_required": [
                    "Telangana state permit",
                    "Hyderabad city area permit",
                    "IT corridor access permit"
                ],
                "city_rules": [
                    "Hyderabad: HITEC City restrictions",
                    "ORR access: Toll compliance",
                    "Airport connectivity: Security clearance"
                ],
                "fees": "New state: Permit fees ₹1,500-4,500"
            },
            
            "Tamil Nadu": {
                "permits_required": [
                    "Tamil Nadu temporary permit (₹500-2,000)",
                    "Chennai city entry permit",
                    "Port area access permit"
                ],
                "city_restrictions": [
                    "Chennai: Heavy vehicles banned 06:00-22:00",
                    "Coimbatore: Textile zone permits",
                    "Madurai: Heritage area restrictions"
                ],
                "validity": "Inter-state permits: 30 days maximum",
                "fees": "Temporary permit: ₹500-2,000 based on duration"
            },
            
            "Kerala": {
                "permits_required": [
                    "Kerala state permit (₹1,200-4,000)",
                    "Ghat road travel permit",
                    "Backwater area vehicle permit"
                ],
                "environmental": [
                    "Western Ghats: Strict emission norms",
                    "Backwaters: Noise restrictions",
                    "Spice plantation routes: Speed limits"
                ],
                "monsoon_rules": "Heavy monsoon: Route restrictions June-September"
            },
            
            # UNION TERRITORIES
            "Chandigarh": {
                "permits_required": [
                    "UT area entry permit",
                    "Sector-wise vehicle permits",
                    "Government area access clearance"
                ],
                "city_planning": [
                    "Sector restrictions for heavy vehicles",
                    "Government offices: Time restrictions",
                    "Planned city: Route compliance mandatory"
                ],
                "fees": "UT permit: ₹200-800"
            },
            
            "Puducherry": {
                "permits_required": [
                    "Puducherry entry permit",
                    "Beach area vehicle permit",
                    "French quarter access permit"
                ],
                "tourism_rules": [
                    "Heritage area restrictions",
                    "Beach front: Environmental compliance",
                    "Tourism season: Additional regulations"
                ],
                "fees": "Entry permit: ₹300-1,000"
            },
            
            "Dadra and Nagar Haveli and Daman and Diu": {
                "permits_required": [
                    "UT entry permit",
                    "Industrial area access",
                    "Coastal area vehicle permit"
                ],
                "industrial": [
                    "Chemical zone clearances",
                    "Port connectivity permits",
                    "Hazardous material transport"
                ],
                "fees": "UT permit: ₹400-1,200"
            },
            
            "Lakshadweep": {
                "permits_required": [
                    "Island entry permit (mandatory)",
                    "Vehicle shipping clearance",
                    "Environmental compliance certificate"
                ],
                "special_conditions": [
                    "Vehicle transport by ship only",
                    "Limited road network",
                    "Coral reef protection compliance"
                ],
                "restrictions": "Very limited vehicle access"
            },
            
            "Andaman and Nicobar Islands": {
                "permits_required": [
                    "Island entry permit",
                    "Vehicle shipping documentation",
                    "Forest area clearance"
                ],
                "island_rules": [
                    "Inter-island transport restrictions",
                    "Tribal areas: Complete prohibition",
                    "Military areas: Security clearance"
                ],
                "shipping": "Vehicle transport: Mainland to island shipping only"
            }
        }
        
        # Return state-specific requirements or generic template
        if state in state_requirements:
            return state_requirements[state]
        else:
            # Generic template for states not explicitly listed
            return {
                "permits_required": [
                    f"{state} state goods permit",
                    "Inter-state permit if crossing borders",
                    "City entry permits for major cities"
                ],
                "general_requirements": [
                    "Valid vehicle registration certificate",
                    "Current insurance certificate",
                    "Pollution Under Control (PUC) certificate",
                    "Valid driving license"
                ],
                "compliance_note": f"Contact {state} State Transport Authority for specific requirements",
                "estimated_fees": "₹1,500-5,000 depending on vehicle category and route",
                "validity": "Permits typically valid for 30-90 days"
            }
    
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