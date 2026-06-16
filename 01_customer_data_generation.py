#!/usr/bin/env python3
"""
AMD ROCm vLLM Fraud Detection System
Module 1: Customer Data Generation with High-Risk Attributes

This module generates synthetic customer data with realistic fraud patterns
including high-risk countries, sanctions lists, and prohibited names.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import pandas as pd
from faker import Faker
import numpy as np

class RiskyCustomerDataGenerator:
    """
    Generate synthetic customer data with high-risk attributes for fraud detection.
    """
    
    def __init__(self, seed: int = 42):
        """Initialize data generator with risk parameters."""
        self.fake = Faker()
        random.seed(seed)
        np.random.seed(seed)
        
        # Risk data
        self.high_risk_countries = {
            'KP': 'North Korea',
            'IR': 'Iran',
            'SY': 'Syria',
            'CU': 'Cuba',
            'SD': 'Sudan',
            'BY': 'Belarus',
            'VE': 'Venezuela'
        }
        
        self.medium_risk_countries = {
            'RU': 'Russia',
            'CN': 'China',
            'PK': 'Pakistan',
            'AF': 'Afghanistan'
        }
        
        # OFAC Sanctions List - Known terrorist/sanctioned individuals
        self.sanctions_names = [
            'Osama bin Laden',
            'Ayman al-Zawahiri',
            'Khalid Sheikh Mohammed',
            'Abu Yahya al-Libi',
            'Nasir al-Wuhayshi',
            'Anwar al-Awlaki',
            'Baitullah Mehsud',
            'Ilyas Kashmiri',
            'Noordin Top',
            'Ali Shukri Mansouri'
        ]
        
        # Prohibited names patterns
        self.prohibited_keywords = [
            'terror', 'jihad', 'bomb', 'weapon', 'explosive',
            'hamas', 'hezbollah', 'al-qaeda', 'isis', 'extremist'
        ]
    
    def generate_transaction_pattern(self) -> Dict:
        """
        Generate suspicious transaction patterns.
        """
        pattern_type = random.choice([
            'structured',  # Structuring (smurfing)
            'rapid',       # Rapid transfers
            'offshore',    # Offshore transfers
            'unusual',     # Unusual amount/timing
            'high_volume'  # High transaction volume
        ])
        
        return {
            'type': pattern_type,
            'frequency': random.randint(10, 100),  # transactions/day
            'avg_amount': random.uniform(1000, 100000),
            'destinations': random.randint(1, 50),  # number of destinations
            'time_pattern': random.choice(['night', 'random', 'weekend', 'all_hours'])
        }
    
    def generate_risky_customer(self) -> Dict:
        """
        Generate a single high-risk customer record.
        """
        risk_level = random.choices(['critical', 'high', 'medium', 'low'], 
                                   weights=[0.1, 0.2, 0.3, 0.4])[0]
        
        customer_id = f"CUST-{random.randint(100000, 999999)}"
        
        # Determine country risk
        if risk_level in ['critical', 'high']:
            country_code = random.choice(list(self.high_risk_countries.keys()))
            country_name = self.high_risk_countries[country_code]
        elif risk_level == 'medium':
            country_code = random.choice(list(self.medium_risk_countries.keys()))
            country_name = self.medium_risk_countries[country_code]
        else:
            country_code = random.choice(['US', 'GB', 'CA', 'DE', 'FR', 'JP'])
            country_name = self.fake.country()
        
        # Generate name
        if risk_level == 'critical':
            # Use sanctioned name
            first_name, last_name = random.choice(self.sanctions_names).split()
        else:
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
        
        # Account information
        account_opened = datetime.now() - timedelta(days=random.randint(0, 1000))
        
        customer = {
            'customer_id': customer_id,
            'first_name': first_name,
            'last_name': last_name,
            'full_name': f"{first_name} {last_name}",
            'email': self.fake.email(),
            'phone': self.fake.phone_number(),
            
            # Risk indicators
            'country_code': country_code,
            'country': country_name,
            'country_risk_level': 'high' if country_code in self.high_risk_countries else 'medium' if country_code in self.medium_risk_countries else 'low',
            
            # Account information
            'account_id': f"ACC-{random.randint(100000, 999999)}",
            'account_type': random.choice(['checking', 'savings', 'business']),
            'account_opened_date': account_opened.isoformat(),
            'account_age_days': (datetime.now() - account_opened).days,
            
            # KYC information
            'kyc_completed': random.choice([True, False]),
            'id_verified': random.choice([True, False]),
            'address': self.fake.address(),
            'date_of_birth': self.fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
            
            # Risk factors
            'pep_status': random.choice([True, False]) if risk_level in ['critical', 'high'] else False,
            'sanctions_list_match': risk_level == 'critical',
            'risk_level': risk_level,
            
            # Transaction patterns
            'transaction_pattern': self.generate_transaction_pattern(),
            
            # Behavioral indicators
            'login_frequency': random.randint(0, 50),  # logins/day
            'failed_login_attempts': random.randint(0, 10),
            'ip_changes': random.randint(0, 100),
            'device_changes': random.randint(0, 20),
            'suspicious_activity': random.choice([True, False]) if risk_level != 'low' else False,
            
            # Document flags
            'unusual_documents': random.choice([True, False]) if risk_level in ['critical', 'high'] else False,
            'document_mismatch': random.choice([True, False]) if risk_level != 'low' else False,
            
            # Beneficiary information
            'num_beneficiaries': random.randint(1, 20),
            'beneficiary_countries': random.sample(list(self.high_risk_countries.keys()) + list(self.medium_risk_countries.keys()), k=random.randint(1, 5)),
            
            # Previous alerts
            'previous_alerts': random.randint(0, 50),
            'alert_severity': random.choice(['none', 'low', 'medium', 'high']) if random.random() > 0.5 else 'none',
            
            # Generated fraud score
            'calculated_fraud_score': round(random.uniform(0, 100), 2)
        }
        
        return customer
    
    def generate_dataset(self, num_customers: int = 1000) -> pd.DataFrame:
        """
        Generate a complete dataset of risky customers.
        """
        print(f"Generating {num_customers} risky customer records...")
        
        customers = []
        for i in range(num_customers):
            customer = self.generate_risky_customer()
            customers.append(customer)
            
            if (i + 1) % 100 == 0:
                print(f"  Generated {i + 1}/{num_customers} customers")
        
        df = pd.DataFrame(customers)
        print(f"✓ Successfully generated {len(df)} customer records")
        return df
    
    def save_dataset(self, df: pd.DataFrame, filename: str = "risky_customers.csv"):
        """
        Save dataset to CSV file.
        """
        df.to_csv(filename, index=False)
        print(f"✓ Dataset saved to {filename}")
    
    def generate_summary_stats(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics of the dataset.
        """
        stats = {
            'total_customers': len(df),
            'risk_distribution': df['risk_level'].value_counts().to_dict(),
            'country_distribution': df['country'].value_counts().head(10).to_dict(),
            'sanctions_matches': df['sanctions_list_match'].sum(),
            'pep_flags': df['pep_status'].sum(),
            'avg_fraud_score': df['calculated_fraud_score'].mean(),
            'high_risk_accounts': len(df[df['risk_level'].isin(['critical', 'high'])]),
        }
        return stats


