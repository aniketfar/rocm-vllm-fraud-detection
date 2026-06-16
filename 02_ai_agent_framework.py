#!/usr/bin/env python3
"""
AMD ROCm vLLM Fraud Detection System
Module 2: AI Agent Framework for Fraud Analysis

This module implements an intelligent agent system for analyzing customer
data and identifying fraudulent patterns.
"""

import json
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
from enum import Enum
import pandas as pd
import numpy as np
from datetime import datetime


class RiskLevel(Enum):
    """Risk level enumeration."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AgentAction(Enum):
    """Agent action enumeration."""
    BLOCK_ACCOUNT = "BLOCK_ACCOUNT"
    FREEZE_TRANSACTION = "FREEZE_TRANSACTION"
    FLAG_FOR_REVIEW = "FLAG_FOR_REVIEW"
    REQUEST_VERIFICATION = "REQUEST_VERIFICATION"
    MONITOR = "MONITOR"
    CLEAR = "CLEAR"


@dataclass
class FraudAnalysisResult:
    """Result of fraud analysis for a customer."""
    customer_id: str
    risk_score: float
    risk_level: RiskLevel
    fraud_indicators: List[str]
    recommended_actions: List[AgentAction]
    confidence: float
    explanation: str
    timestamp: str


class FraudAnalysisAgent:
    """
    AI Agent for fraud analysis and decision making.
    """
    
    def __init__(self):
        """Initialize the fraud analysis agent."""
        self.name = "FraudAnalysisAgent_v1"
        self.version = "1.0.0"
        self.analysis_history = []
        
        # Risk thresholds
        self.thresholds = {
            'critical': 0.81,
            'high': 0.61,
            'medium': 0.31,
            'low': 0.0
        }
        
        # Risk weights
        self.risk_weights = {
            'country_risk': 0.30,
            'transaction_anomaly': 0.25,
            'name_match': 0.20,
            'behavioral_pattern': 0.15,
            'account_age': 0.10
        }
    
    def analyze_country_risk(self, customer: Dict) -> Tuple[float, str]:
        """
        Analyze country-based risk.
        """
        high_risk_countries = ['KP', 'IR', 'SY', 'CU', 'SD', 'BY', 'VE']
        medium_risk_countries = ['RU', 'CN', 'PK', 'AF']
        
        country_code = customer.get('country_code', '')
        
        if country_code in high_risk_countries:
            return 0.95, "High-risk country location"
        elif country_code in medium_risk_countries:
            return 0.60, "Medium-risk country location"
        else:
            return 0.10, "Low-risk country location"
    
    def analyze_transaction_anomaly(self, customer: Dict) -> Tuple[float, str]:
        """
        Analyze transaction patterns for anomalies.
        """
        transaction_pattern = customer.get('transaction_pattern', {})
        pattern_type = transaction_pattern.get('type', '')
        
        anomaly_scores = {
            'structured': 0.95,      # Structuring is highly suspicious
            'rapid': 0.85,           # Rapid transfers
            'offshore': 0.75,        # Offshore transfers
            'unusual': 0.65,         # Unusual patterns
            'high_volume': 0.70      # High volume transactions
        }
        
        score = anomaly_scores.get(pattern_type, 0.10)
        explanation = f"Transaction pattern: {pattern_type}"
        
        return score, explanation
    
    def analyze_name_match(self, customer: Dict) -> Tuple[float, str]:
        """
        Analyze name against sanctions and prohibited lists.
        """
        sanctions_list = [
            'osama bin laden', 'ayman al-zawahiri', 'khalid sheikh mohammed',
            'abu yahya al-libi', 'nasir al-wuhayshi', 'anwar al-awlaki'
        ]
        
        full_name = customer.get('full_name', '').lower()
        
        # Exact match
        if full_name in sanctions_list:
            return 0.99, "OFAC sanctions list match"
        
        # Partial match
        for name in sanctions_list:
            if name in full_name:
                return 0.85, "Partial sanctions list match"
        
        # Check for prohibited keywords
        prohibited_keywords = ['terror', 'jihad', 'bomb', 'weapon', 'explosive']
        for keyword in prohibited_keywords:
            if keyword in full_name:
                return 0.90, "Prohibited keyword in name"
        
        return 0.05, "No name match alerts"
    
    def analyze_behavioral_pattern(self, customer: Dict) -> Tuple[float, str]:
        """
        Analyze behavioral indicators.
        """
        score = 0.0
        indicators = []
        
        # KYC completion
        if not customer.get('kyc_completed', True):
            score += 0.30
            indicators.append("KYC not completed")
        
        # ID verification
        if not customer.get('id_verified', True):
            score += 0.25
            indicators.append("ID not verified")
        
        # Failed login attempts
        failed_attempts = customer.get('failed_login_attempts', 0)
        if failed_attempts > 5:
            score += 0.20
            indicators.append(f"Multiple failed logins: {failed_attempts}")
        
        # IP changes
        ip_changes = customer.get('ip_changes', 0)
        if ip_changes > 20:
            score += 0.15
            indicators.append(f"Frequent IP changes: {ip_changes}")
        
        # Device changes
        device_changes = customer.get('device_changes', 0)
        if device_changes > 10:
            score += 0.15
            indicators.append(f"Multiple device changes: {device_changes}")
        
        # Previous alerts
        previous_alerts = customer.get('previous_alerts', 0)
        if previous_alerts > 10:
            score += 0.20
            indicators.append(f"Previous fraud alerts: {previous_alerts}")
        
        # Suspicious activity flag
        if customer.get('suspicious_activity', False):
            score += 0.25
            indicators.append("Suspicious activity detected")
        
        # Beneficiary risk
        beneficiary_countries = customer.get('beneficiary_countries', [])
        high_risk_countries = ['KP', 'IR', 'SY', 'CU', 'SD']
        risky_beneficiaries = sum(1 for c in beneficiary_countries if c in high_risk_countries)
        if risky_beneficiaries > 0:
            score += 0.15 * risky_beneficiaries
            indicators.append(f"High-risk beneficiaries: {risky_beneficiaries}")
        
        # Cap score at 1.0
        score = min(score, 1.0)
        explanation = "; ".join(indicators) if indicators else "No behavioral alerts"
        
        return score, explanation
    
    def analyze_account_age(self, customer: Dict) -> Tuple[float, str]:
        """
        Analyze account age indicator.
        """
        account_age = customer.get('account_age_days', 0)
        
        # New accounts are riskier
        if account_age < 7:
            return 0.95, "Very new account (< 7 days)"
        elif account_age < 30:
            return 0.75, "New account (< 30 days)"
        elif account_age < 90:
            return 0.50, "Recent account (< 90 days)"
        elif account_age < 365:
            return 0.25, "Account < 1 year old"
        else:
            return 0.05, "Established account (> 1 year)"
    
    def calculate_fraud_score(self, customer: Dict) -> Tuple[float, Dict]:
        """
        Calculate overall fraud score using weighted components.
        """
        # Analyze each component
        country_score, country_exp = self.analyze_country_risk(customer)
        transaction_score, transaction_exp = self.analyze_transaction_anomaly(customer)
        name_score, name_exp = self.analyze_name_match(customer)
        behavioral_score, behavioral_exp = self.analyze_behavioral_pattern(customer)
        account_age_score, account_age_exp = self.analyze_account_age(customer)
        
        # Calculate weighted score
        fraud_score = (
            country_score * self.risk_weights['country_risk'] +
            transaction_score * self.risk_weights['transaction_anomaly'] +
            name_score * self.risk_weights['name_match'] +
            behavioral_score * self.risk_weights['behavioral_pattern'] +
            account_age_score * self.risk_weights['account_age']
        )
        
        component_scores = {
            'country_risk': round(country_score, 3),
            'transaction_anomaly': round(transaction_score, 3),
            'name_match': round(name_score, 3),
            'behavioral_pattern': round(behavioral_score, 3),
            'account_age': round(account_age_score, 3)
        }
        
        component_explanations = {
            'country_risk': country_exp,
            'transaction_anomaly': transaction_exp,
            'name_match': name_exp,
            'behavioral_pattern': behavioral_exp,
            'account_age': account_age_exp
        }
        
        return round(fraud_score, 3), component_scores, component_explanations
    
    def determine_risk_level(self, fraud_score: float) -> RiskLevel:
        """
        Determine risk level based on fraud score.
        """
        if fraud_score >= self.thresholds['critical']:
            return RiskLevel.CRITICAL
        elif fraud_score >= self.thresholds['high']:
            return RiskLevel.HIGH
        elif fraud_score >= self.thresholds['medium']:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def determine_actions(self, fraud_score: float, customer: Dict) -> List[AgentAction]:
        """
        Determine recommended actions based on fraud score.
        """
        actions = []
        risk_level = self.determine_risk_level(fraud_score)
        
        if risk_level == RiskLevel.CRITICAL:
            actions.append(AgentAction.BLOCK_ACCOUNT)
            actions.append(AgentAction.FREEZE_TRANSACTION)
        elif risk_level == RiskLevel.HIGH:
            actions.append(AgentAction.FREEZE_TRANSACTION)
            actions.append(AgentAction.REQUEST_VERIFICATION)
        elif risk_level == RiskLevel.MEDIUM:
            actions.append(AgentAction.FLAG_FOR_REVIEW)
            actions.append(AgentAction.REQUEST_VERIFICATION)
        else:
            actions.append(AgentAction.MONITOR)
        
        # Additional checks
        if customer.get('sanctions_list_match', False):
            actions = [AgentAction.BLOCK_ACCOUNT]
        elif customer.get('pep_status', False):
            if AgentAction.BLOCK_ACCOUNT not in actions:
                actions.append(AgentAction.REQUEST_VERIFICATION)
        
        return actions
    
    def analyze_customer(self, customer: Dict) -> FraudAnalysisResult:
        """
        Perform complete fraud analysis on a customer.
        """
        # Calculate fraud score
        fraud_score, component_scores, explanations = self.calculate_fraud_score(customer)
        
        # Determine risk level
        risk_level = self.determine_risk_level(fraud_score)
        
        # Collect fraud indicators
        fraud_indicators = [
            exp for exp in explanations.values() 
            if exp not in ["No behavioral alerts", "Low-risk country location", "No name match alerts"]
        ]
        
        # Determine recommended actions
        recommended_actions = self.determine_actions(fraud_score, customer)
        
        # Calculate confidence
        confidence = min(fraud_score * 1.2, 0.99) if fraud_score > 0.5 else fraud_score
        
        # Generate explanation
        explanation = (
            f"Fraud Score: {fraud_score}. "
            f"Component Analysis: Country Risk ({component_scores['country_risk']}), "
            f"Transaction Anomaly ({component_scores['transaction_anomaly']}), "
            f"Name Match ({component_scores['name_match']}), "
            f"Behavioral Pattern ({component_scores['behavioral_pattern']}), "
            f"Account Age ({component_scores['account_age']})."
        )
        
        result = FraudAnalysisResult(
            customer_id=customer.get('customer_id', 'UNKNOWN'),
            risk_score=fraud_score,
            risk_level=risk_level,
            fraud_indicators=fraud_indicators,
            recommended_actions=recommended_actions,
            confidence=confidence,
            explanation=explanation,
            timestamp=datetime.now().isoformat()
        )
        
        self.analysis_history.append(result)
        return result
    
    def analyze_batch(self, customers_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze a batch of customers.
        """
        results = []
        
        for idx, row in customers_df.iterrows():
            customer_dict = row.to_dict()
            result = self.analyze_customer(customer_dict)
            
            results.append({
                'customer_id': result.customer_id,
                'risk_score': result.risk_score,
                'risk_level': result.risk_level.value,
                'fraud_indicators': ';'.join(result.fraud_indicators),
                'recommended_actions': ';'.join([a.value for a in result.recommended_actions]),
                'confidence': result.confidence,
                'explanation': result.explanation,
                'timestamp': result.timestamp
            })
            
            if (idx + 1) % 100 == 0:
                print(f"  Analyzed {idx + 1} customers")
        
        return pd.DataFrame(results)


