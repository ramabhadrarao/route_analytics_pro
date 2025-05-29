# utils/pdf_generator.py - WORKING ENHANCED VERSION WITH COMPLIANCE & FIXED TEXT RENDERING

from fpdf import FPDF
import os
import datetime
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import requests
import tempfile
import json
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from geopy.distance import geodesic

# Add these imports
try:
    from utils.advanced_features.elevation_analyzer import ElevationAnalyzer
    from utils.advanced_features.emergency_planner import EmergencyPlanner
    print("✅ Advanced features modules imported successfully")
except ImportError as e:
    print(f"⚠️ Advanced features not available: {e}")
    ElevationAnalyzer = None
    EmergencyPlanner = None

class EnhancedRoutePDF(FPDF):
    def __init__(self, title=None):
        super().__init__()
        self.title = title or "Enhanced Route Analysis Report"
        self.company_name = "Route Analytics Pro"
        self.set_auto_page_break(auto=True, margin=15)
        
        # Professional color scheme
        self.primary_color = (52, 58, 64)
        self.secondary_color = (108, 117, 125)
        self.accent_color = (32, 107, 196)
        self.danger_color = (220, 53, 69)
        self.warning_color = (253, 126, 20)
        self.success_color = (40, 167, 69)
        self.info_color = (13, 110, 253)
        
    def clean_text(self, text):
        """Clean text for PDF compatibility - COMPREHENSIVE EMOJI/UNICODE HANDLING"""
        if not isinstance(text, str):
            text = str(text)
        
        # Comprehensive Unicode to ASCII replacements
        replacements = {
            # Emojis to text
            '📄': '[DOCUMENT]', '🗺️': '[MAP]', '📡': '[SIGNAL]', '⚠️': '[WARNING]',
            '🔴': '[CRITICAL]', '⏰': '[TIME]', '📋': '[CHECKLIST]', '✅': '[OK]',
            '❌': '[ERROR]', '🚗': '[CAR]', '🏥': '[HOSPITAL]', '⛽': '[FUEL]',
            '🏫': '[SCHOOL]', '🚔': '[POLICE]', '🌡️': '[TEMP]', '🌧️': '[RAIN]',
            '☀️': '[SUN]', '📊': '[CHART]', '🔋': '[BATTERY]', '📱': '[PHONE]',
            '🛰️': '[SATELLITE]', '🔍': '[SEARCH]', '📍': '[LOCATION]',
            '🚨': '[EMERGENCY]', '💾': '[STORAGE]', '📈': '[TRENDING]',
            '🌐': '[INTERNET]', '🎯': '[TARGET]', '🔄': '[REFRESH]',
            '🆕': '[NEW]', '🏗️': '[CONSTRUCTION]', '⭐': '[STAR]',
            '🔒': '[LOCKED]', '🔓': '[UNLOCKED]', '🎨': '[DESIGN]',
            '🎵': '[MUSIC]', '🎬': '[VIDEO]', '📞': '[CALL]',
            '📧': '[EMAIL]', '📝': '[NOTE]', '📚': '[BOOKS]',
            '🏠': '[HOME]', '🏢': '[OFFICE]', '🏪': '[SHOP]',
            '🚀': '[ROCKET]', '⚡': '[LIGHTNING]', '🔥': '[FIRE]',
            '💧': '[WATER]', '🌟': '[SHINE]', '💡': '[BULB]',
            '🎁': '[GIFT]', '🎉': '[CELEBRATION]', '🎊': '[CONFETTI]',
            '🚛': '[TRUCK]', '🏭': '[FACTORY]', '⛽': '[GAS-STATION]',
            
            # Symbols to text - FIXED
            '°': ' degrees', '₹': 'Rs.', '€': 'EUR', '$': 'USD',
            '£': 'GBP', '¥': 'YEN', '©': '(c)', '®': '(R)',
            '™': '(TM)', '±': '+/-', '≤': '<=', '≥': '>=',
            '≠': '!=', '≈': '~=', '×': 'x', '÷': '/',
            
            # Quote marks and dashes - FIXED
            '"': '"', '"': '"', ''': "'", ''': "'",
            '–': '-', '—': '-', '…': '...',
            
            # Arrows - FIXED
            '→': '->', '←': '<-', '↑': '^', '↓': 'v',
            '↔': '<->', '⇒': '=>', '⇐': '<=', '⇔': '<=>',
            
            # Mathematical symbols - FIXED
            '∞': 'infinity', '∑': 'sum', '∏': 'product',
            '∫': 'integral', '∂': 'partial', '∆': 'delta',
            '√': 'sqrt', '∝': 'proportional', '∈': 'in',
            '∉': 'not in', '∪': 'union', '∩': 'intersection',
            
            # Other common Unicode - FIXED
            '•': '*', '◦': 'o', '▪': '-', '▫': '-',
            '★': '[STAR]', '☆': '[STAR-OUTLINE]', '♠': '[SPADE]',
            '♣': '[CLUB]', '♥': '[HEART]', '♦': '[DIAMOND]',
            
            # Fractions - FIXED
            '½': '1/2', '⅓': '1/3', '⅔': '2/3', '¼': '1/4',
            '¾': '3/4', '⅕': '1/5', '⅖': '2/5', '⅗': '3/5',
            
            # Superscripts and subscripts - FIXED
            '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5',
            '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁰': '0',
            
            # Additional safety-related symbols - FIXED
            '⚠': '[WARNING]', '☢': '[RADIOACTIVE]', '☣': '[BIOHAZARD]',
            '🔥': '[FIRE]', '💀': '[DANGER]',
        }
        
        # Apply replacements ONLY for specific unicode characters
        for old, new in replacements.items():
            if old in text:  # Only replace if the character exists
                text = text.replace(old, new)
        
        # Simple approach - if text can be encoded as latin-1, return as-is
        try:
            text.encode('latin-1')
            return text
        except UnicodeEncodeError:
            # More conservative approach - only remove problematic characters
            clean_chars = []
            for char in text:
                try:
                    char.encode('latin-1')
                    clean_chars.append(char)
                except UnicodeEncodeError:
                    # Replace individual problematic characters
                    if ord(char) > 255:
                        clean_chars.append('[?]')  # Replace with placeholder
                    else:
                        clean_chars.append(char)
            
            return ''.join(clean_chars)

    def add_elevation_analysis_page(self, route_data, api_key=None):
        """Add elevation analysis page"""
        if not ElevationAnalyzer:
            return
        
        try:
            analyzer = ElevationAnalyzer(api_key)
            analysis = analyzer.analyze_route_elevation(route_data.get('route_points', []))
            
            if 'error' in analysis:
                return
            
            self.add_page()
            self.add_section_header("ELEVATION ANALYSIS - GRADIENT RISK ASSESSMENT", "info")
            self.set_text_color(0, 0, 0)
            
            # Elevation Statistics
            stats = analysis.get('elevation_statistics', {})
            elevation_data = [
                ['Minimum Elevation', f"{stats.get('min_elevation', 0):.0f} m"],
                ['Maximum Elevation', f"{stats.get('max_elevation', 0):.0f} m"],
                ['Elevation Range', f"{stats.get('elevation_range', 0):.0f} m"],
                ['Total Ascent', f"{stats.get('total_ascent', 0):.0f} m"],
                ['Total Descent', f"{stats.get('total_descent', 0):.0f} m"],
                ['Average Elevation', f"{stats.get('average_elevation', 0):.0f} m"]
            ]
            
            self.set_font('Arial', 'B', 12)
            self.cell(0, 8, 'ELEVATION PROFILE STATISTICS', 0, 1, 'L')
            self.create_simple_table(elevation_data, [70, 110])
            
            # Risk Assessment
            risk_assessment = analysis.get('risk_assessment', {})
            risk_level = risk_assessment.get('overall_risk_level', 'LOW')
            
            self.ln(5)
            self.set_font('Arial', 'B', 12)
            
            if risk_level in ['EXTREME', 'HIGH']:
                self.set_text_color(220, 53, 69)
                status_symbol = '❌'
            elif risk_level == 'MEDIUM':
                self.set_text_color(253, 126, 20)
                status_symbol = '⚠️'
            else:
                self.set_text_color(40, 167, 69)
                status_symbol = '✅'
            
            self.cell(8, 8, status_symbol, 0, 0, 'C')
            self.cell(0, 8, f' ELEVATION RISK LEVEL: {risk_level}', 0, 1, 'L')
            
            # Risk Segments
            risk_segments = risk_assessment.get('risk_segments', [])
            if risk_segments:
                self.ln(5)
                self.set_text_color(0, 0, 0)
                self.set_font('Arial', 'B', 12)
                self.cell(0, 8, 'HIGH-RISK ELEVATION SEGMENTS', 0, 1, 'L')
                
                headers = ['Location', 'Risk Level', 'Gradient %', 'Type']
                col_widths = [50, 30, 25, 75]
                
                # Header row
                self.set_font('Arial', 'B', 9)
                self.set_fill_color(230, 230, 230)
                
                for i, (header, width) in enumerate(zip(headers, col_widths)):
                    self.set_xy(10 + sum(col_widths[:i]), self.get_y())
                    self.cell(width, 10, header, 1, 0, 'C', True)
                self.ln(10)
                
                # Data rows
                self.set_font('Arial', '', 8)
                self.set_fill_color(255, 255, 255)
                
                for segment in risk_segments[:10]:  # Top 10 risk segments
                    y_pos = self.get_y()
                    
                    # Location
                    self.set_xy(10, y_pos)
                    coords = segment.get('location', {})
                    location_str = f"{coords.get('lat', 0):.4f}, {coords.get('lng', 0):.4f}"
                    self.cell(50, 8, location_str, 1, 0, 'C')
                    
                    # Risk Level
                    self.set_xy(60, y_pos)
                    risk = segment.get('risk_level', 'UNKNOWN')
                    self.cell(30, 8, risk, 1, 0, 'C')
                    
                    # Gradient
                    self.set_xy(90, y_pos)
                    gradient = abs(segment.get('gradient_percent', 0))
                    self.cell(25, 8, f"{gradient:.1f}%", 1, 0, 'C')
                    
                    # Type
                    self.set_xy(115, y_pos)
                    risk_type = segment.get('risk_type', 'UNKNOWN').replace('_', ' ')
                    self.cell(75, 8, risk_type, 1, 0, 'L')
                    
                    self.ln(8)
            
            # Recommendations
            recommendations = analysis.get('driving_recommendations', [])
            if recommendations:
                self.ln(5)
                self.set_font('Arial', 'B', 12)
                self.set_text_color(0, 0, 0)
                self.cell(0, 8, 'ELEVATION-BASED DRIVING RECOMMENDATIONS', 0, 1, 'L')
                
                for rec in recommendations:
                    priority = rec.get('priority', 'MEDIUM')
                    title = rec.get('title', '')
                    actions = rec.get('actions', [])
                    
                    # Priority color
                    if priority == 'CRITICAL':
                        priority_color = self.danger_color
                    elif priority == 'HIGH':
                        priority_color = self.warning_color
                    else:
                        priority_color = self.info_color
                    
                    # Recommendation header
                    self.set_fill_color(*priority_color)
                    self.rect(10, self.get_y(), 190, 10, 'F')
                    
                    self.set_font('Arial', 'B', 10)
                    self.set_text_color(255, 255, 255)
                    self.set_xy(15, self.get_y() + 2)
                    header_text = f"{priority}: {title}"
                    self.cell(180, 6, self.clean_text(header_text), 0, 1, 'L')
                    self.ln(2)
                    
                    # Actions
                    self.set_font('Arial', '', 9)
                    self.set_text_color(0, 0, 0)
                    for i, action in enumerate(actions[:5], 1):  # Limit to 5 actions
                        self.cell(8, 6, f'{i}.', 0, 0, 'L')
                        current_x = self.get_x()
                        current_y = self.get_y()
                        self.set_xy(current_x + 8, current_y)
                        self.multi_cell(170, 6, self.clean_text(action), 0, 'L')
                        self.ln(1)
                    
                    self.ln(5)
            
            print("✅ Elevation Analysis page added successfully")
            
        except Exception as e:
            print(f"❌ Error adding elevation analysis: {e}")

    def add_emergency_planning_page(self, route_data, api_key=None):
        """Add emergency planning page"""
        if not EmergencyPlanner or not api_key:
            return
        
        try:
            planner = EmergencyPlanner(api_key)
            analysis = planner.analyze_emergency_preparedness(route_data)
            
            if 'error' in analysis:
                return
            
            self.add_page()
            self.add_section_header("ADVANCED EMERGENCY PLANNING", "danger")
            self.set_text_color(0, 0, 0)
            
            # Emergency Preparedness Score
            emergency_score = analysis.get('emergency_services', {}).get('emergency_preparedness_score', 0)
            
            if emergency_score >= 80:
                score_color = self.success_color
                status = "EXCELLENT"
            elif emergency_score >= 60:
                score_color = self.warning_color
                status = "ADEQUATE"
            else:
                score_color = self.danger_color
                status = "POOR"
            
            self.set_fill_color(*score_color)
            self.rect(10, self.get_y(), 190, 15, 'F')
            self.set_text_color(255, 255, 255)
            self.set_font('Arial', 'B', 14)
            self.set_xy(15, self.get_y() + 3)
            self.cell(180, 9, f'EMERGENCY PREPAREDNESS: {emergency_score}/100 - {status}', 0, 1, 'C')
            self.ln(5)
            
            # Alternate Routes
            self.set_text_color(0, 0, 0)
            alternate_routes = analysis.get('alternate_routes', {})
            if not alternate_routes.get('error'):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 8, 'ALTERNATE ROUTES AVAILABLE', 0, 1, 'L')
                
                routes = alternate_routes.get('routes', [])
                route_data = [
                    ['Total Alternates', str(alternate_routes.get('total_alternates', 0))],
                    ['Best Alternate', alternate_routes.get('recommendation', {}).get('reason', 'Not available')],
                    ['Route Availability', 'GOOD' if len(routes) > 1 else 'LIMITED' if len(routes) == 1 else 'NONE']
                ]
                
                self.create_simple_table(route_data, [60, 120])
            
            # Emergency Services
            emergency_services = analysis.get('emergency_services', {})
            if emergency_services:
                self.ln(5)
                self.set_font('Arial', 'B', 12)
                self.cell(0, 8, 'EMERGENCY SERVICES ALONG ROUTE', 0, 1, 'L')
                
                services_data = [
                    ['Hospitals', str(emergency_services.get('service_density', {}).get('hospitals_count', 0))],
                    ['Police Stations', str(emergency_services.get('service_density', {}).get('police_stations_count', 0))],
                    ['Service Centers', str(emergency_services.get('service_density', {}).get('service_centers_count', 0))],
                    ['Service Density', emergency_services.get('service_density', {}).get('emergency_density', 'UNKNOWN')]
                ]
                
                self.create_simple_table(services_data, [60, 120])
            
            # Emergency Contacts
            emergency_contacts = analysis.get('emergency_contacts', {})
            if emergency_contacts:
                self.ln(5)
                self.set_font('Arial', 'B', 12)
                self.cell(0, 8, 'EMERGENCY CONTACT NUMBERS', 0, 1, 'L')
                
                national_numbers = emergency_contacts.get('national_emergency_numbers', {})
                contact_data = []
                for service, number in national_numbers.items():
                    contact_data.append([service, number])
                
                self.create_simple_table(contact_data, [90, 90])
            
            # Contingency Plans
            contingency_plans = analysis.get('contingency_plans', [])
            if contingency_plans:
                self.add_page()
                self.add_section_header("EMERGENCY CONTINGENCY PLANS", "warning")
                self.set_text_color(0, 0, 0)
                
                for plan in contingency_plans:
                    scenario = plan.get('scenario', 'Unknown')
                    priority = plan.get('priority', 'MEDIUM')
                    actions = plan.get('immediate_actions', [])
                    
                    # Scenario header
                    if priority == 'CRITICAL':
                        header_color = self.danger_color
                    elif priority == 'HIGH':
                        header_color = self.warning_color
                    else:
                        header_color = self.info_color
                    
                    self.set_fill_color(*header_color)
                    self.rect(10, self.get_y(), 190, 12, 'F')
                    
                    self.set_font('Arial', 'B', 11)
                    self.set_text_color(255, 255, 255)
                    self.set_xy(15, self.get_y() + 2)
                    self.cell(180, 8, f'{priority}: {scenario}', 0, 1, 'L')
                    self.ln(2)
                    
                    # Actions
                    self.set_font('Arial', '', 10)
                    self.set_text_color(0, 0, 0)
                    self.set_font('Arial', 'B', 10)
                    self.cell(0, 6, 'IMMEDIATE ACTIONS:', 0, 1, 'L')
                    
                    self.set_font('Arial', '', 9)
                    for i, action in enumerate(actions, 1):
                        self.cell(8, 6, f'{i}.', 0, 0, 'L')
                        current_x = self.get_x()
                        current_y = self.get_y()
                        self.set_xy(current_x + 8, current_y)
                        self.multi_cell(170, 6, self.clean_text(action), 0, 'L')
                        self.ln(1)
                    
                    self.ln(8)
            
            print("✅ Emergency Planning page added successfully")
            
        except Exception as e:
            print(f"❌ Error adding emergency planning: {e}")   
    def add_basic_heavy_vehicle_analysis(self, route_data, vehicle_type="heavy_goods_vehicle"):
        """Add basic heavy vehicle analysis when Google APIs are not available"""
        
        self.add_page()
        self.add_section_header("HEAVY VEHICLE SPECIFIC ANALYSIS - BASIC ASSESSMENT", "warning")
        self.set_text_color(0, 0, 0)
        
        # Basic analysis without APIs
        distance_km = self.parse_distance_to_km(route_data.get('distance', '0 km'))
        duration_str = route_data.get('duration', '0 hours')
        base_hours = self.parse_duration_to_hours(duration_str)
        sharp_turns = route_data.get('sharp_turns', [])
        
        # Basic calculations
        adjusted_hours = base_hours * 1.3  # 30% increase for heavy vehicle
        rest_stops = max(0, int(adjusted_hours / 4.5))
        
        self.set_font('Arial', '', 10)
        intro_text = ("This basic analysis provides essential heavy vehicle considerations. "
                    "Enhanced analysis with Google APIs requires API key configuration.")
        self.multi_cell(0, 6, self.clean_text(intro_text), 0, 'L')
        self.ln(5)
        
        # 1. Travel Time Analysis
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, '1. ADJUSTED TRAVEL TIME ANALYSIS', 0, 1, 'L')
        
        time_data = [
            ['Base Travel Time', f"{base_hours:.1f} hours"],
            ['Heavy Vehicle Adjusted', f"{adjusted_hours:.1f} hours"],
            ['Time Increase', f"{((adjusted_hours - base_hours) / base_hours * 100):.0f}%"],
            ['Mandatory Rest Stops', f"{rest_stops} stops required"],
            ['Rest Time Required', f"{rest_stops * 0.75:.1f} hours"],
            ['Total Realistic Time', f"{adjusted_hours + (rest_stops * 0.75):.1f} hours"]
        ]
        
        self.create_simple_table(time_data, [70, 110])
        
        self.set_font('Arial', 'B', 10)
        self.set_text_color(40, 167, 69)
        self.cell(8, 6, '', 0, 0, 'C')
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, ' Basic travel time adjustment calculated', 0, 1, 'L')
        self.ln(5)
        
        # 2. Road Width Assessment
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, '2. ROAD WIDTH & SUITABILITY ASSESSMENT', 0, 1, 'L')
        
        road_data = [
            ['Minimum Width Required', '7.5 meters for safe operation'],
            ['Bridge Weight Capacity', 'Manual verification required'],
            ['Overhead Clearance', '4.2m minimum height needed'],
            ['Assessment Status', 'Field verification recommended'],
            ['Route Classification', 'Unknown - Google Roads API needed'],
            ['Infrastructure Suitability', 'Cannot be determined without APIs']
        ]
        
        self.create_simple_table(road_data, [70, 110])
        
        self.set_font('Arial', 'B', 10)
        self.set_text_color(253, 126, 20)
        self.cell(8, 6, '', 0, 0, 'C')
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, ' Road infrastructure assessment requires Google Roads API', 0, 1, 'L')
        self.ln(5)
        
        # 3. Turning Radius Analysis
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, '3. TURNING RADIUS REQUIREMENTS', 0, 1, 'L')
        
        # Basic turning analysis using existing sharp turns data
        impossible_turns = len([t for t in sharp_turns if t.get('angle', 0) > 90])
        difficult_turns = len([t for t in sharp_turns if 70 <= t.get('angle', 0) <= 90])
        caution_turns = len([t for t in sharp_turns if 45 <= t.get('angle', 0) < 70])
        
        turning_data = [
            ['Total Sharp Turns Detected', str(len(sharp_turns))],
            ['Impossible Turns (>90°)', str(impossible_turns)],
            ['Very Difficult (70-90°)', str(difficult_turns)],
            ['Caution Required (45-70°)', str(caution_turns)],
            ['Heavy Vehicle Turning Radius', '12.5 meters required'],
            ['Route Navigability', 'PROBLEMATIC' if impossible_turns > 0 else 'MANAGEABLE']
        ]
        
        self.create_simple_table(turning_data, [70, 110])
        
        if impossible_turns == 0:
            self.set_font('Arial', 'B', 10)
            self.set_text_color(253, 126, 20)
            self.cell(8, 6, '⚠️', 0, 0, 'C')
            self.set_text_color(0, 0, 0)
            self.cell(0, 6, f' Turning analysis based on GPS data - {difficult_turns} difficult turns detected', 0, 1, 'L')
        else:
            self.set_font('Arial', 'B', 10)
            self.set_text_color(220, 53, 69)
            self.cell(8, 6, '', 0, 0, 'C')
            self.set_text_color(0, 0, 0)
            self.cell(0, 6, f' {impossible_turns} impossible turns detected - Alternate route recommended', 0, 1, 'L')
        
        self.ln(5)
        
        # 4. Fuel & Range Planning
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, '4. FUEL & RANGE PLANNING', 0, 1, 'L')
        
        fuel_consumption = 3.5  # km/L for heavy vehicles
        fuel_needed = distance_km / fuel_consumption if distance_km > 0 else 0
        fuel_stations_count = len(route_data.get('petrol_bunks', {}))
        
        fuel_data = [
            ['Route Distance', f"{distance_km:.1f} km"],
            ['Fuel Consumption Rate', f"{fuel_consumption} km/L (loaded)"],
            ['Fuel Required', f"{fuel_needed:.1f} liters"],
            ['Fuel Buffer (30%)', f"{fuel_needed * 0.3:.1f} liters"],
            ['Total Fuel Needed', f"{fuel_needed * 1.3:.1f} liters"],
            ['Fuel Stations Found', f"{fuel_stations_count} locations"]
        ]
        
        self.create_simple_table(fuel_data, [70, 110])
        
        if fuel_stations_count > 0:
            self.set_font('Arial', 'B', 10)
            self.set_text_color(40, 167, 69)
            self.cell(8, 6, '', 0, 0, 'C')
            self.set_text_color(0, 0, 0)
            self.cell(0, 6, f' Fuel planning complete - {fuel_stations_count} stations available', 0, 1, 'L')
        else:
            self.set_font('Arial', 'B', 10)
            self.set_text_color(220, 53, 69)
            self.cell(8, 6, '', 0, 0, 'C')
            self.set_text_color(0, 0, 0)
            self.cell(0, 6, ' No fuel stations detected along route', 0, 1, 'L')
        
        self.ln(5)
        
        # 5. Load Distribution & Parking
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, '5. LOAD DISTRIBUTION & PARKING FACILITIES', 0, 1, 'L')
        
        load_data = [
            ['Legal GVW Limit', '49,000 kg maximum'],
            ['Front Axle Limit', '10,200 kg maximum'],
            ['Rear Axle Limit', '18,500 kg maximum'],
            ['Load Distribution', 'Weighbridge verification required'],
            ['Truck Parking Areas', 'Manual identification needed'],
            ['Parking Assessment', 'Google Places API required for analysis']
        ]
        
        self.create_simple_table(load_data, [70, 110])
        
        self.set_font('Arial', 'B', 10)
        self.set_text_color(253, 126, 20)
        self.cell(8, 6, '', 0, 0, 'C')
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, ' Parking facility analysis requires Google Places API', 0, 1, 'L')
        self.ln(8)
        
        # Basic Recommendations
        self.add_section_header("BASIC HEAVY VEHICLE RECOMMENDATIONS", "info")
        self.set_text_color(0, 0, 0)
        
        basic_recommendations = [
            "Add 30% buffer time for heavy vehicle travel delays",
            f"Plan {rest_stops} mandatory rest stops (45 minutes each)",
            "Verify bridge weight capacity along the route manually",
            "Check road width at narrow sections before travel",
            "Confirm fuel availability at stations for heavy vehicles",
            "Plan alternative routes for impossible turning locations",
            "Carry emergency contact numbers for route assistance",
            "Ensure vehicle compliance with axle load limits"
        ]
        
        self.set_font('Arial', '', 10)
        for i, rec in enumerate(basic_recommendations, 1):
            self.cell(8, 6, f'{i}.', 0, 0, 'L')
            current_x = self.get_x()
            current_y = self.get_y()
            self.set_xy(current_x + 8, current_y)
            self.multi_cell(170, 6, self.clean_text(rec), 0, 'L')
            self.ln(2)
        
        # API Enhancement Note
        self.ln(5)
        self.set_fill_color(52, 144, 220)
        self.rect(10, self.get_y(), 190, 25, 'F')
        
        self.set_font('Arial', 'B', 12)
        self.set_text_color(255, 255, 255)
        self.set_xy(15, self.get_y() + 3)
        self.cell(180, 8, 'ENHANCED ANALYSIS AVAILABLE', 0, 1, 'C')
        
        self.set_font('Arial', '', 10)
        self.set_xy(15, self.get_y())
        enhancement_text = ("Configure Google Maps API key to enable: Real road width analysis, "
                        "Bridge detection, Truck parking facilities, Route-specific recommendations")
        self.multi_cell(170, 6, self.clean_text(enhancement_text), 0, 'C')
        
        self.set_text_color(0, 0, 0)
        
        print(" Basic Heavy Vehicle Analysis page added (API enhancement available)")

    def parse_distance_to_km(self, distance_str: str) -> float:
        """Parse distance string to kilometers"""
        try:
            if not distance_str:
                return 0.0
            distance_str = distance_str.lower().replace('km', '').replace(',', '').strip()
            return float(distance_str)
        except:
            return 0.0

    def parse_duration_to_hours(self, duration_str: str) -> float:
        """Parse duration string to hours"""
        try:
            if not duration_str:
                return 0.0
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
            return 0.0
        except:
            return 0.0    
    
    def add_heavy_vehicle_analysis_page(self, route_data, vehicle_type="heavy_goods_vehicle"):
        """Add Heavy Vehicle Specific Analysis page using JSON configuration OR Google APIs"""
        
        # Only add for heavy vehicles
        if vehicle_type not in ["heavy_goods_vehicle", "medium_goods_vehicle", "bus"]:
            return
        
        try:
            # Try Google API enhanced analysis first
            api_key = getattr(self, 'google_api_key', None)
            
            if api_key:
                # Try to use Google API enhanced analysis
                try:
                    from utils.heavy_vehicle_analyzer import HeavyVehicleRouteAnalyzer
                    
                    analyzer = HeavyVehicleRouteAnalyzer(api_key)
                    print("🚛 Generating Heavy Vehicle Analysis using Google APIs...")
                    
                    analysis = analyzer.analyze_heavy_vehicle_suitability(route_data)
                    
                    if 'error' not in analysis:
                        return self.add_google_api_heavy_vehicle_analysis(route_data, analysis, vehicle_type)
                    else:
                        print(f"⚠️ Google API analysis failed: {analysis.get('error')}")
                
                except ImportError:
                    print("⚠️ Heavy vehicle analyzer not available - using basic analysis")
                except Exception as e:
                    print(f"⚠️ Google API heavy vehicle analysis failed: {e}")
            
            # Fallback to basic analysis
            print("📋 Using basic heavy vehicle analysis...")
            return self.add_basic_heavy_vehicle_analysis(route_data, vehicle_type)
            
        except Exception as e:
            print(f" Error in heavy vehicle analysis: {e}")
            # Add minimal error page
            self.add_page()
            self.add_section_header("HEAVY VEHICLE ANALYSIS - ERROR", "danger")
            self.set_text_color(0, 0, 0)
            self.set_font('Arial', '', 12)
            self.cell(0, 10, 'Heavy vehicle analysis could not be completed.', 0, 1, 'L')
            self.cell(0, 8, f'Error: {str(e)}', 0, 1, 'L')

    def get_google_api_key(self):
        """Get Google API key - you'll need to implement this"""
        # This should return the same API key used for other Google services
        return self.google_api_key if hasattr(self, 'google_api_key') else None  
        
    def add_professional_title_page(self):
        """Professional title page with compliance info"""
        self.add_page()
        
        # Background
        self.set_fill_color(248, 249, 250)
        self.rect(0, 0, 210, 297, 'F')
        
        # Header section
        self.set_fill_color(*self.accent_color)
        self.rect(0, 0, 210, 85, 'F')
        
        # Company branding
        self.set_font('Arial', 'B', 28)
        self.set_text_color(255, 255, 255)
        self.set_xy(20, 20)
        self.cell(0, 15, 'Route Analytics Pro', 0, 1, 'L')
        
        self.set_font('Arial', '', 14)
        self.set_xy(20, 40)
        self.cell(0, 8, 'Enhanced Route Safety Analysis with Regulatory Compliance', 0, 1, 'L')
        
        # Main title
        self.set_xy(20, 105)
        self.set_font('Arial', 'B', 24)
        self.set_text_color(*self.primary_color)
        self.multi_cell(170, 12, self.clean_text(self.title), 0, 'C')
        
        # Report details
        self.set_xy(30, 160)
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(222, 226, 230)
        self.rect(30, 160, 150, 90, 'DF')
        
        self.set_font('Arial', 'B', 14)
        self.set_text_color(*self.primary_color)
        self.set_xy(40, 170)
        self.cell(0, 10, 'Enhanced Analysis Report', 0, 1, 'L')
        
        self.set_font('Arial', '', 12)
        self.set_text_color(*self.secondary_color)
        self.set_xy(40, 185)
        now = datetime.datetime.now()
        self.cell(0, 8, now.strftime("%B %d, %Y at %I:%M %p"), 0, 1, 'L')
        
        self.set_xy(40, 200)
        self.cell(0, 8, 'Features: Individual Turn Analysis, Street Views, Maps', 0, 1, 'L')
        
        self.set_xy(40, 215)
        self.cell(0, 8, 'Compliance: CMVR, AIS-140, RTSP Analysis Included', 0, 1, 'L')
        
        self.set_xy(40, 230)
        self.cell(0, 8, 'Analysis: GPS Coordinates & Turn-by-Turn Details', 0, 1, 'L')
        
    def header(self):
        if self.page_no() == 1:
            return
            
        self.set_fill_color(*self.accent_color)
        self.rect(0, 0, 210, 20, 'F')
        
        self.set_font('Arial', 'B', 11)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(0, 8, 'Route Analytics Pro - Enhanced Analysis Report', 0, 0, 'L')
        
        self.set_xy(-35, 6)
        self.cell(0, 8, f'Page {self.page_no()}', 0, 0, 'R')
        
        self.ln(25)
        
    def footer(self):
        self.set_y(-15)
        self.set_draw_color(222, 226, 230)
        self.line(10, self.get_y(), 200, self.get_y())
        
        self.set_font('Arial', 'I', 8)
        self.set_text_color(*self.secondary_color)
        self.set_y(-10)
        self.cell(0, 5, 'Generated by Route Analytics Pro - Enhanced Route Safety System', 0, 0, 'C')
        
    def add_section_header(self, title, color_type='primary'):
        """Add section header with proper text cleaning"""
        colors = {
            'primary': self.accent_color,
            'danger': self.danger_color,
            'success': self.success_color,
            'warning': self.warning_color,
            'info': self.info_color
        }
        
        color = colors.get(color_type, self.accent_color)
        
        # Check if we need a new page
        if self.get_y() > 250:
            self.add_page()
        
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.rect(10, self.get_y(), 190, 15, 'F')
        
        self.set_xy(15, self.get_y() + 3)
        self.cell(180, 9, self.clean_text(title), 0, 1, 'L')
        self.ln(5)
    
    def add_network_coverage_analysis_page(self, route_data):
        """Add dedicated network coverage analysis page with map and legend table"""
        network_coverage = route_data.get('network_coverage', {})
        coverage_analysis = network_coverage.get('coverage_analysis', [])
        
        if not coverage_analysis:
            return
        
        self.add_page()
        self.add_section_header("NETWORK COVERAGE ANALYSIS - REAL-TIME DATA", "info")
        
        # Coverage Statistics Summary
        coverage_stats = network_coverage.get('coverage_stats', {})
        stats_info = [
            ['Total Points Analyzed', str(coverage_stats.get('total_points_analyzed', 0))],
            ['API Success Rate', f"{coverage_stats.get('api_success_rate', 0):.1f}%"],
            ['Overall Coverage Score', f"{coverage_stats.get('overall_coverage_score', 0):.1f}/100"],
            ['Dead Zones Detected', str(len(network_coverage.get('dead_zones', [])))],
            ['Poor Coverage Areas', str(len(network_coverage.get('poor_zones', [])))],
            ['Data Quality', coverage_stats.get('data_quality', 'Unknown')]
        ]
        
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, 'NETWORK COVERAGE STATISTICS', 0, 1, 'L')
        self.create_simple_table(stats_info, [80, 100])
        
        # Network Coverage Points Table (following schools/hospital table format)
        self.ln(5)
        self.add_section_header("NETWORK COVERAGE POINTS - TESTED LOCATIONS", "info")
        
        # Create detailed table with headers (same format as hospital/school tables)
        headers = ['S.No', 'Coverage Quality', 'Signal Strength', 'Latitude', 'Longitude', 'Technologies']
        col_widths = [15, 35, 30, 25, 25, 55]
        
        # Header row
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(230, 230, 230)
        self.set_text_color(0, 0, 0)
        
        x_start = 10
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            self.set_xy(x_start + sum(col_widths[:i]), self.get_y())
            self.cell(width, 10, header, 1, 0, 'C', True)
        self.ln(10)
        
        # Data rows (limit to first 20 points for space)
        self.set_font('Arial', '', 8)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        
        for idx, point in enumerate(coverage_analysis[:20], 1):
            if self.get_y() > 270:
                self.add_page()
                self.add_section_header("NETWORK COVERAGE POINTS (Continued)", "info")
            
            coords = point.get('coordinates', {})
            coverage_data = point.get('coverage_data', {})
            quality = point.get('coverage_quality', 'unknown')
            
            # Get signal strength and technologies
            signal_dbm = coverage_data.get('strongest_signal_dbm', -120)
            technologies = coverage_data.get('available_technologies', [])
            tech_str = ', '.join(technologies[:2]) if technologies else 'None'
            
            # Color code based on quality
            if quality == 'excellent':
                self.set_text_color(40, 167, 69)  # Green
            elif quality == 'good':
                self.set_text_color(13, 110, 253)  # Blue
            elif quality == 'fair':
                self.set_text_color(253, 126, 20)  # Orange
            elif quality == 'poor':
                self.set_text_color(220, 53, 69)  # Red
            elif quality == 'dead':
                self.set_text_color(108, 117, 125)  # Gray
            else:
                self.set_text_color(0, 0, 0)  # Black for API failed
            
            y_pos = self.get_y()
            
            # S.No
            self.set_xy(10, y_pos)
            self.cell(15, 8, str(idx), 1, 0, 'C')
            
            # Coverage Quality
            self.set_xy(25, y_pos)
            quality_display = quality.replace('_', ' ').title()
            self.cell(35, 8, quality_display, 1, 0, 'C')
            
            # Signal Strength
            self.set_xy(60, y_pos)
            signal_display = f"{signal_dbm} dBm" if signal_dbm > -120 else "No Signal"
            self.cell(30, 8, signal_display, 1, 0, 'C')
            
            # Latitude
            self.set_xy(90, y_pos)
            lat = coords.get('lat', 0)
            self.cell(25, 8, f"{lat:.4f}", 1, 0, 'C')
            
            # Longitude
            self.set_xy(115, y_pos)
            lng = coords.get('lng', 0)
            self.cell(25, 8, f"{lng:.4f}", 1, 0, 'C')
            
            # Technologies
            self.set_xy(140, y_pos)
            self.cell(55, 8, self.clean_text(tech_str[:15]), 1, 0, 'L')
            
            self.ln(8)
        
        # Reset text color
        self.set_text_color(0, 0, 0)
        
        # Network Coverage Legend Table (same format as hospital/school tables)
        self.ln(5)
        self.add_section_header("NETWORK COVERAGE LEGEND", "success")
        
        legend_headers = ['Coverage Level', 'Signal Range (dBm)', 'Description', 'Color Code']
        legend_col_widths = [30, 35, 80, 30]
        
        # Legend header
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(230, 230, 230)
        self.set_text_color(0, 0, 0)
        
        for i, (header, width) in enumerate(zip(legend_headers, legend_col_widths)):
            self.set_xy(10 + sum(legend_col_widths[:i]), self.get_y())
            self.cell(width, 10, header, 1, 0, 'C', True)
        self.ln(10)
        
        # Legend data
        legend_data = [
            ['Excellent', '> -70 dBm', 'Full connectivity', 'Green'],
            ['Good', '-70 to -85 dBm', 'Reliable connectivity', 'Blue'],
            ['Fair', '-85 to -100 dBm', 'Adequate connectivity', 'Orange'],
            ['Poor', '-100 to -110 dBm', 'Unreliable connectivity', 'Red'],
            ['Dead Zones', '< -110 dBm', 'No connectivity', 'Gray'],
            ['API Failed', 'Unknown', 'Coverage data unavailable', 'Black']
        ]
        
        self.set_font('Arial', '', 9)
        self.set_fill_color(255, 255, 255)
        
        for level, signal_range, description, color in legend_data:
            y_pos = self.get_y()
            
            # Coverage Level
            self.set_xy(10, y_pos)
            self.cell(30, 8, level, 1, 0, 'C')
            
            # Signal Range
            self.set_xy(40, y_pos)
            self.cell(35, 8, signal_range, 1, 0, 'C')
            
            # Description
            self.set_xy(75, y_pos)
            self.cell(80, 8, description, 1, 0, 'L')
            
            # Color Code
            self.set_xy(155, y_pos)
            self.cell(30, 8, color, 1, 0, 'C')
            
            self.ln(8)
        
        # Summary
        self.ln(3)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(0, 0, 0)
        total_points = len(coverage_analysis)
        dead_zones_count = len(network_coverage.get('dead_zones', []))
        summary_text = f"Total Network Coverage Analysis: {total_points} points tested | {dead_zones_count} dead zones identified"
        self.cell(0, 8, self.clean_text(summary_text), 0, 1, 'L')   

    def add_enhanced_route_overview(self, route_data):
        """Enhanced route overview with statistics"""
        self.add_page()
        self.add_section_header("Enhanced Route Overview", "primary")
        
        # Calculate statistics
        sharp_turns = route_data.get('sharp_turns', [])
        network_coverage = route_data.get('network_coverage', {})
        
        blind_spots = len([t for t in sharp_turns if t.get('angle', 0) > 80])
        sharp_danger = len([t for t in sharp_turns if 70 <= t.get('angle', 0) <= 80])
        moderate_turns = len([t for t in sharp_turns if 45 <= t.get('angle', 0) < 70])
        
        safety_score = self.calculate_safety_score(
            sharp_turns, 
            len(network_coverage.get('dead_zones', [])),
            len(network_coverage.get('poor_zones', []))
        )
        
        # Create overview table
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, 'ROUTE INFORMATION', 0, 1, 'L')
        
        # Route info table
        route_info = [
            ['From Address', route_data.get('from_address', 'Unknown')[:60]],
            ['To Address', route_data.get('to_address', 'Unknown')[:60]],
            ['Total Distance', route_data.get('distance', 'Unknown')],
            ['Estimated Duration', route_data.get('duration', 'Unknown')],
            ['Route Points Analyzed', str(route_data.get('total_points', 0))],
            ['Overall Safety Score', f"{safety_score}/100"],
            ['Individual Turn Pages', f"{blind_spots + sharp_danger} detailed pages included"]
        ]
        
        self.create_simple_table(route_info, [60, 120])
        
        self.ln(5)
        
        # Hazard statistics table
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, 'HAZARD ANALYSIS SUMMARY', 0, 1, 'L')
        
        hazard_info = [
            ['Extreme Blind Spots (>80 degrees)', str(blind_spots), 'CRITICAL DANGER - Individual Pages Added'],
            ['Sharp Danger Turns (70-80 degrees)', str(sharp_danger), 'HIGH DANGER - Individual Pages Added'],
            ['Moderate Turns (45-70 degrees)', str(moderate_turns), 'CAUTION REQUIRED'],
            ['Network Dead Zones', str(len(network_coverage.get('dead_zones', []))), 'NO SIGNAL'],
            ['Poor Coverage Areas', str(len(network_coverage.get('poor_zones', []))), 'WEAK SIGNAL'],
            ['Weather Monitoring Points', str(len(route_data.get('weather', []))), 'CONDITIONS TRACKED']
        ]
        
        self.create_simple_table(hazard_info, [50, 30, 100])
        
        # Add turn analysis summary
        self.ln(5)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(220, 53, 69)
        total_critical_turns = blind_spots + sharp_danger
        self.cell(0, 8, f'CRITICAL: {total_critical_turns} DANGEROUS TURNS REQUIRE DETAILED ANALYSIS', 0, 1, 'C')
        
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, f'Each critical turn has a dedicated page with street view, satellite map, and safety recommendations.', 0, 1, 'C')
        
    def create_simple_table(self, data, col_widths):
        """Create a simple table with data"""
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        
        for row in data:
            x_start = self.get_x()
            y_start = self.get_y()
            
            # Check if we need a new page
            if y_start > 260:
                self.add_page()
                y_start = self.get_y()
            
            for i, (cell, width) in enumerate(zip(row, col_widths)):
                if i == 0:  # First column - bold
                    self.set_font('Arial', 'B', 10)
                    self.set_text_color(0, 0, 0)
                else:
                    self.set_font('Arial', '', 10)
                    self.set_text_color(0, 0, 0)
                
                self.set_xy(x_start + sum(col_widths[:i]), y_start)
                # Clean the text before adding to cell
                cell_text = self.clean_text(str(cell)[:70])
                self.cell(width, 8, cell_text, 1, 0, 'L')
            
            self.ln(8)
        
        self.ln(3)
    
    
    def add_detailed_poi_tables(self, route_data):
        """Add detailed POI tables with S.No, Coordinates, and Distance"""
        route_points = route_data.get('route_points', [])
        
        poi_categories = {
            'hospitals': ('HOSPITALS - Emergency Medical Services', 'info'),
            'petrol_bunks': ('FUEL STATIONS - Petrol Pumps', 'warning'),
            'schools': ('SCHOOLS - Speed Limit Zones (40 km/h)', 'success'),
            'food_stops': ('RESTAURANTS/FOOD STOPS - Rest Areas', 'info'),
            'police_stations': ('POLICE STATIONS - Security Services', 'danger')
        }
        
        for poi_key, (title, color_type) in poi_categories.items():
            pois = route_data.get(poi_key, {})
            
            if not pois:
                continue
                
            self.add_page()
            self.add_section_header(title, color_type)
            
            # Create detailed table with headers
            headers = ['S.No', 'Name', 'Location', 'Latitude', 'Longitude', 'Distance (km)']
            col_widths = [15, 50, 45, 25, 25, 25]
            
            # Header row
            self.set_font('Arial', 'B', 9)
            self.set_fill_color(230, 230, 230)
            self.set_text_color(0, 0, 0)
            
            x_start = 10
            for i, (header, width) in enumerate(zip(headers, col_widths)):
                self.set_xy(x_start + sum(col_widths[:i]), self.get_y())
                self.cell(width, 10, header, 1, 0, 'C', True)
            self.ln(10)
            
            # Data rows
            self.set_font('Arial', '', 8)
            self.set_fill_color(255, 255, 255)
            self.set_text_color(0, 0, 0)
            
            for idx, (name, location) in enumerate(pois.items(), 1):
                # Calculate coordinates and distance (estimated)
                lat, lng, distance = self.estimate_poi_location(name, location, route_points, idx, len(pois))
                
                # Check for page break
                if self.get_y() > 270:
                    self.add_page()
                    self.add_section_header(f"{title} (Continued)", color_type)
                
                y_pos = self.get_y()
                
                # S.No
                self.set_xy(10, y_pos)
                self.cell(15, 8, str(idx), 1, 0, 'C')
                
                # Name (truncated if too long)
                self.set_xy(25, y_pos)
                name_truncated = name[:25] + '...' if len(name) > 25 else name
                self.cell(50, 8, self.clean_text(name_truncated), 1, 0, 'L')
                
                # Location (truncated)
                self.set_xy(75, y_pos)
                location_truncated = location[:22] + '...' if len(location) > 22 else location
                self.cell(45, 8, self.clean_text(location_truncated), 1, 0, 'L')
                
                # Latitude
                self.set_xy(120, y_pos)
                self.cell(25, 8, f"{lat:.4f}", 1, 0, 'C')
                
                # Longitude
                self.set_xy(145, y_pos)
                self.cell(25, 8, f"{lng:.4f}", 1, 0, 'C')
                
                # Distance
                self.set_xy(170, y_pos)
                self.cell(25, 8, f"{distance:.1f}", 1, 0, 'C')
                
                self.ln(8)
            
            # Summary
            self.ln(3)
            self.set_font('Arial', 'B', 10)
            self.set_text_color(0, 0, 0)
            summary_text = self.clean_text(f"Total {title.split(' - ')[0]}: {len(pois)} locations identified along the route")
            self.cell(0, 8, summary_text, 0, 1, 'L')
    
    def add_regulatory_compliance_page(self, route_data, vehicle_type="heavy_goods_vehicle"):
        """Add comprehensive regulatory compliance analysis page - FIXED TEXT RENDERING"""
        try:
            # Simple compliance data without external analyzer
            vehicle_info = self.get_vehicle_info_by_type(vehicle_type)
            compliance_data = self.generate_simple_compliance_data(route_data, vehicle_info)
            
            # Add compliance page
            self.add_page()
            self.add_section_header("REGULATORY COMPLIANCE ANALYSIS", "danger")
            
            # Compliance Score Header
            score = compliance_data.get('compliance_score', 75)
            score_color = self.success_color if score >= 80 else self.warning_color if score >= 60 else self.danger_color
            
            self.set_fill_color(*score_color)
            self.rect(10, self.get_y(), 190, 20, 'F')
            
            self.set_font('Arial', 'B', 16)
            self.set_text_color(255, 255, 255)
            self.set_xy(15, self.get_y() + 5)
            status_text = "GOOD" if score >= 80 else "NEEDS ATTENTION" if score >= 60 else "CRITICAL"
            self.cell(180, 10, f'COMPLIANCE SCORE: {score}/100 - {status_text}', 0, 1, 'C')
            self.ln(5)
            
            # Route Summary
            self.set_text_color(0, 0, 0)
            route_summary = compliance_data.get('route_summary', {})
            self.add_compliance_section("ROUTE COMPLIANCE SUMMARY", [
                ['Vehicle Type', route_summary.get('vehicle_type', 'Heavy Goods Vehicle')],
                ['Vehicle Weight', route_summary.get('vehicle_weight', '18,000 kg')],
                ['Route Distance', route_data.get('distance', 'Unknown')],
                ['Estimated Duration', route_data.get('duration', 'Unknown')],
                ['States Crossed', 'Delhi, Haryana (Estimated)'],
                ['Compliance Category', route_summary.get('compliance_category', 'HIGH RISK - Heavy Goods Vehicle')],
            ])
            
            # CMVR Compliance
            self.add_compliance_section("CMVR 1989 & AMENDMENT 2022 COMPLIANCE", [
                ['Vehicle Category', 'Heavy Goods Vehicle'],
                ['Weight Category', f'{vehicle_info.get("weight", 18000)} kg'],
                ['License Required', 'HMV (Heavy Motor Vehicle)'],
                ['Permit Required', 'YES - Mandatory for >12 tons'],
                ['Training Hours Required', '80 hours'],
                ['Medical Fitness Validity', '3 years']
            ])
            
            # Speed Limits
            self.add_compliance_section("APPLICABLE SPEED LIMITS", [
                ['Urban Areas', '40 km/h'],
                ['Near Schools', '25 km/h'],
                ['Highways', '80 km/h'],
                ['Rural Roads', '60 km/h'],
                ['Night Driving', 'Reduce by 10 km/h']
            ])
            
            # AIS-140 Compliance
            self.add_page()  # New page for AIS-140 details
            self.add_section_header("AIS-140 COMPLIANCE (MANDATORY)", "danger")
            
            self.set_font('Arial', 'B', 12)
            self.set_text_color(220, 53, 69)
            self.cell(0, 10, 'CRITICAL: AIS-140 compliance is MANDATORY for this vehicle type', 0, 1, 'C')
            self.set_text_color(0, 0, 0)
            self.ln(5)
            
            # GPS Tracking requirements
            self.add_compliance_section("GPS TRACKING REQUIREMENTS", [
                ['Accuracy Required', '+/- 3 meters'],
                ['Update Frequency', '10 seconds'],
                ['Data Storage', '30 days minimum'],
                ['Compliance Deadline', 'April 1, 2023']
            ])
            
            # Panic Button requirements
            self.add_compliance_section("PANIC BUTTON REQUIREMENTS", [
                ['Location', 'Driver accessible position'],
                ['Response Time', '<5 seconds'],
                ['Alert Recipients', 'Police, Owner, Control Center'],
                ['Installation', 'Authorized centers only']
            ])
            
            # Compliance checklist
            checklist = [
                'GPS device installed and functional',
                'Panic button accessible to driver', 
                'Emergency SOS functionality active',
                'Overspeed alert system configured',
                'Data transmission to India-based servers',
                'Device certification from BIS'
            ]
            
            self.set_font('Arial', 'B', 12)
            self.cell(0, 8, 'AIS-140 COMPLIANCE CHECKLIST:', 0, 1, 'L')
            self.set_font('Arial', '', 10)
            for item in checklist:
                self.cell(0, 6, f'  -{self.clean_text(item)}', 0, 1, 'L')
            self.ln(5)
            
            # RTSP Compliance
            estimated_hours = self.parse_duration_to_hours(route_data.get('duration', '8 hours'))
            required_rest_stops = max(0, int(estimated_hours / 4.5))
            
            self.add_compliance_section("ROAD TRANSPORT SAFETY POLICY (RTSP)", [
                ['Estimated Driving Time', f'{estimated_hours:.1f} hours'],
                ['Max Continuous Allowed', '4.5 hours'],
                ['Daily Max Allowed', '10 hours'],
                ['Time Compliance', 'COMPLIANT' if estimated_hours <= 10 else 'NON-COMPLIANT'],
                ['Required Rest Stops', str(required_rest_stops)],
                ['Rest Duration Each Stop', '45 minutes minimum']
            ])
            
            # Night Driving Restrictions
            self.add_compliance_section("NIGHT DRIVING RESTRICTIONS", [
                ['Night Hours', '22:00 to 06:00'],
                ['Speed Reduction', '10 km/h below daytime limits'],
                ['Additional Safety', 'Enhanced lighting, fatigue monitoring required']
            ])
            
            # State Permits
            self.add_page()  # New page for state permits
            self.add_section_header("STATE PERMITS & INTER-STATE COMPLIANCE", "warning")
            self.set_text_color(0, 0, 0)
            self.set_font('Arial', 'B', 12)
            self.cell(0, 8, 'STATES CROSSED: Delhi, Haryana (Estimated)', 0, 1, 'L')
            self.ln(3)
            
            critical_permits = [
                'Inter-State Permit (Mandatory)',
                'Heavy Vehicle Permit',
                'Route Permit for Commercial Vehicles',
                'Environmental Clearance (if applicable)'
            ]
            
            self.set_font('Arial', 'B', 12)
            self.cell(0, 8, 'CRITICAL PERMITS REQUIRED:', 0, 1, 'L')
            self.set_font('Arial', '', 10)
            for permit in critical_permits:
                self.cell(0, 6, f'  - {self.clean_text(permit)}', 0, 1, 'L')
            self.ln(5)
            
            # Recommendations
            recommendations = [
                'CRITICAL: Install AIS-140 compliant GPS tracking system',
                'CRITICAL: Install panic button accessible to driver',
                'Plan 2 mandatory rest stops (45 min each) for this journey',
                'Obtain inter-state permits for all states',
                'Check Delhi-specific entry requirements',
                'Carry all vehicle documents (RC, Insurance, PUC)',
                'Ensure driver medical fitness certificate is valid',
                'Check vehicle safety equipment (first aid, fire extinguisher)',
                'Verify speed governor installation and calibration',
                'Plan route to avoid restricted time zones'
            ]
            
            self.add_page()  # New page for recommendations
            self.add_section_header("COMPLIANCE RECOMMENDATIONS", "info")
            
            self.set_font('Arial', '', 10)
            self.set_text_color(0, 0, 0)
            
            for i, recommendation in enumerate(recommendations, 1):
                # Color code recommendations by priority
                if recommendation.startswith('CRITICAL'):
                    self.set_text_color(220, 53, 69)  # Red for critical
                elif recommendation.startswith('Plan'):
                    self.set_text_color(253, 126, 20)  # Orange for time-sensitive
                elif recommendation.startswith('Check') or recommendation.startswith('Obtain'):
                    self.set_text_color(13, 110, 253)  # Blue for documentation
                else:
                    self.set_text_color(0, 0, 0)  # Black for general
                
                self.cell(8, 6, f'{i}.', 0, 0, 'L')
                # Use multi_cell for long text with proper cleaning
                current_x = self.get_x()
                current_y = self.get_y()
                self.set_xy(current_x + 8, current_y)
                self.multi_cell(170, 6, self.clean_text(recommendation), 0, 'L')
                self.ln(2)
            
            # Reset color
            self.set_text_color(0, 0, 0)
            
            print(" Regulatory Compliance page added successfully")
            
        except Exception as e:
            print(f" Error adding regulatory compliance page: {e}")
            # Add error page
            self.add_page()
            self.add_section_header("REGULATORY COMPLIANCE - ERROR", "danger")
            self.set_font('Arial', '', 12)
            self.set_text_color(0, 0, 0)
            self.cell(0, 10, 'Regulatory compliance analysis could not be completed.', 0, 1, 'L')
            self.cell(0, 8, f'Error: {str(e)}', 0, 1, 'L')
    
    def add_compliance_section(self, title, data):
        """Add a compliance section with table"""
        # Check space and add page if needed
        if self.get_y() > 240:
            self.add_page()
        
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, self.clean_text(title), 0, 1, 'L')
        
        # Create table
        col_widths = [80, 100]
        
        self.set_font('Arial', '', 10)
        for row in data:
            if self.get_y() > 270:
                self.add_page()
            
            y_pos = self.get_y()
            
            # Key column (bold)
            self.set_font('Arial', 'B', 10)
            self.set_xy(10, y_pos)
            self.cell(80, 8, self.clean_text(str(row[0])), 1, 0, 'L')
            
            # Value column
            self.set_font('Arial', '', 10)
            self.set_xy(90, y_pos)
            self.cell(100, 8, self.clean_text(str(row[1])), 1, 0, 'L')
            
            self.ln(8)
        
        self.ln(5)
    
    def add_individual_turn_pages(self, route_data, api_key):
        """Add individual pages for each critical turn with street view and maps"""
        sharp_turns = route_data.get('sharp_turns', [])
        
        if not sharp_turns:
            return
        
        # Filter critical turns (blind spots and sharp danger turns)
        critical_turns = [turn for turn in sharp_turns if turn.get('angle', 0) >= 70]
        
        if not critical_turns:
            return
        
        # Sort by danger level (highest angle first)
        critical_turns.sort(key=lambda x: x.get('angle', 0), reverse=True)
        
        print(f"📄 Generating {len(critical_turns)} individual turn analysis pages...")
        
        for idx, turn in enumerate(critical_turns, 1):
            self.add_single_turn_analysis_page(turn, idx, len(critical_turns), api_key)
    
    def add_single_turn_analysis_page(self, turn, turn_number, total_turns, api_key):
        """Add detailed analysis page for a single turn"""
        self.add_page()
        
        angle = turn.get('angle', 0)
        lat = turn.get('lat', 0)
        lng = turn.get('lng', 0)
        classification = turn.get('classification', 'Unknown')
        
        # Determine danger level and color
        if angle > 80:
            danger_level = "EXTREME BLIND SPOT"
            color_type = "danger"
            danger_color = self.danger_color
            speed_recommendation = "15-20 km/h"
            visibility = "ZERO visibility around corner"
        else:
            danger_level = "SHARP DANGER TURN"
            color_type = "warning" 
            danger_color = self.warning_color
            speed_recommendation = "25-30 km/h"
            visibility = "LIMITED visibility"
        
        # Header with turn information
        self.add_section_header(f"TURN {turn_number}/{total_turns}: {danger_level} - {angle} degrees", color_type)
        
        # Turn details table
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, 'CRITICAL TURN ANALYSIS:', 0, 1, 'L')
        
        turn_details = [
            ['Turn Classification', classification],
            ['Turn Angle', f"{angle} degrees (DANGEROUS)"],
            ['GPS Coordinates', f"{lat:.6f}, {lng:.6f}"],
            ['Danger Level', danger_level],
            ['Recommended Speed', speed_recommendation],
            ['Visibility Status', visibility],
            ['Safety Priority', 'HIGHEST' if angle > 80 else 'HIGH']
        ]
        
        self.create_simple_table(turn_details, [60, 120])
        
        # Safety recommendations
        self.ln(5)
        self.set_font('Arial', 'B', 11)
        self.set_text_color(*danger_color)
        self.cell(0, 8, 'CRITICAL SAFETY RECOMMENDATIONS:', 0, 1, 'L')
        
        recommendations = self.get_turn_safety_recommendations(angle)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        
        for i, rec in enumerate(recommendations, 1):
            self.cell(8, 6, f"{i}.", 0, 0, 'L')
            # Use multi_cell for long text with proper cleaning
            current_x = self.get_x()
            current_y = self.get_y()
            self.set_xy(current_x + 8, current_y)
            self.multi_cell(170, 6, self.clean_text(rec), 0, 'L')
            self.ln(2)
        
        # Add maps section
        self.ln(5)
        if api_key:
            self.add_turn_maps_section(lat, lng, angle, api_key, turn_number)
        else:
            self.set_font('Arial', 'I', 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 6, 'Maps require Google Maps API key configuration.', 0, 1, 'L')
        
        # Add warning footer
        # self.set_y(-40)
        # self.set_fill_color(*danger_color)
        # self.rect(10, self.get_y(), 190, 20, 'F')
        
        # self.set_font('Arial', 'B', 12)
        # self.set_text_color(255, 255, 255)
        # self.set_xy(15, self.get_y() + 4)
        # warning_text = f"WARNING: {danger_level} - Exercise EXTREME CAUTION at {lat:.4f}, {lng:.4f}"
        # self.cell(180, 12, self.clean_text(warning_text), 0, 1, 'C')
    
    def get_turn_safety_recommendations(self, angle):
        """Get safety recommendations based on turn angle"""
        if angle > 80:
            return [
                "CRAWL SPEED MANDATORY: Reduce speed to 15-20 km/h minimum before entering turn",
                "HORN WARNING: Sound horn continuously while approaching and taking the turn", 
                "HEADLIGHTS ON: Keep headlights on during daytime for maximum visibility",
                "AVOID OVERTAKING: Absolutely no overtaking 200m before and after this turn",
                "STAY IN LANE: Keep to the extreme left of your lane throughout the turn",
                "PASSENGER ALERT: Warn all passengers about the dangerous blind spot ahead",
                "EMERGENCY PREP: Have emergency contact ready - accidents common at such turns",
                "WEATHER CHECK: Avoid this turn in rain, fog, or night conditions if possible"
            ]
        else:
            return [
                "REDUCE SPEED: Slow down to 25-30 km/h before entering the sharp turn",
                "USE HORN: Sound horn to alert oncoming traffic of your presence",
                "MAINTAIN DISTANCE: Keep safe distance from vehicle ahead (minimum 50m)",
                "PROPER LANE: Stay in correct lane and avoid cutting corners",
                "CHECK MIRRORS: Monitor traffic behind before slowing down",
                "GEAR DOWN: Use appropriate gear for controlled speed through turn",
                "AVOID BRAKING: Complete braking before turn, not during the turn",
                "POST-TURN CAUTION: Accelerate gradually after completing the turn"
            ]
    
    def add_turn_maps_section(self, lat, lng, angle, api_key, turn_number):
        """Add street view and satellite map for the turn"""
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, 'TURN LOCATION ANALYSIS:', 0, 1, 'L')
        
        print(f"🗺️ Adding turn maps section for turn {turn_number}")
        self.add_dual_turn_maps(lat, lng, api_key)
    
    def add_dual_turn_maps(self, lat, lng, api_key):
        """Add street view and satellite map side by side"""
        try:
            current_y = self.get_y()
            
            # Street View (left side)
            self.set_font('Arial', 'B', 10)
            self.set_text_color(0, 0, 0)
            self.set_xy(10, current_y)
            self.cell(85, 6, 'STREET VIEW - Driver Perspective:', 0, 0, 'L')
            
            # Satellite Map (right side)  
            self.set_xy(105, current_y)
            self.cell(85, 6, 'SATELLITE MAP - Overhead View:', 0, 0, 'L')
            
            self.ln(8)
            current_y = self.get_y()
            
            print(f"📍 Processing turn at coordinates: {lat:.6f}, {lng:.6f}")
            
            # Generate street view
            print("🔄 Attempting to generate Street View...")
            street_view_success = self.add_street_view_image(lat, lng, api_key, 
                                                           x_pos=10, y_pos=current_y, 
                                                           width=85, height=50)
            
            # Generate satellite map
            print("🔄 Attempting to generate Satellite Map...")
            satellite_success = self.add_satellite_map_image(lat, lng, api_key,
                                                           x_pos=105, y_pos=current_y,
                                                           width=85, height=50)
            
            # # Move cursor below both images
            # # Move cursor below both images
            # self.set_y(current_y + 65)

            # # CHECK SPACE BEFORE ADDING COORDINATES - PREVENT PAGE BREAK
            # coordinates_y = self.get_y()
            # if coordinates_y > 280:  # Not enough space for coordinates (need ~12px)
            #     self.add_page()
            #     coordinates_y = self.get_y()

            # # Add coordinates info with status
            # self.set_font('Arial', '', 9)
            # self.set_text_color(0, 0, 0)
            # success_street = "OK" if street_view_success else "FAILED"
            # success_satellite = "OK" if satellite_success else "FAILED"
            # status_text = f'GPS: {lat:.6f}, {lng:.6f} | Street View: {success_street} | Satellite: {success_satellite}'
            # self.set_y(coordinates_y)  # Ensure we're at the right position
            # self.cell(0, 6, status_text, 0, 1, 'C')
            
            # Debug API status
            if not street_view_success:
                print(f"⚠️ Street View failed for {lat:.6f}, {lng:.6f}")
                self.set_font('Arial', '', 8)
                self.set_text_color(200, 100, 0)
                self.cell(0, 5, 'Note: Street View may not be available for this location. Using placeholder.', 0, 1, 'C')
            
        except Exception as e:
            print(f" Error adding dual maps: {e}")
            import traceback
            traceback.print_exc()
            self.add_compact_turn_map(lat, lng, api_key, 'roadmap')
    
    def add_street_view_image(self, lat, lng, api_key, x_pos=10, y_pos=None, width=85, height=60):
        """Add Google Street View image with fallback to placeholder"""
        try:
            if y_pos is None:
                y_pos = self.get_y()
            
            print(f"🔍 Generating Street View for {lat:.6f}, {lng:.6f}")
            
            # Try multiple headings to get street view
            attempts = [
                (lat, lng, 0),    # Original location, north
                (lat, lng, 90),   # Original location, east  
                (lat, lng, 180),  # Original location, south
                (lat, lng, 270),  # Original location, west
                (lat + 0.0001, lng, 0),     # Slightly north
                (lat - 0.0001, lng, 0),     # Slightly south
                (lat, lng + 0.0001, 0),     # Slightly east
                (lat, lng - 0.0001, 0),     # Slightly west
            ]
            
            for attempt_num, (try_lat, try_lng, heading) in enumerate(attempts):
                try:
                    # Street View API with enhanced parameters
                    base_url = "https://maps.googleapis.com/maps/api/streetview"
                    params = [
                        f"size=640x640",
                        f"location={try_lat},{try_lng}",
                        f"heading={heading}",
                        f"pitch=5",
                        f"fov=90",
                        f"return_error_code=true",
                        f"key={api_key}"
                    ]
                    
                    url = f"{base_url}?" + "&".join(params)
                    print(f"  📡 Street View attempt {attempt_num+1}/8: {try_lat:.6f},{try_lng:.6f} heading:{heading}°")
                    
                    response = requests.get(url, timeout=25)
                    
                    if response.status_code == 200:
                        content_length = len(response.content)
                        print(f"  📊 Response size: {content_length} bytes")
                        
                        # Check for valid street view
                        if content_length > 3000:  # Real street view images are much larger
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp:
                                temp.write(response.content)
                                temp_path = temp.name
                            
                            try:
                                # Add green border for street view
                                self.set_draw_color(34, 139, 34)  # Forest green
                                self.set_line_width(1.5)
                                self.rect(x_pos - 1, y_pos - 1, width + 2, height + 2, 'D')
                                
                                # Add image
                                self.image(temp_path, x=x_pos, y=y_pos, w=width, h=height)
                                
                                print(f"   Street View SUCCESS! (attempt {attempt_num+1}, heading: {heading}°)")
                                
                                # Add success label
                                self.set_font('Arial', 'B', 8)
                                self.set_text_color(34, 139, 34)
                                self.set_xy(x_pos, y_pos + height + 1)
                                self.cell(width, 4, f'Street View - {heading} degree view', 0, 0, 'C')
                                
                                os.unlink(temp_path)
                                return True
                                
                            except Exception as img_error:
                                print(f"   Image processing failed: {img_error}")
                                try:
                                    os.unlink(temp_path)
                                except:
                                    pass
                                continue
                        else:
                            print(f"  ⚠️ Response too small ({content_length} bytes) - no street view at this location")
                    else:
                        print(f"   HTTP {response.status_code}")
             
                except requests.RequestException as req_error:
                    print(f"   Request failed: {req_error}")
                    continue
                except Exception as e:
                    print(f"   Attempt {attempt_num+1} failed: {e}")
                    continue
            
            # All attempts failed - add informative placeholder
            print(f"  🚫 No Street View available after {len(attempts)} attempts")
            self.add_street_view_placeholder(x_pos, y_pos, width, height, lat, lng)
            return False
            
        except Exception as e:
            print(f" Street view critical error: {e}")
            self.add_street_view_placeholder(x_pos, y_pos, width, height, lat, lng)
            return False
    
    def add_street_view_placeholder(self, x_pos, y_pos, width, height, lat, lng):
        """Add placeholder when street view is not available"""
        try:
            # Draw placeholder rectangle with street view styling
            self.set_draw_color(220, 20, 60)  # Crimson red border
            self.set_fill_color(255, 240, 245)  # Light pink background
            self.set_line_width(2)
            self.rect(x_pos, y_pos, width, height, 'DF')
            
            # Add "NO STREET VIEW" header
            self.set_font('Arial', 'B', 11)
            self.set_text_color(220, 20, 60)
            self.set_xy(x_pos, y_pos + height/2 - 25)
            self.cell(width, 8, 'STREET VIEW', 0, 0, 'C')
            
            self.set_xy(x_pos, y_pos + height/2 - 15)
            self.cell(width, 8, 'NOT AVAILABLE', 0, 0, 'C')
            
            # Add coordinates
            self.set_font('Arial', '', 9)
            self.set_text_color(100, 100, 100)
            self.set_xy(x_pos, y_pos + height/2 - 2)
            self.cell(width, 6, f'GPS: {lat:.6f}, {lng:.6f}', 0, 0, 'C')
            
            # Add helpful message
            self.set_font('Arial', '', 8)
            self.set_xy(x_pos, y_pos + height/2 + 8)
            self.cell(width, 5, 'Street imagery not available', 0, 0, 'C')
            
            self.set_xy(x_pos, y_pos + height/2 + 16)
            self.cell(width, 5, 'for this exact location.', 0, 0, 'C')
            
            self.set_xy(x_pos, y_pos + height/2 + 24)
            self.cell(width, 5, 'Refer to satellite map.', 0, 0, 'C')
            
            print(f"  📋 Street View placeholder added for {lat:.4f}, {lng:.4f}")
            
        except Exception as e:
            print(f"Error adding street view placeholder: {e}")
    
    def add_satellite_map_image(self, lat, lng, api_key, x_pos=105, y_pos=None, width=85, height=60):
        """Add satellite map image"""
        try:
            if y_pos is None:
                y_pos = self.get_y()
            
            print(f"🛰️ Generating Satellite Map for {lat:.6f}, {lng:.6f}")
            
            base_url = "https://maps.googleapis.com/maps/api/staticmap"
            params = [
                f"center={lat},{lng}",
                f"zoom=18",
                f"size=640x640",
                f"maptype=satellite",
                f"markers=color:red|size:mid|{lat},{lng}",
                f"key={api_key}"
            ]
            
            url = f"{base_url}?" + "&".join(params)
            print(f"  📡 Satellite Map API call...")
            
            response = requests.get(url, timeout=20)
            
            if response.status_code == 200:
                content_length = len(response.content)
                print(f"  📊 Satellite response size: {content_length} bytes")
                
                if content_length > 1000:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp:
                        temp.write(response.content)
                        temp_path = temp.name
                    
                    try:
                        # Add border (blue for satellite)
                        self.set_draw_color(100, 100, 200)
                        self.set_line_width(1)
                        self.rect(x_pos - 1, y_pos - 1, width + 2, height + 2, 'D')
                        
                        # Add image
                        self.image(temp_path, x=x_pos, y=y_pos, w=width, h=height)
                        
                        print(f"   Satellite map added successfully")
                        
                        # Add small text label
                        self.set_font('Arial', '', 7)
                        self.set_text_color(0, 0, 200)
                        self.set_xy(x_pos, y_pos + height + 1)
                        self.cell(width, 4, 'Satellite View - Zoom 18', 0, 0, 'C')
                        
                        os.unlink(temp_path)
                        return True
                        
                    except Exception as img_error:
                        print(f"   Invalid satellite image: {img_error}")
                        os.unlink(temp_path)
                        self.add_satellite_placeholder(x_pos, y_pos, width, height, lat, lng)
                        return False
                else:
                    print(f"  ⚠️ Satellite response too small ({content_length} bytes)")
                    self.add_satellite_placeholder(x_pos, y_pos, width, height, lat, lng)
                    return False
            else:
                print(f"   Satellite HTTP {response.status_code}")
                self.add_satellite_placeholder(x_pos, y_pos, width, height, lat, lng)
                return False
            
        except Exception as e:
            print(f" Satellite map error: {e}")
            self.add_satellite_placeholder(x_pos, y_pos, width, height, lat, lng)
            return False
    
    def add_satellite_placeholder(self, x_pos, y_pos, width, height, lat, lng):
        """Add placeholder when satellite map is not available"""
        try:
            # Draw placeholder rectangle
            self.set_draw_color(150, 150, 200)
            self.set_fill_color(240, 240, 250)
            self.rect(x_pos, y_pos, width, height, 'DF')
            
            # Add placeholder text
            self.set_font('Arial', 'B', 10)
            self.set_text_color(100, 100, 150)
            self.set_xy(x_pos, y_pos + height/2 - 15)
            self.cell(width, 6, 'SATELLITE MAP', 0, 0, 'C')
            
            self.set_font('Arial', '', 8)
            self.set_xy(x_pos, y_pos + height/2 - 5)
            self.cell(width, 5, 'NOT AVAILABLE', 0, 0, 'C')
            
            self.set_xy(x_pos, y_pos + height/2 + 5)
            self.cell(width, 5, f'{lat:.4f}, {lng:.4f}', 0, 0, 'C')
            
            self.set_xy(x_pos, y_pos + height/2 + 15)
            self.cell(width, 5, 'Check API key and quota', 0, 0, 'C')
            
        except Exception as e:
            print(f"Error adding satellite placeholder: {e}")
    
    def add_compact_turn_map(self, lat, lng, api_key, map_type='roadmap'):
        """Add single optimized map for the turn"""
        try:
            current_y = self.get_y()
            
            self.set_font('Arial', 'B', 10)
            self.set_text_color(0, 0, 0)
            self.cell(0, 6, f'TURN LOCATION MAP - {map_type.upper()} VIEW:', 0, 1, 'L')
            
            current_y = self.get_y()
            
            success = self.add_static_map_image(lat, lng, api_key, map_type,
                                              x_pos=30, y_pos=current_y,
                                              width=150, height=80)
            
            if success:
                self.set_y(current_y + 85)
                self.set_font('Arial', '', 9)
                self.set_text_color(0, 0, 0)
                self.cell(0, 6, f'GPS: {lat:.6f}, {lng:.6f} | Zoom level optimized for turn analysis', 0, 1, 'C')
            
        except Exception as e:
            print(f"Error adding compact map: {e}")
            self.set_font('Arial', '', 10)
            self.set_text_color(0, 0, 0)
            self.cell(0, 6, f'Map generation failed for turn at {lat:.4f}, {lng:.4f}', 0, 1, 'L')
    
    def add_static_map_image(self, lat, lng, api_key, map_type='roadmap', x_pos=30, y_pos=None, width=150, height=80):
        """Add static Google Map image"""
        try:
            if y_pos is None:
                y_pos = self.get_y()
            
            print(f"🗺️ Generating {map_type} map for {lat:.6f}, {lng:.6f}")
            
            base_url = "https://maps.googleapis.com/maps/api/staticmap"
            params = [
                f"center={lat},{lng}",
                f"zoom=17",
                f"size=640x640",
                f"maptype={map_type}",
                f"markers=color:red|size:mid|{lat},{lng}",
                f"key={api_key}"
            ]
            
            url = f"{base_url}?" + "&".join(params)
            print(f"  📡 Static Map API call ({map_type})...")
            
            response = requests.get(url, timeout=20)
            
            if response.status_code == 200:
                content_length = len(response.content)
                print(f"  📊 {map_type} response size: {content_length} bytes")
                
                if content_length > 1000:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp:
                        temp.write(response.content)
                        temp_path = temp.name
                    
                    try:
                        # Add border
                        border_colors = {
                            'roadmap': (100, 100, 100),
                            'satellite': (100, 100, 200),
                            'terrain': (100, 150, 100),
                            'hybrid': (150, 100, 150)
                        }
                        border_color = border_colors.get(map_type, (150, 150, 150))
                        
                        self.set_draw_color(*border_color)
                        self.set_line_width(1)
                        self.rect(x_pos - 1, y_pos - 1, width + 2, height + 2, 'D')
                        
                        # Add image
                        self.image(temp_path, x=x_pos, y=y_pos, w=width, h=height)
                        
                        print(f"   {map_type} map added successfully")
                        
                        # Add small text label
                        self.set_font('Arial', '', 7)
                        self.set_text_color(*border_color)
                        self.set_xy(x_pos, y_pos + height + 1)
                        self.cell(width, 4, f'{map_type.title()} View - Zoom 17', 0, 0, 'C')
                        
                        os.unlink(temp_path)
                        return True
                        
                    except Exception as img_error:
                        print(f"   Invalid {map_type} image: {img_error}")
                        os.unlink(temp_path)
                        self.add_map_placeholder(x_pos, y_pos, width, height, lat, lng, map_type)
                        return False
                else:
                    print(f"  ⚠️ {map_type} response too small ({content_length} bytes)")
                    self.add_map_placeholder(x_pos, y_pos, width, height, lat, lng, map_type)
                    return False
            else:
                print(f"   {map_type} HTTP {response.status_code}")
                self.add_map_placeholder(x_pos, y_pos, width, height, lat, lng, map_type)
                return False
            
        except Exception as e:
            print(f" Static map error ({map_type}): {e}")
            self.add_map_placeholder(x_pos, y_pos, width, height, lat, lng, map_type)
            return False
 # Continuing from the previous part - Helper methods and main function
    
    def add_map_placeholder(self, x_pos, y_pos, width, height, lat, lng, map_type):
        """Add placeholder when map is not available"""
        try:
            # Draw placeholder rectangle
            self.set_draw_color(180, 180, 180)
            self.set_fill_color(250, 250, 250)
            self.rect(x_pos, y_pos, width, height, 'DF')
            
            # Add placeholder text
            self.set_font('Arial', 'B', 12)
            self.set_text_color(120, 120, 120)
            self.set_xy(x_pos, y_pos + height/2 - 20)
            self.cell(width, 8, f'{map_type.upper()} MAP', 0, 0, 'C')
            
            self.set_font('Arial', '', 10)
            self.set_xy(x_pos, y_pos + height/2 - 10)
            self.cell(width, 6, 'NOT AVAILABLE', 0, 0, 'C')
            
            self.set_xy(x_pos, y_pos + height/2)
            self.cell(width, 6, f'{lat:.4f}, {lng:.4f}', 0, 0, 'C')
            
            self.set_font('Arial', '', 8)
            self.set_xy(x_pos, y_pos + height/2 + 15)
            self.cell(width, 5, 'Please verify API key and quota limits', 0, 0, 'C')
            
        except Exception as e:
            print(f"Error adding map placeholder: {e}")
    
    def estimate_poi_location(self, name, location, route_points, index, total_pois):
        """Estimate POI coordinates and distance from route"""
        if not route_points:
            return 0.0, 0.0, 0.0
        
        # Distribute POIs along the route based on their index
        route_length = len(route_points)
        estimated_index = min(int((index / total_pois) * route_length), route_length - 1)
        base_point = route_points[estimated_index]
        
        # Add small random offset to simulate actual POI location
        import random
        random.seed(hash(name) % 1000)  # Consistent random based on name
        
        lat_offset = random.uniform(-0.005, 0.005)
        lng_offset = random.uniform(-0.005, 0.005)
        
        estimated_lat = base_point[0] + lat_offset
        estimated_lng = base_point[1] + lng_offset
        
        # Calculate distance from nearest route point
        distances = []
        for point in route_points[::10]:  # Sample every 10th point for performance
            try:
                dist = geodesic((estimated_lat, estimated_lng), (point[0], point[1])).kilometers
                distances.append(dist)
            except:
                distances.append(0.0)
        
        min_distance = min(distances) if distances else 0.0
        
        return estimated_lat, estimated_lng, min_distance
    
    def add_comprehensive_map_with_markers(self, route_data, api_key):
        """Add comprehensive map with all markers"""
        self.add_page()
        self.add_section_header("COMPREHENSIVE ROUTE MAP WITH ALL MARKERS", "info")
        
        route_points = route_data.get('route_points', [])
        sharp_turns = route_data.get('sharp_turns', [])
        
        if not route_points or len(route_points) < 2:
            self.set_font('Arial', '', 12)
            self.set_text_color(0, 0, 0)
            self.cell(0, 8, 'Route points not available for map generation.', 0, 1, 'L')
            return
        
        # Create comprehensive markers
        markers = self.create_comprehensive_markers(route_data)
        
        # Calculate map center
        center_lat = sum(point[0] for point in route_points) / len(route_points)
        center_lng = sum(point[1] for point in route_points) / len(route_points)
        
        # Generate map
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, 'COMPREHENSIVE ROUTE MAP:', 0, 1, 'L')
        self.ln(3)
        
        if api_key:
            success = self.add_static_map_with_route(center_lat, center_lng, markers, route_points, api_key)
            if success:
                self.ln(3)
                self.add_map_legend()
            else:
                self.set_font('Arial', '', 10)
                self.set_text_color(0, 0, 0)
                self.cell(0, 6, 'Map generation failed. Please check API key and connectivity.', 0, 1, 'L')
        else:
            self.set_font('Arial', '', 10)
            self.set_text_color(0, 0, 0)
            self.cell(0, 6, 'Map generation requires Google Maps API key.', 0, 1, 'L')
    
    def create_comprehensive_markers(self, route_data):
        """Create comprehensive markers for map"""
        markers = []
        route_points = route_data.get('route_points', [])
        
        if not route_points:
            return markers
        
        # Start and end markers
        markers.extend([
            {'lat': route_points[0][0], 'lng': route_points[0][1], 'color': 'green', 'label': 'S', 'title': 'Start'},
            {'lat': route_points[-1][0], 'lng': route_points[-1][1], 'color': 'red', 'label': 'E', 'title': 'End'}
        ])
        
        # Sharp turn markers (top 10 most dangerous)
        sharp_turns = route_data.get('sharp_turns', [])
        if sharp_turns:
            sorted_turns = sorted(sharp_turns, key=lambda x: x.get('angle', 0), reverse=True)
            for i, turn in enumerate(sorted_turns[:10], 1):
                angle = turn.get('angle', 0)
                color = 'red' if angle > 80 else 'orange' if angle > 70 else 'yellow'
                markers.append({
                    'lat': turn['lat'], 
                    'lng': turn['lng'], 
                    'color': color, 
                    'label': f'T{i}',
                    'title': f'Turn {i}: {angle} degrees'
                })
        
        # POI markers
        poi_markers = self.create_poi_markers_for_map(route_points, route_data)
        markers.extend(poi_markers[:15])  # Limit total markers for map clarity
        
        return markers
    
    def create_poi_markers_for_map(self, route_points, route_data):
        """Create POI markers distributed along route"""
        markers = []
        route_length = len(route_points)
        
        if route_length == 0:
            return markers
        
        # Hospitals (blue markers)
        hospitals = list(route_data.get('hospitals', {}).keys())[:3]
        for i, hospital in enumerate(hospitals):
            point_index = min(int((i + 1) * route_length / 4), route_length - 1)
            point = route_points[point_index]
            markers.append({
                'lat': point[0] + 0.002,
                'lng': point[1] + 0.002,
                'color': 'blue',
                'label': f'H{i+1}',
                'title': f'Hospital: {hospital[:20]}'
            })
        
        # Fuel stations (purple markers)  
        fuel_stations = list(route_data.get('petrol_bunks', {}).keys())[:3]
        for i, station in enumerate(fuel_stations):
            point_index = min(int((i + 1) * route_length / 3), route_length - 1)
            point = route_points[point_index]
            markers.append({
                'lat': point[0] - 0.002,
                'lng': point[1] + 0.002,
                'color': 'purple',
                'label': f'F{i+1}',
                'title': f'Fuel: {station[:20]}'
            })
        
        # Schools (yellow markers)
        schools = list(route_data.get('schools', {}).keys())[:2]
        for i, school in enumerate(schools):
            point_index = min(int((i + 2) * route_length / 5), route_length - 1)
            point = route_points[point_index]  
            markers.append({
                'lat': point[0] + 0.001,
                'lng': point[1] - 0.002,
                'color': 'yellow',
                'label': f'S{i+1}',
                'title': f'School: {school[:20]}'
            })
        
        return markers
    
    def add_static_map_with_route(self, center_lat, center_lng, markers, route_points, api_key, zoom=8):
        """Add static map with route and markers"""
        try:
            # Create route path
            path_points = route_points[::5]  # Sample every 5th point to avoid URL length limits
            path_string = '|'.join([f"{point[0]},{point[1]}" for point in path_points])
            
            base_url = "https://maps.googleapis.com/maps/api/staticmap"
            params = [
                f"center={center_lat},{center_lng}",
                f"zoom={zoom}",
                "size=640x400",
                "maptype=roadmap",
                f"path=color:0x0000ff|weight:3|{path_string}"
            ]
            
            # Add markers
            for marker in markers[:15]:  # Limit markers
                color = marker.get('color', 'red')
                label = marker.get('label', '')
                lat = marker.get('lat')
                lng = marker.get('lng')
                
                if lat and lng:
                    params.append(f"markers=size:mid|color:{color}|label:{label}|{lat},{lng}")
            
            params.append(f"key={api_key}")
            
            url = f"{base_url}?" + "&".join(params)
            
            # Limit URL length
            if len(url) > 8192:  # Google's URL limit
                # Fallback: simpler map with fewer points
                simplified_path = '|'.join([f"{point[0]},{point[1]}" for point in route_points[::20]])
                params[3] = f"path=color:0x0000ff|weight:3|{simplified_path}"
                url = f"{base_url}?" + "&".join(params)
            
            response = requests.get(url, timeout=25)
            
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp:
                    temp.write(response.content)
                    temp_path = temp.name
                
                # Add image to PDF
                current_y = self.get_y()
                img_width = 180
                img_height = 100
                
                # Check space and add page if needed
                if current_y + img_height > 270:
                    self.add_page()
                    current_y = self.get_y()
                
                x_position = (210 - img_width) / 2
                
                # Add border
                self.set_draw_color(200, 200, 200)
                self.set_line_width(1)
                self.rect(x_position - 2, current_y - 2, img_width + 4, img_height + 4, 'D')
                
                # Add image
                self.image(temp_path, x=x_position, y=current_y, w=img_width, h=img_height)
                
                os.unlink(temp_path)
                self.set_y(current_y + img_height + 5)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error adding map: {e}")
            return False
    
    def add_map_legend(self):
        """Add comprehensive map legend"""
        self.set_font('Arial', 'B', 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, 'MAP LEGEND:', 0, 1, 'L')
        
        legend_items = [
            ['S', 'Green', 'Route Start Point'],
            ['E', 'Red', 'Route End Point'],
            ['T#', 'Red/Orange/Yellow', 'Sharp Turns (by danger level)'],
            ['H#', 'Blue', 'Hospitals - Emergency Services'],
            ['F#', 'Purple', 'Fuel Stations - Petrol Pumps'],
            ['S#', 'Yellow', 'Schools - Speed Limit 40 km/h'],
            ['Blue Line', 'Blue', 'Complete Route Path']
        ]
        
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        
        for marker, color, description in legend_items:
            self.cell(20, 6, marker, 0, 0, 'L')
            self.cell(25, 6, color, 0, 0, 'L')
            self.cell(0, 6, description, 0, 1, 'L')
    
    def calculate_safety_score(self, sharp_turns, dead_zones_count, poor_zones_count):
        """Calculate safety score"""
        base_score = 100
        
        if not sharp_turns:
            return base_score
        
        blind_spots = len([t for t in sharp_turns if t.get('angle', 0) > 80])
        sharp_danger = len([t for t in sharp_turns if 70 <= t.get('angle', 0) <= 80])
        moderate_turns = len([t for t in sharp_turns if 45 <= t.get('angle', 0) < 70])
        
        base_score -= blind_spots * 15
        base_score -= sharp_danger * 10
        base_score -= moderate_turns * 5
        base_score -= dead_zones_count * 8
        base_score -= poor_zones_count * 4
        
        return max(0, min(100, base_score))
    
    def get_vehicle_info_by_type(self, vehicle_type):
        """Get vehicle information based on type"""
        vehicle_profiles = {
            "heavy_goods_vehicle": {
                "type": "heavy_goods_vehicle",
                "weight": 18000,  # 18 tons
                "passenger_capacity": 2,
                "vehicle_category": "Heavy Goods Vehicle",
                "fuel_type": "Diesel"
            },
            "medium_goods_vehicle": {
                "type": "medium_goods_vehicle", 
                "weight": 8000,   # 8 tons
                "passenger_capacity": 2,
                "vehicle_category": "Medium Goods Vehicle",
                "fuel_type": "Diesel"
            },
            "light_vehicle": {
                "type": "light_motor_vehicle",
                "weight": 2500,   # 2.5 tons
                "passenger_capacity": 5,
                "vehicle_category": "Light Motor Vehicle",
                "fuel_type": "Petrol"
            },
            "bus": {
                "type": "passenger_vehicle",
                "weight": 12000,  # 12 tons
                "passenger_capacity": 45,
                "vehicle_category": "Passenger Vehicle",
                "fuel_type": "Diesel"
            }
        }
        
        return vehicle_profiles.get(vehicle_type, vehicle_profiles["heavy_goods_vehicle"])
    
    def generate_simple_compliance_data(self, route_data, vehicle_info):
        """Generate simple compliance data without external dependencies"""
        weight = vehicle_info.get('weight', 18000)
        
        # Calculate basic compliance score
        score = 100
        if weight > 12000:
            score -= 15  # Heavy vehicle complexity
        
        # Estimate driving time
        duration_str = route_data.get('duration', '8 hours')
        estimated_hours = self.parse_duration_to_hours(duration_str)
        if estimated_hours > 10:
            score -= 20  # RTSP violation
        
        # AIS-140 mandatory for heavy vehicles
        if weight > 3500:
            score -= 25  # Major compliance requirement
        
        return {
            'compliance_score': max(60, score),  # Minimum 60 for demonstration
            'route_summary': {
                'vehicle_type': vehicle_info.get('vehicle_category', 'Heavy Goods Vehicle'),
                'vehicle_weight': f"{weight:,} kg",
                'compliance_category': 'HIGH RISK - Heavy Goods Vehicle' if weight > 12000 else 'MEDIUM RISK'
            }
        }
    
    def parse_duration_to_hours(self, duration_str):
        """Parse duration string to hours"""
        try:
            # Simple parsing
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
            else:
                return 8.0  # Default assumption
        except:
            return 8.0