def main():
    """
    Main execution function.
    """
    print("="*70)
    print("AMD ROCm vLLM Fraud Detection System")
    print("Module 1: Risky Customer Data Generation")
    print("="*70)
    
    # Initialize generator
    generator = RiskyCustomerDataGenerator(seed=42)
    
    # Generate dataset
    df = generator.generate_dataset(num_customers=1000)
    
    # Save dataset
    generator.save_dataset(df, "risky_customers.csv")
    
    # Print summary statistics
    stats = generator.generate_summary_stats(df)
    print("\n" + "="*70)
    print("Dataset Summary Statistics:")
    print("="*70)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Print sample records
    print("\n" + "="*70)
    print("Sample High-Risk Customers:")
    print("="*70)
    high_risk_sample = df[df['risk_level'].isin(['critical', 'high'])].head(3)
    for idx, row in high_risk_sample.iterrows():
        print(f"\n  Customer: {row['full_name']}")
        print(f"    ID: {row['customer_id']}")
        print(f"    Country: {row['country']}")
        print(f"    Risk Level: {row['risk_level']}")
        print(f"    Fraud Score: {row['calculated_fraud_score']}")
        print(f"    Sanctions Match: {row['sanctions_list_match']}")
        print(f"    PEP Status: {row['pep_status']}")
    
    print("\n" + "="*70)
    print("✓ Customer data generation completed successfully!")
    print("="*70)


if __name__ == "__main__":
    main()