def main():
    """
    Main execution function.
    """
    print("="*70)
    print("AMD ROCm vLLM Fraud Detection System")
    print("Module 2: AI Agent Framework")
    print("="*70)
    
    # Initialize agent
    agent = FraudAnalysisAgent()
    print(f"\n✓ Agent initialized: {agent.name} v{agent.version}")
    
    # Load customer data
    try:
        df = pd.read_csv('risky_customers.csv')
        print(f"✓ Loaded {len(df)} customer records")
    except FileNotFoundError:
        print("✗ risky_customers.csv not found. Run Module 1 first.")
        return
    
    # Analyze batch
    print("\nAnalyzing customers...")
    analysis_df = agent.analyze_batch(df)
    
    # Save results
    analysis_df.to_csv('fraud_analysis_results.csv', index=False)
    print("\n✓ Analysis results saved to fraud_analysis_results.csv")
    
    # Print summary
    print("\n" + "="*70)
    print("Analysis Summary:")
    print("="*70)
    print(f"Total customers analyzed: {len(analysis_df)}")
    print(f"Critical risk: {len(analysis_df[analysis_df['risk_level'] == 'CRITICAL'])}")
    print(f"High risk: {len(analysis_df[analysis_df['risk_level'] == 'HIGH'])}")
    print(f"Medium risk: {len(analysis_df[analysis_df['risk_level'] == 'MEDIUM'])}")
    print(f"Low risk: {len(analysis_df[analysis_df['risk_level'] == 'LOW'])}")
    
    # Print critical cases
    print("\n" + "="*70)
    print("Critical Risk Customers:")
    print("="*70)
    critical_df = analysis_df[analysis_df['risk_level'] == 'CRITICAL'].head(5)
    for idx, row in critical_df.iterrows():
        print(f"\n  Customer: {row['customer_id']}")
        print(f"    Risk Score: {row['risk_score']}")
        print(f"    Actions: {row['recommended_actions']}")
        print(f"    Indicators: {row['fraud_indicators']}")
    
    print("\n" + "="*70)
    print("✓ Agent analysis completed successfully!")
    print("="*70)


if __name__ == "__main__":
    main()
