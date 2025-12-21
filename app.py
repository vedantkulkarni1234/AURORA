#!/usr/bin/env python3
"""
Namespace Dominance Engine - Semi-Autonomous Agentic DNS Intelligence Platform

Author: Offensive Cybersecurity Engineer
Version: 1.0.0
Classification: RESTRICTED - Passive Reconnaissance Only

This Streamlit application implements a 6-phase Domain & DNS Intelligence workflow
with dynamic LLM-powered command generation and human-in-the-loop approval.

Requirements:
streamlit>=1.28.0
google-generativeai>=0.3.0
requests>=2.31.0
python-dotenv>=1.0.0
graphviz>=0.20.1
rich>=13.6.0
asyncio
subprocess
json
datetime
re
os
sys
"""

import streamlit as st
import google.generativeai as genai
import requests
import subprocess
import asyncio
import json
import re
import os
import sys
import time
import threading
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import graphviz
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree
import io
import base64
from concurrent.futures import ThreadPoolExecutor

# Configure Streamlit page
st.set_page_config(
    page_title="Namespace Dominance Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Modern CSS Styling System
st.markdown("""
<style>
    :root {
        --color-primary: #0f172a;
        --color-secondary: #1e293b;
        --color-tertiary: #334155;
        --color-accent: #06b6d4;
        --color-accent-light: #22d3ee;
        --color-success: #10b981;
        --color-warning: #f59e0b;
        --color-danger: #ef4444;
        --color-text-primary: #f1f5f9;
        --color-text-secondary: #cbd5e1;
        --color-border: #475569;
        --spacing-xs: 4px;
        --spacing-sm: 8px;
        --spacing-md: 16px;
        --spacing-lg: 24px;
        --spacing-xl: 32px;
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.25);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    * {
        box-sizing: border-box;
    }

    html, body {
        margin: 0;
        padding: 0;
    }

    .stApp {
        background: linear-gradient(135deg, var(--color-primary) 0%, #0d1b2a 100%);
        color: var(--color-text-primary);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
        letter-spacing: 0.3px;
    }

    /* Typography Hierarchy */
    h1, h2, h3, h4, h5, h6 {
        letter-spacing: -0.5px;
        font-weight: 600;
    }

    h1 {
        font-size: 2.5rem;
        line-height: 1.2;
        margin: var(--spacing-lg) 0 var(--spacing-md) 0;
    }

    h2 {
        font-size: 2rem;
        line-height: 1.3;
        margin: var(--spacing-lg) 0 var(--spacing-md) 0;
    }

    h3 {
        font-size: 1.5rem;
        line-height: 1.4;
        margin: var(--spacing-md) 0 var(--spacing-sm) 0;
    }

    h4 {
        font-size: 1.125rem;
        line-height: 1.5;
        margin: var(--spacing-md) 0 var(--spacing-sm) 0;
    }

    /* Refined Input Styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: var(--color-secondary) !important;
        color: var(--color-text-primary) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--spacing-sm) var(--spacing-md) !important;
        font-size: 0.95rem !important;
        transition: var(--transition) !important;
        font-family: inherit !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        background-color: var(--color-tertiary) !important;
        border-color: var(--color-accent) !important;
        box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1) !important;
        outline: none !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: var(--color-text-secondary) !important;
    }

    /* Modern Button Styling */
    .stButton > button {
        background-color: var(--color-accent) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: var(--transition) !important;
        cursor: pointer !important;
        text-transform: none !important;
        box-shadow: var(--shadow-md) !important;
        letter-spacing: 0.3px !important;
    }

    .stButton > button:hover {
        background-color: var(--color-accent-light) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button:disabled {
        background-color: var(--color-tertiary) !important;
        color: var(--color-text-secondary) !important;
        cursor: not-allowed !important;
        opacity: 0.6 !important;
    }

    /* Primary Button Variant */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-light) 100%) !important;
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 20px rgba(6, 182, 212, 0.4) !important;
    }

    /* Card/Container Styling */
    .premium-card {
        background-color: var(--color-secondary);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        margin: var(--spacing-md) 0;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        backdrop-filter: blur(10px);
    }

    .premium-card:hover {
        border-color: var(--color-accent);
        box-shadow: 0 4px 20px rgba(6, 182, 212, 0.15);
        transform: translateY(-2px);
    }

    /* Header Styling - Premium Modern */
    .premium-header {
        background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-light) 100%);
        padding: var(--spacing-xl) var(--spacing-lg);
        border-radius: var(--radius-lg);
        margin-bottom: var(--spacing-xl);
        box-shadow: 0 10px 30px rgba(6, 182, 212, 0.25);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .premium-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        animation: pulse-glow 3s ease-in-out infinite;
    }

    @keyframes pulse-glow {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }

    .premium-header h1 {
        color: white !important;
        margin: 0 !important;
        position: relative;
        z-index: 1;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 2.25rem;
    }

    .premium-header > small {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.875rem !important;
        letter-spacing: 1px !important;
        display: block !important;
        margin-top: var(--spacing-sm) !important;
        position: relative;
        z-index: 1;
    }

    /* Phase Status Styling */
    .phase-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: var(--radius-md);
        font-weight: 600;
        font-size: 0.875rem;
        transition: var(--transition);
        border: 1px solid;
        letter-spacing: 0.5px;
    }

    .phase-complete {
        background-color: rgba(16, 185, 129, 0.15) !important;
        border-color: var(--color-success) !important;
        color: var(--color-success) !important;
    }

    .phase-active {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(34, 211, 238, 0.1) 100%) !important;
        border-color: var(--color-accent) !important;
        color: var(--color-accent-light) !important;
        box-shadow: 0 0 10px rgba(6, 182, 212, 0.2) !important;
        animation: pulse-border 2s ease-in-out infinite;
    }

    @keyframes pulse-border {
        0%, 100% { box-shadow: 0 0 10px rgba(6, 182, 212, 0.2); }
        50% { box-shadow: 0 0 20px rgba(6, 182, 212, 0.4); }
    }

    .phase-pending {
        background-color: var(--color-tertiary) !important;
        border-color: var(--color-border) !important;
        color: var(--color-text-secondary) !important;
    }

    /* Console Output Styling */
    .console-output {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        color: var(--color-accent);
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        padding: var(--spacing-lg);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        max-height: 500px;
        overflow-y: auto;
        margin: var(--spacing-md) 0;
        line-height: 1.6;
        font-size: 0.875rem;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
        word-break: break-word;
        white-space: pre-wrap;
    }

    /* Scrollbar Styling */
    .console-output::-webkit-scrollbar {
        width: 8px;
    }

    .console-output::-webkit-scrollbar-track {
        background: var(--color-secondary);
        border-radius: var(--radius-sm);
    }

    .console-output::-webkit-scrollbar-thumb {
        background: var(--color-accent);
        border-radius: var(--radius-sm);
    }

    .console-output::-webkit-scrollbar-thumb:hover {
        background: var(--color-accent-light);
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: var(--color-secondary) !important;
        color: var(--color-text-primary) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--spacing-md) !important;
        transition: var(--transition) !important;
    }

    .streamlit-expanderHeader:hover {
        background-color: var(--color-tertiary) !important;
        border-color: var(--color-accent) !important;
    }

    /* Metric Cards */
    [data-testid="metric-container"] {
        background-color: var(--color-secondary) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--spacing-lg) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* Alert/Info/Success/Error Styling */
    .stAlert {
        background-color: var(--color-secondary) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--spacing-md) !important;
        color: var(--color-text-primary) !important;
    }

    .stSuccess {
        background-color: rgba(16, 185, 129, 0.15) !important;
        border-color: var(--color-success) !important;
        color: var(--color-success) !important;
    }

    .stError {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border-color: var(--color-danger) !important;
        color: var(--color-danger) !important;
    }

    .stWarning {
        background-color: rgba(245, 158, 11, 0.15) !important;
        border-color: var(--color-warning) !important;
        color: var(--color-warning) !important;
    }

    .stInfo {
        background-color: rgba(6, 182, 212, 0.15) !important;
        border-color: var(--color-accent) !important;
        color: var(--color-accent-light) !important;
    }

    /* Columns Spacing */
    .stColumns > div {
        gap: var(--spacing-lg);
    }

    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--color-accent-light);
        margin: var(--spacing-lg) 0 var(--spacing-md) 0;
        padding-bottom: var(--spacing-md);
        border-bottom: 2px solid var(--color-accent);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--color-primary) 0%, #0d1b2a 100%) !important;
    }

    [data-testid="stSidebar"] > div > div {
        background: transparent !important;
    }

    /* Code Block Styling */
    .stCodeBlock {
        background-color: var(--color-secondary) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-md) !important;
    }

    code {
        background-color: var(--color-tertiary);
        color: var(--color-accent);
        padding: 2px 6px;
        border-radius: var(--radius-sm);
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.85rem;
    }

    /* Spinner and Loading */
    .stSpinner {
        color: var(--color-accent) !important;
    }

    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--color-accent) 0%, var(--color-accent-light) 100%) !important;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] button {
        background-color: transparent !important;
        border-bottom: 2px solid transparent !important;
        color: var(--color-text-secondary) !important;
        transition: var(--transition) !important;
    }

    .stTabs [data-baseweb="tab-list"] button:hover {
        color: var(--color-accent) !important;
    }

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        border-bottom-color: var(--color-accent) !important;
        color: var(--color-accent-light) !important;
    }

    /* Markdown Links */
    a {
        color: var(--color-accent) !important;
        text-decoration: none !important;
        transition: var(--transition) !important;
    }

    a:hover {
        color: var(--color-accent-light) !important;
        text-decoration: underline !important;
    }

    /* Special Section - Phase Grid */
    .phase-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: var(--spacing-lg);
        margin: var(--spacing-lg) 0;
    }

    .phase-item {
        background-color: var(--color-secondary);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        transition: var(--transition);
        position: relative;
    }

    .phase-item:hover {
        border-color: var(--color-accent);
        box-shadow: 0 8px 24px rgba(6, 182, 212, 0.2);
        transform: translateY(-4px);
    }

    /* Gradient Accent Line */
    .accent-line {
        height: 3px;
        background: linear-gradient(90deg, var(--color-accent) 0%, var(--color-accent-light) 100%);
        border-radius: 2px;
        margin: var(--spacing-md) 0;
    }

    /* Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--spacing-xs);
        padding: 6px 12px;
        border-radius: var(--radius-sm);
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-success {
        background-color: rgba(16, 185, 129, 0.2);
        color: var(--color-success);
    }

    .status-active {
        background-color: rgba(6, 182, 212, 0.2);
        color: var(--color-accent);
        animation: pulse-glow 2s ease-in-out infinite;
    }

    .status-pending {
        background-color: rgba(100, 116, 139, 0.2);
        color: var(--color-text-secondary);
    }

    /* Fade-in Animation */
    @keyframes fade-in {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in {
        animation: fade-in 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class PhaseResult:
    """Structured result for each phase execution"""
    phase_number: int
    phase_name: str
    status: str  # PENDING, ACTIVE, COMPLETED, FAILED
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    commands_executed: List[str]
    findings: Dict[str, Any]
    artifacts: List[str]
    confidence_score: float
    reasoning: str

@dataclass
class NamespaceMap:
    """Master namespace mapping structure"""
    target_domain: str
    discovery_phases: Dict[int, PhaseResult]
    infrastructure_skeleton: Dict[str, Any]
    temporal_analysis: Dict[str, Any]
    control_plane: Dict[str, Any]
    adversarial_posture: Dict[str, Any]
    predictive_model: Dict[str, Any]
    created_at: datetime
    last_updated: datetime

class AIAgent:
    """Agentic AI powered by Gemini for dynamic command generation"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.console = Console()
        
    def generate_phase_commands(self, phase: int, target: str, context: Dict[str, Any]) -> Tuple[str, List[str], str]:
        """Dynamically generate commands for a specific phase"""
        
        phase_doctrine = {
            0: {
                "name": "Event Horizon Framing",
                "objectives": [
                    "Authority Surface Isolation",
                    "Temporal Ownership Compression", 
                    "Semantic Drift Mapping",
                    "Registrar Behavior Fingerprinting"
                ],
                "techniques": [
                    "WHOIS registrar analysis",
                    "Historical ownership records",
                    "DNS semantic variation analysis",
                    "Registration pattern fingerprinting"
                ]
            },
            1: {
                "name": "Inertial Enumeration",
                "objectives": [
                    "Historical Resolution Echoes",
                    "Cross-Zone Naming Symmetry",
                    "Delegation Entropy Analysis",
                    "Operational Laziness Exploitation"
                ],
                "techniques": [
                    "Passive DNS historical analysis",
                    "Subzone enumeration via public records",
                    "NS delegation pattern analysis",
                    "Infrastructure reuse detection"
                ]
            },
            2: {
                "name": "Temporal Parallax",
                "objectives": [
                    "Resolution Latency Phase-Shift",
                    "TTL Personality Profiling",
                    "Propagation Asymmetry Detection",
                    "Maintenance Window Inference"
                ],
                "techniques": [
                    "DNS resolution timing analysis",
                    "TTL variation fingerprinting",
                    "Geographic propagation analysis",
                    "Maintenance pattern detection"
                ]
            },
            3: {
                "name": "Infrastructure Skeletonization",
                "objectives": [
                    "Shared Fate Correlation",
                    "Negative Space Cartography",
                    "Protocol Behavior Residue",
                    "Fallback Path Reconstruction"
                ],
                "techniques": [
                    "IP infrastructure correlation",
                    "Unused subnet analysis",
                    "Service fingerprinting via passive data",
                    "Failover path reconstruction"
                ]
            },
            4: {
                "name": "Control Plane Inference",
                "objectives": [
                    "Update Velocity Measurement",
                    "Rollback Signature Detection",
                    "Blast Radius Estimation",
                    "Control-Key Shadowing (outcome only)"
                ],
                "techniques": [
                    "DNS change frequency analysis",
                    "Configuration rollback detection",
                    "Impact radius calculation",
                    "Control plane inference"
                ]
            },
            5: {
                "name": "Adversarial Posture Modeling",
                "objectives": [
                    "Countermeasure Reflex Profiling",
                    "Decoy Discrimination",
                    "Sensor Placement Inference",
                    "Escalation Threshold Mapping"
                ],
                "techniques": [
                    "Security posture analysis",
                    "Honeypot/decoy detection",
                    "Sensor network mapping",
                    "Response threshold analysis"
                ]
            },
            6: {
                "name": "Predictive Namespace Dominance",
                "objectives": [
                    "Future Domain Pre-Image Modeling",
                    "Lifecycle Exhaust Mapping",
                    "Strategic Choke Anticipation",
                    "Deterministic Collapse Triggering (outcome only)"
                ],
                "techniques": [
                    "Future domain prediction",
                    "Lifecycle pattern analysis",
                    "Chokepoint identification",
                    "Collapse prediction modeling"
                ]
            }
        }
        
        phase_info = phase_doctrine.get(phase, phase_doctrine[0])
        
        prompt = f"""
You are an elite offensive cybersecurity engineer executing Phase {phase}: {phase_info['name']} against target {target}.

DOCTRINE - ABSOLUTE LAW:
{chr(10).join(f"{i+1}. {obj}" for i, obj in enumerate(phase_info['objectives']))}

AUTHORIZED TECHNIQUES (PASSIVE ONLY):
{chr(10).join(f"- {tech}" for tech in phase_info['techniques'])}

CONTEXT FROM PREVIOUS PHASES:
{json.dumps(context, indent=2)}

MISSION:
Generate a comprehensive reasoning and exact shell commands to achieve all phase objectives.

RULES:
1. ALL TECHNIQUES MUST BE PASSIVE - no active DNS queries, port scans, or direct HTTP requests
2. Use public data sources: Certificate Transparency, SecurityTrails, Shodan, PassiveTotal, DNS dumps, Common Crawl
3. Each command must be complete and executable
4. Include proper error handling and output parsing
5. Commands must be dynamically generated - no hardcoded lists
6. Focus on evidence collection and correlation

RESPONSE FORMAT:
---REASONING---
[Detailed tactical reasoning for this phase execution]
---COMMANDS---
[Complete shell commands, one per line]
---EXPECTED_OUTCOME---
[Expected intelligence outcomes]
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Parse response
            reasoning_match = re.search(r'---REASONING---(.*?)---COMMANDS---', response_text, re.DOTALL)
            commands_match = re.search(r'---COMMANDS---(.*?)---EXPECTED_OUTCOME---', response_text, re.DOTALL)
            outcome_match = re.search(r'---EXPECTED_OUTCOME---(.*)', response_text, re.DOTALL)
            
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "Reasoning not parsed"
            commands_text = commands_match.group(1).strip() if commands_match else ""
            expected_outcome = outcome_match.group(1).strip() if outcome_match else "Outcome not parsed"
            
            # Parse commands into list
            commands = [cmd.strip() for cmd in commands_text.split('\n') if cmd.strip() and not cmd.strip().startswith('#')]
            
            return reasoning, commands, expected_outcome
            
        except Exception as e:
            return f"AI Generation Error: {str(e)}", [], "Failed to generate commands"

class NamespaceDominanceEngine:
    """Main application class for the Namespace Dominance Engine"""
    
    def __init__(self):
        self.console = Console()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'target_domain' not in st.session_state:
            st.session_state.target_domain = ""
        if 'api_key' not in st.session_state:
            st.session_state.api_key = ""
        if 'current_phase' not in st.session_state:
            st.session_state.current_phase = 0
        if 'phase_results' not in st.session_state:
            st.session_state.phase_results = {}
        if 'namespace_map' not in st.session_state:
            st.session_state.namespace_map = None
        if 'operation_log' not in st.session_state:
            st.session_state.operation_log = []
        if 'ai_agent' not in st.session_state:
            st.session_state.ai_agent = None
        if 'execution_approved' not in st.session_state:
            st.session_state.execution_approved = False
        if 'current_reasoning' not in st.session_state:
            st.session_state.current_reasoning = ""
        if 'current_commands' not in st.session_state:
            st.session_state.current_commands = []
        if 'operation_start_time' not in st.session_state:
            st.session_state.operation_start_time = None
            
    def render_header(self):
        """Render the premium header"""
        st.markdown("""
        <div class="premium-header">
            <h1>⚡ NAMESPACE DOMINANCE ENGINE</h1>
            <small>SEMI-AUTONOMOUS AGENTIC DNS INTELLIGENCE PLATFORM</small>
        </div>
        """, unsafe_allow_html=True)
        
    def render_sidebar(self):
        """Render the premium sidebar"""
        st.sidebar.markdown('<div class="section-header">⚙️ Configuration</div>', unsafe_allow_html=True)
        st.sidebar.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
        
        # API Key input
        api_key = st.sidebar.text_input(
            "🔑 Gemini API Key",
            type="password",
            value=st.session_state.api_key,
            help="Enter your Gemini API key for AI command generation"
        )
        st.session_state.api_key = api_key
        
        # Target domain input
        target_domain = st.sidebar.text_input(
            "🎯 Target Domain",
            value=st.session_state.target_domain,
            help="Enter the target domain for intelligence gathering"
        )
        st.session_state.target_domain = target_domain
        
        # Initialize AI agent if API key provided
        if api_key and not st.session_state.ai_agent:
            try:
                st.session_state.ai_agent = AIAgent(api_key)
                st.sidebar.success("✅ AI Agent Initialized")
            except Exception as e:
                st.sidebar.error(f"❌ AI Agent Failed: {str(e)}")
        
        st.sidebar.markdown("")  # Spacing
        st.sidebar.markdown('<div class="section-header">📊 Phase Progress</div>', unsafe_allow_html=True)
        st.sidebar.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
        
        phase_names = [
            "Event Horizon Framing",
            "Inertial Enumeration", 
            "Temporal Parallax",
            "Infrastructure Skeletonization",
            "Control Plane Inference",
            "Adversarial Posture Modeling",
            "Predictive Namespace Dominance"
        ]
        
        for i, name in enumerate(phase_names):
            if i < st.session_state.current_phase:
                status = "✅"
                css_class = "phase-badge phase-complete"
            elif i == st.session_state.current_phase:
                status = "🔄"
                css_class = "phase-badge phase-active"
            else:
                status = "⏳"
                css_class = "phase-badge phase-pending"
                
            st.sidebar.markdown(f"""
            <div class="{css_class}" style="width: 100%; margin: {6}px 0;">
                {status} Phase {i}: {name}
            </div>
            """, unsafe_allow_html=True)
        
        st.sidebar.markdown("")  # Spacing
        st.sidebar.markdown('<div class="section-header">🎮 Controls</div>', unsafe_allow_html=True)
        st.sidebar.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button(
                "🚀 START",
                disabled=not (api_key and target_domain),
                help="Initialize the intelligence operation",
                use_container_width=True
            ):
                self.start_operation()
            
        with col2:
            if st.button(
                "📥 EXPORT",
                disabled=st.session_state.namespace_map is None,
                help="Export operation results as JSON",
                use_container_width=True
            ):
                self.export_results()
        
        if st.sidebar.button(
            "🔄 RESET SESSION",
            help="Clear all session data and start fresh",
            use_container_width=True
        ):
            self.reset_session()
            
    def start_operation(self):
        """Initialize a new operation"""
        if not st.session_state.target_domain or not st.session_state.api_key:
            st.error("❌ Target domain and API key required")
            return
            
        st.session_state.operation_start_time = datetime.now(timezone.utc)
        st.session_state.current_phase = 0
        st.session_state.phase_results = {}
        st.session_state.operation_log = []
        st.session_state.namespace_map = None
        
        self.log_event(f"🚀 Operation initiated against {st.session_state.target_domain}")
        st.rerun()
        
    def reset_session(self):
        """Reset the entire session"""
        for key in st.session_state.keys():
            del st.session_state[key]
        self.initialize_session_state()
        st.rerun()
        
    def log_event(self, message: str):
        """Add event to operation log"""
        timestamp = datetime.now(timezone.utc).isoformat()
        st.session_state.operation_log.append({
            "timestamp": timestamp,
            "message": message
        })
        
    def execute_command(self, command: str) -> Tuple[str, int, str]:
        """Execute a shell command and return output"""
        try:
            # Replace template variables
            command = command.replace("{TARGET}", st.session_state.target_domain)
            command = command.replace("{DOMAIN}", st.session_state.target_domain)
            
            # Execute command with timeout
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return result.stdout, result.returncode, result.stderr
            
        except subprocess.TimeoutExpired:
            return "", 1, "Command timed out after 5 minutes"
        except Exception as e:
            return "", 1, str(e)
            
    def render_phase_execution(self):
        """Render the current phase execution interface"""
        if not st.session_state.ai_agent or not st.session_state.target_domain:
            st.warning("⚠️ Configure API key and target domain to begin")
            return
            
        if st.session_state.current_phase > 6:
            st.success("🎉 Operation Complete - All phases executed")
            self.render_final_results()
            return
            
        phase_names = [
            "Event Horizon Framing",
            "Inertial Enumeration", 
            "Temporal Parallax",
            "Infrastructure Skeletonization",
            "Control Plane Inference",
            "Adversarial Posture Modeling",
            "Predictive Namespace Dominance"
        ]
        
        current_phase_name = phase_names[st.session_state.current_phase]
        
        st.markdown(f'<div class="section-header">🎯 Phase {st.session_state.current_phase}: {current_phase_name}</div>', unsafe_allow_html=True)
        st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
        
        # Generate phase commands if not already done
        if not st.session_state.current_reasoning and not st.session_state.current_commands:
            with st.spinner("🧠 AI Agent generating tactical approach..."):
                context = {
                    "previous_phases": {
                        str(k): asdict(v) for k, v in st.session_state.phase_results.items()
                    },
                    "target": st.session_state.target_domain,
                    "current_phase": st.session_state.current_phase
                }
                
                reasoning, commands, outcome = st.session_state.ai_agent.generate_phase_commands(
                    st.session_state.current_phase,
                    st.session_state.target_domain,
                    context
                )
                
                st.session_state.current_reasoning = reasoning
                st.session_state.current_commands = commands
                
        # Display AI reasoning
        if st.session_state.current_reasoning:
            with st.container():
                st.markdown('<h4 style="color: #22d3ee; margin-bottom: 12px;">🧠 AI Tactical Reasoning</h4>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="premium-card">
                {st.session_state.current_reasoning}
                </div>
                """, unsafe_allow_html=True)
            
        # Display generated commands
        if st.session_state.current_commands:
            st.markdown('<h4 style="color: #22d3ee; margin-top: 24px; margin-bottom: 12px;">⚡ Dynamically Generated Commands</h4>', unsafe_allow_html=True)
            
            for i, cmd in enumerate(st.session_state.current_commands, 1):
                st.markdown(f'<span style="color: #06b6d4; font-weight: 600;">Command {i}:</span>', unsafe_allow_html=True)
                st.code(cmd, language="bash")
                
            # Expected outcome
            if hasattr(st.session_state.ai_agent, 'model'):
                st.markdown('<h4 style="color: #22d3ee; margin-top: 24px; margin-bottom: 12px;">🎯 Expected Outcome</h4>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="premium-card" style="border-color: #10b981; background-color: rgba(16, 185, 129, 0.1);">
                <span style="color: #10b981;">✓ Intelligence gathering will achieve the phase objectives through passive reconnaissance techniques.</span>
                </div>
                """, unsafe_allow_html=True)
                
            # Human approval gate
            st.markdown('<h4 style="color: #22d3ee; margin-top: 24px; margin-bottom: 12px;">🔐 Human-in-the-Loop Approval</h4>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(
                    "✅ APPROVE & EXECUTE",
                    type="primary",
                    help="Execute the generated commands"
                ):
                    self.execute_phase()
                    
            with col2:
                if st.button(
                    "❌ REJECT & REGENERATE",
                    help="Reject these commands and generate new ones"
                ):
                    st.session_state.current_reasoning = ""
                    st.session_state.current_commands = []
                    st.rerun()
                    
    def execute_phase(self):
        """Execute the current phase commands"""
        if not st.session_state.current_commands:
            st.error("No commands to execute")
            return
            
        phase_number = st.session_state.current_phase
        phase_names = [
            "Event Horizon Framing",
            "Inertial Enumeration", 
            "Temporal Parallax",
            "Infrastructure Skeletonization",
            "Control Plane Inference",
            "Adversarial Posture Modeling",
            "Predictive Namespace Dominance"
        ]
        
        phase_result = PhaseResult(
            phase_number=phase_number,
            phase_name=phase_names[phase_number],
            status="ACTIVE",
            start_time=datetime.now(timezone.utc),
            end_time=None,
            commands_executed=[],
            findings={},
            artifacts=[],
            confidence_score=0.0,
            reasoning=st.session_state.current_reasoning
        )
        
        # Create execution log container
        log_container = st.container()
        
        with log_container:
            st.markdown('<h4 style="color: #22d3ee; margin-bottom: 12px;">📡 Execution Log</h4>', unsafe_allow_html=True)
            execution_log = st.empty()
            log_content = []
            
        # Execute each command
        for i, command in enumerate(st.session_state.current_commands, 1):
            self.log_event(f"🔄 Executing command {i}/{len(st.session_state.current_commands)}: {command[:50]}...")
            
            # Update execution log
            log_content.append(f"[{datetime.now().strftime('%H:%M:%S')}] Executing: {command}")
            execution_log.markdown(f"""
            <div class="console-output">
            {'<br>'.join(log_content)}
            </div>
            """, unsafe_allow_html=True)
            
            # Execute command
            stdout, returncode, stderr = self.execute_command(command)
            
            phase_result.commands_executed.append(command)
            
            # Log results
            if returncode == 0:
                log_content.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ SUCCESS")
                if stdout.strip():
                    log_content.append(f"OUTPUT: {stdout[:200]}..." if len(stdout) > 200 else f"OUTPUT: {stdout}")
                phase_result.findings[f"command_{i}"] = {
                    "command": command,
                    "status": "success",
                    "output": stdout
                }
            else:
                log_content.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ FAILED (code: {returncode})")
                if stderr.strip():
                    log_content.append(f"ERROR: {stderr[:200]}..." if len(stderr) > 200 else f"ERROR: {stderr}")
                phase_result.findings[f"command_{i}"] = {
                    "command": command,
                    "status": "failed",
                    "error": stderr
                }
                
            # Update display
            execution_log.markdown(f"""
            <div class="console-output">
            {'<br>'.join(log_content)}
            </div>
            """, unsafe_allow_html=True)
            
            # Small delay for visual effect
            time.sleep(0.5)
            
        # Complete phase
        phase_result.end_time = datetime.now(timezone.utc)
        phase_result.status = "COMPLETED"
        
        # Calculate confidence score based on success rate
        successful_commands = sum(1 for f in phase_result.findings.values() if f.get("status") == "success")
        phase_result.confidence_score = successful_commands / len(phase_result.commands_executed) if phase_result.commands_executed else 0.0
        
        # Store result
        st.session_state.phase_results[phase_number] = phase_result
        
        # Log completion
        self.log_event(f"✅ Phase {phase_number} completed with {phase_result.confidence_score:.1%} confidence")
        
        # Clear current commands and advance to next phase
        st.session_state.current_reasoning = ""
        st.session_state.current_commands = []
        st.session_state.current_phase += 1
        
        st.success(f"🎉 Phase {phase_number} completed successfully!")
        time.sleep(2)
        st.rerun()
        
    def render_operation_log(self):
        """Render the operation log"""
        st.markdown('<div class="section-header">📋 Operation Log</div>', unsafe_allow_html=True)
        st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
        
        if not st.session_state.operation_log:
            st.info("No operations logged yet")
            return
            
        log_container = st.container()
        
        with log_container:
            log_text = []
            for entry in reversed(st.session_state.operation_log[-20:]):  # Show last 20 entries
                timestamp = datetime.fromisoformat(entry["timestamp"]).strftime('%H:%M:%S')
                log_text.append(f"[{timestamp}] {entry['message']}")
                
            st.markdown(f"""
            <div class="console-output">
            {'<br>'.join(log_text)}
            </div>
            """, unsafe_allow_html=True)
            
    def render_phase_summary(self):
        """Render summary of completed phases"""
        st.markdown('<div class="section-header">📊 Phase Summary</div>', unsafe_allow_html=True)
        st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
        
        if not st.session_state.phase_results:
            st.info("No phases completed yet")
            return
        
        # Create phase grid
        st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)
        
        for phase_num, result in st.session_state.phase_results.items():
            with st.expander(f"📍 Phase {phase_num}: {result.phase_name} — {result.status}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f'<div class="status-badge status-active">Status: {result.status}</div>', unsafe_allow_html=True)
                    st.metric("Confidence", f"{result.confidence_score:.1%}")
                    
                with col2:
                    duration = (result.end_time - result.start_time).total_seconds()
                    st.metric("Duration", f"{duration:.1f}s")
                    st.metric("Commands", len(result.commands_executed))
                    
                with col3:
                    st.markdown("**Reasoning Summary:**")
                    reasoning_text = f"{result.reasoning[:250]}..." if len(result.reasoning) > 250 else result.reasoning
                    st.markdown(f'<span style="font-size: 0.85rem; color: #cbd5e1;">{reasoning_text}</span>', unsafe_allow_html=True)
                
                # Findings section
                if result.findings:
                    st.markdown('<div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #475569;"></div>', unsafe_allow_html=True)
                    st.markdown('<h5 style="color: #22d3ee;">📋 Command Findings</h5>', unsafe_allow_html=True)
                    
                    for key, finding in result.findings.items():
                        if finding.get("status") == "success":
                            st.markdown(f'<div class="premium-card" style="border-left: 4px solid #10b981;"><span style="color: #10b981;">✅</span> <strong>{key}</strong>: SUCCESS</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="premium-card" style="border-left: 4px solid #ef4444;"><span style="color: #ef4444;">❌</span> <strong>{key}</strong>: FAILED</div>', unsafe_allow_html=True)
                        
    def render_namespace_map(self):
        """Render the master namespace map"""
        st.markdown('<div class="section-header">🗺️ Master Namespace Map</div>', unsafe_allow_html=True)
        st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
        
        if not st.session_state.phase_results:
            st.info("Namespace map will populate as phases complete")
            return
        
        st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)
            
        # Create visual representation with modern colors
        try:
            dot = graphviz.Digraph(comment='Namespace Map', format='png')
            dot.attr(bgcolor='#0f172a', fontcolor='#22d3ee', graph_attr={'bgcolor':'#0f172a', 'splines': 'curved'})
            dot.attr('node', fontname='Arial', fontcolor='#f1f5f9', style='filled', fillcolor='#1e293b', color='#06b6d4', penwidth='2')
            dot.attr('edge', color='#475569', penwidth='1.5')
            
            # Add target domain with emphasis
            dot.node(st.session_state.target_domain, st.session_state.target_domain, 
                    fillcolor='#06b6d4', fontcolor='#0f172a', penwidth='3')
            
            # Add phase nodes with color coding
            for phase_num, result in st.session_state.phase_results.items():
                phase_label = f"Phase {phase_num}\n{result.status}"
                color = '#10b981' if result.status == 'COMPLETED' else '#f59e0b'
                dot.attr('node', fillcolor=color, color=color, fontcolor='#0f172a')
                dot.node(f"phase_{phase_num}", phase_label)
                dot.edge(st.session_state.target_domain, f"phase_{phase_num}")
                
            # Render graph
            st.graphviz_chart(dot)
            
        except Exception as e:
            st.markdown(f'<div class="premium-card" style="border-left: 4px solid #ef4444;"><span style="color: #ef4444;">⚠️</span> Graph rendering failed: {str(e)}</div>', unsafe_allow_html=True)
            
        # Show structured data
        if st.button("📋 Show Raw Data", use_container_width=True):
            st.json({
                str(k): asdict(v) for k, v in st.session_state.phase_results.items()
            })
            
    def render_final_results(self):
        """Render final operation results"""
        st.markdown('<div class="section-header">🎉 Operation Complete</div>', unsafe_allow_html=True)
        st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.operation_start_time:
                duration = datetime.now(timezone.utc) - st.session_state.operation_start_time
                st.metric("Total Duration", f"{duration.total_seconds():.1f}s")
                
        with col2:
            # Calculate overall confidence
            if st.session_state.phase_results:
                total_confidence = sum(r.confidence_score for r in st.session_state.phase_results.values())
                avg_confidence = total_confidence / len(st.session_state.phase_results)
                st.metric("Overall Confidence", f"{avg_confidence:.1%}")
        
        st.markdown('<div style="margin-top: 32px;"></div>', unsafe_allow_html=True)
        st.markdown('<h4 style="color: #22d3ee;">📤 Export Results</h4>', unsafe_allow_html=True)
            
        # Export options in a grid
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export JSON", use_container_width=True):
                self.export_json()
                
        with col2:
            if st.button("📊 Export Report", use_container_width=True):
                self.export_report()
                
        with col3:
            if st.button("🔄 New Operation", use_container_width=True):
                self.reset_session()
                
    def export_json(self):
        """Export results as JSON"""
        if not st.session_state.phase_results:
            st.error("No results to export")
            return
            
        export_data = {
            "target_domain": st.session_state.target_domain,
            "operation_start_time": st.session_state.operation_start_time.isoformat() if st.session_state.operation_start_time else None,
            "phase_results": {
                str(k): asdict(v) for k, v in st.session_state.phase_results.items()
            },
            "operation_log": st.session_state.operation_log,
            "export_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        json_str = json.dumps(export_data, indent=2, default=str)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"namespace_dominance_{st.session_state.target_domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
    def export_report(self):
        """Export a formatted report"""
        if not st.session_state.phase_results:
            st.error("No results to export")
            return
            
        report = f"""
# NAMESPACE DOMINANCE ENGINE - OPERATION REPORT

**Target Domain:** {st.session_state.target_domain}
**Operation Start:** {st.session_state.operation_start_time}
**Operation Duration:** {(datetime.now(timezone.utc) - st.session_state.operation_start_time).total_seconds():.1f} seconds

## EXECUTIVE SUMMARY

Operation completed {len(st.session_state.phase_results)} phases of intelligence gathering.

## PHASE RESULTS

"""
        
        for phase_num, result in st.session_state.phase_results.items():
            report += f"""
### Phase {phase_num}: {result.phase_name}
- **Status:** {result.status}
- **Confidence Score:** {result.confidence_score:.1%}
- **Duration:** {(result.end_time - result.start_time).total_seconds():.1f} seconds
- **Commands Executed:** {len(result.commands_executed)}

**Key Findings:**
"""
            
            for key, finding in result.findings.items():
                if finding.get("status") == "success":
                    report += f"- {key}: SUCCESS\n"
                else:
                    report += f"- {key}: FAILED - {finding.get('error', 'Unknown error')}\n"
                    
        report += f"""

## OPERATION LOG

"""
        
        for entry in st.session_state.operation_log:
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime('%Y-%m-%d %H:%M:%S UTC')
            report += f"[{timestamp}] {entry['message']}\n"
            
        report += f"""

---
Generated by Namespace Dominance Engine on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
Classification: RESTRICTED - Passive Reconnaissance Only
"""
        
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=f"namespace_report_{st.session_state.target_domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
        
    def export_results(self):
        """Export all results"""
        self.export_json()
        
    def run(self):
        """Main application runner"""
        self.initialize_session_state()
        self.render_header()
        self.render_sidebar()
        
        # Main content area
        if st.session_state.target_domain and st.session_state.api_key:
            # Phase execution
            self.render_phase_execution()
            
            # Operation log
            self.render_operation_log()
            
            # Phase summary
            self.render_phase_summary()
            
            # Namespace map
            self.render_namespace_map()
            
            # Final results if complete
            if st.session_state.current_phase > 6:
                self.render_final_results()
        else:
            st.markdown("""
            <div style="margin-top: 40px; margin-bottom: 40px;">
                <h2 style="color: #22d3ee; text-align: center; margin-bottom: 32px;">🎯 Mission Briefing</h2>
                
                <div class="premium-card" style="margin: 24px 0; padding: 32px;">
                    <p style="font-size: 1.1rem; line-height: 1.8; color: #f1f5f9; margin: 0;">
                    Welcome to the <strong style="color: #22d3ee;">Namespace Dominance Engine</strong> — 
                    a semi-autonomous agentic platform for comprehensive DNS and domain intelligence gathering. 
                    This enterprise-grade platform combines AI-powered reconnaissance with human oversight to deliver 
                    actionable intelligence through passive, non-invasive techniques.
                    </p>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin: 32px 0;">
                    <div class="premium-card" style="padding: 24px;">
                        <h3 style="color: #22d3ee; margin-top: 0; margin-bottom: 16px;">✨ Capabilities</h3>
                        <ul style="margin: 0; padding-left: 20px; line-height: 2;">
                            <li>🔍 7-Phase intelligence workflow</li>
                            <li>🧠 AI-powered dynamic command generation</li>
                            <li>🔒 100% passive reconnaissance</li>
                            <li>👤 Human-in-the-loop approval gates</li>
                            <li>📊 Real-time progress tracking</li>
                            <li>🗺️ Master namespace mapping</li>
                        </ul>
                    </div>
                    
                    <div class="premium-card" style="padding: 24px;">
                        <h3 style="color: #22d3ee; margin-top: 0; margin-bottom: 16px;">🚀 Quick Start</h3>
                        <ol style="margin: 0; padding-left: 20px; line-height: 2;">
                            <li>Enter your Gemini API key in the sidebar</li>
                            <li>Specify your target domain for analysis</li>
                            <li>Click "START" to begin intelligence gathering</li>
                            <li>Review and approve AI-generated commands</li>
                            <li>Monitor execution and review findings</li>
                            <li>Export comprehensive intelligence reports</li>
                        </ol>
                    </div>
                </div>
                
                <div class="premium-card" style="margin-top: 32px; padding: 24px; border-left: 4px solid #06b6d4; background-color: rgba(6, 182, 212, 0.05);">
                    <h4 style="color: #22d3ee; margin-top: 0;">📋 Operating Doctrine</h4>
                    <p style="color: #cbd5e1; line-height: 1.8; margin: 0;">
                    This platform operates under strict <strong>passive reconnaissance protocols</strong>. 
                    All intelligence is gathered exclusively from publicly available sources without any direct 
                    interaction with target infrastructure. Each phase is carefully designed to maintain operational 
                    security and legal compliance while maximizing intelligence coverage.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
def main():
    """Main entry point"""
    app = NamespaceDominanceEngine()
    app.run()
    
if __name__ == "__main__":
    main()