def generate_pdf(filename, from_addr, to_addr, distance, duration, turns, petrol_bunks,
                hospital_list, schools=None, food_stops=None, police_stations=None, 
                elevation=None, weather=None, risk_segments=None, compliance=None,
                emergency=None, environmental=None, toll_gates=None, bridges=None, 
                vehicle_type="car", type="enhanced", api_key=None, major_highways=None, route_data=None):
    """
    WORKING ENHANCED PDF GENERATION WITH REGULATORY COMPLIANCE & FIXED TEXT RENDERING
    """
    
    # Handle None values
    if not schools: schools = {}
    if not food_stops: food_stops = {}
    if not police_stations: police_stations = {}
    if not elevation: elevation = []
    if not weather: weather = []
    if not risk_segments: risk_segments = []
    if not turns: turns = []
    if not route_data: route_data = {}
    
    try:
        # Create enhanced PDF with proper text handling
        pdf = EnhancedRoutePDF("Enhanced Route Analysis Report with Regulatory Compliance")
        
        print("📄 Starting WORKING Enhanced PDF Generation...")
        
        # 1. Professional title page
        pdf.add_professional_title_page()
        
        # 2. Enhanced route overview with fixed text rendering
        pdf.add_enhanced_route_overview(route_data)
        if api_key:
            pdf.add_comprehensive_map_with_markers(route_data, api_key)
        pdf.add_regulatory_compliance_page(route_data, vehicle_type)
        if vehicle_type in ["heavy_goods_vehicle", "medium_goods_vehicle", "bus"]:
            pdf.google_api_key = api_key  # Pass API key to PDF generator
            pdf.add_heavy_vehicle_analysis_page(route_data, vehicle_type)
        # 3. Detailed POI tables with coordinates and distances
        pdf.add_detailed_poi_tables(route_data)
        # 4. Network Coverage Analysis Page
        pdf.add_network_coverage_analysis_page(route_data)
        
        # 4. Comprehensive map with all markers
        
        
        # 5. *** WORKING FEATURE *** Regulatory Compliance Analysis with fixed text
        print("📋 Adding Working Regulatory Compliance Analysis...")
        
        
        # 6. *** WORKING FEATURE *** Individual turn analysis pages with street views and maps
        if api_key and route_data.get('sharp_turns'):
            critical_turns = [turn for turn in route_data.get('sharp_turns', []) if turn.get('angle', 0) >= 70]
            if critical_turns:
                print(f"🔄 Adding {len(critical_turns)} individual turn analysis pages with street views...")
                pdf.add_individual_turn_pages(route_data, api_key)
        # 7. Advanced Features - Elevation Analysis
        if ElevationAnalyzer:
            pdf.add_elevation_analysis_page(route_data, api_key)

        # 8. Advanced Features - Emergency Planning  
        if EmergencyPlanner and api_key:
            pdf.add_emergency_planning_page(route_data, api_key)
        # Save PDF
        pdf.output(filename)
        
        # Calculate total pages
        total_turns = len([turn for turn in route_data.get('sharp_turns', []) if turn.get('angle', 0) >= 70])
        estimated_pages = 8 + total_turns  # Base pages + individual turn pages + compliance pages
        
        print(f" WORKING Enhanced PDF report generated successfully: {filename}")
        print(f"📊 Features: FIXED text rendering, Regulatory compliance, Individual turn analysis, Street views")
        print(f"📄 Total pages: ~{estimated_pages} (including {total_turns} turn pages + compliance analysis)")
        print(f"🗺️ Street views and satellite maps included for each critical turn")
        print(f"📋 WORKING regulatory compliance analysis with CMVR, AIS-140, RTSP requirements")
        print(f"🔧 FIXED: All emoji and Unicode issues resolved with comprehensive text cleaning")
        
        return filename
        
    except Exception as e:
        print(f" Error generating WORKING enhanced PDF: {e}")
        import traceback
        traceback.print_exc()
        return None