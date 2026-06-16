#!/usr/bin/env python3
"""
AMD ROCm vLLM Fraud Detection System
Module 4: vLLM + AMD ROCm Integration

This module integrates vLLM with AMD ROCm for high-performance
GPU-accelerated fraud analysis and explanation generation.
"""

import os
from typing import List, Dict, Any
import json
import numpy as np


class VLLMFraudAnalyzer:
    """
    vLLM-based fraud analyzer with AMD ROCm GPU acceleration.
    """
    
    def __init__(self, model_name: str = "meta-llama/Llama-2-7b-hf", gpu_type: str = "rocm"):
        """
        Initialize vLLM fraud analyzer.
        
        Args:
            model_name: Name of the LLM model
            gpu_type: GPU type ('rocm' for AMD, 'cuda' for NVIDIA)
        """
        self.model_name = model_name
        self.gpu_type = gpu_type
        self.device = self._init_device()
        self.is_vllm_available = self._check_vllm()
        
        print(f"Initializing vLLM Fraud Analyzer")
        print(f"  Model: {self.model_name}")
        print(f"  GPU Type: {self.gpu_type}")
        print(f"  Device: {self.device}")
        print(f"  vLLM Available: {self.is_vllm_available}")
        
        if self.is_vllm_available:
            self._init_vllm()
    
    def _init_device(self) -> str:
        """
        Initialize GPU device.
        """
        try:
            if self.gpu_type == "rocm":
                import torch
                if torch.cuda.is_available():
                    device_count = torch.cuda.device_count()
                    device_name = torch.cuda.get_device_name(0)
                    return f"ROCm ({device_count} GPU(s), {device_name})"
                else:
                    return "CPU (ROCm GPU not available)"
            else:
                return "CUDA"
        except Exception as e:
            print(f"Warning: {e}")
            return "CPU"
    
    def _check_vllm(self) -> bool:
        """
        Check if vLLM is available.
        """
        try:
            import vllm
            return True
        except ImportError:
            print("Warning: vLLM not installed. Using fallback implementation.")
            return False
    
    def _init_vllm(self):
        """
        Initialize vLLM engine.
        """
        try:
            from vllm import LLM, SamplingParams
            
            # Initialize LLM with GPU settings
            self.llm = LLM(
                model=self.model_name,
                tensor_parallel_size=1,
                dtype="float16",
                gpu_memory_utilization=0.9,
                swap_space=4
            )
            
            self.sampling_params = SamplingParams(
                temperature=0.7,
                top_p=0.95,
                max_tokens=512
            )
            
            print("✓ vLLM engine initialized successfully")
        except Exception as e:
            print(f"Error initializing vLLM: {e}")
            self.is_vllm_available = False
    
    def generate_fraud_explanation(self, customer_data: Dict) -> str:
        """
        Generate detailed fraud explanation using vLLM.
        """
        if not self.is_vllm_available:
            return self._generate_fallback_explanation(customer_data)
        
        try:
            # Prepare prompt
            prompt = self._prepare_explanation_prompt(customer_data)
            
            # Generate explanation
            outputs = self.llm.generate([prompt], self.sampling_params)
            
            explanation = outputs[0].outputs[0].text.strip()
            return explanation
        
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return self._generate_fallback_explanation(customer_data)
    
    def _prepare_explanation_prompt(self, customer_data: Dict) -> str:
        """
        Prepare prompt for LLM.
        """
        prompt = f"""
        Analyze the following customer data for fraud risk and provide a detailed explanation:
        
        Customer ID: {customer_data.get('customer_id', 'N/A')}
        Name: {customer_data.get('full_name', 'N/A')}
        Country: {customer_data.get('country', 'N/A')}
        Account Age: {customer_data.get('account_age_days', 0)} days
        Risk Level: {customer_data.get('risk_level', 'N/A')}
        
        Risk Factors:
        - Country Risk: {customer_data.get('country_risk_level', 'N/A')}
        - Transaction Pattern: {customer_data.get('transaction_pattern', {}).get('type', 'N/A')}
        - PEP Status: {customer_data.get('pep_status', False)}
        - Sanctions Match: {customer_data.get('sanctions_list_match', False)}
        - KYC Completed: {customer_data.get('kyc_completed', False)}
        - Previous Alerts: {customer_data.get('previous_alerts', 0)}
        
        Provide a concise analysis of fraud risk:
        """
        return prompt
    
    def _generate_fallback_explanation(self, customer_data: Dict) -> str:
        """
        Generate explanation using rule-based system (fallback).
        """
        explanations = []
        
        # Country risk
        if customer_data.get('country_risk_level') == 'high':
            explanations.append(f"Customer is located in high-risk country: {customer_data.get('country')}")
        
        # Sanctions match
        if customer_data.get('sanctions_list_match'):
            explanations.append("Customer name matches OFAC sanctions list")
        
        # PEP status
        if customer_data.get('pep_status'):
            explanations.append("Customer flagged as Politically Exposed Person (PEP)")
        
        # Account age
        if customer_data.get('account_age_days', 0) < 30:
            explanations.append("Very new account with limited history")
        
        # Transaction patterns
        transaction_pattern = customer_data.get('transaction_pattern', {})
        if transaction_pattern.get('type') == 'structured':
            explanations.append("Suspicious transaction structuring detected")
        
        # KYC
        if not customer_data.get('kyc_completed', True):
            explanations.append("KYC process not completed")
        
        # Previous alerts
        if customer_data.get('previous_alerts', 0) > 10:
            explanations.append(f"Multiple previous fraud alerts: {customer_data.get('previous_alerts')}")
        
        if explanations:
            return " ".join(explanations)
        else:
            return "No significant fraud risk factors detected."
    
    def analyze_with_llm(self, customer_batch: List[Dict]) -> List[Dict]:
        """
        Analyze customer batch using vLLM.
        """
        results = []
        
        for customer in customer_batch:
            explanation = self.generate_fraud_explanation(customer)
            
            result = {
                'customer_id': customer.get('customer_id'),
                'vllm_analysis': explanation,
                'timestamp': self._get_timestamp()
            }
            
            results.append(result)
        
        return results
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp.
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def generate_batch_report(self, customers: List[Dict], fraud_scores: List[float]) -> Dict:
        """
        Generate comprehensive report for customer batch.
        """
        report = {
            'summary': {
                'total_customers': len(customers),
                'critical_cases': sum(1 for score in fraud_scores if score >= 0.81),
                'high_risk_cases': sum(1 for score in fraud_scores if 0.61 <= score < 0.81),
                'medium_risk_cases': sum(1 for score in fraud_scores if 0.31 <= score < 0.61),
                'low_risk_cases': sum(1 for score in fraud_scores if score < 0.31),
                'average_fraud_score': np.mean(fraud_scores),
                'max_fraud_score': np.max(fraud_scores),
                'min_fraud_score': np.min(fraud_scores)
            },
            'recommendations': self._generate_recommendations(fraud_scores),
            'gpu_stats': self._get_gpu_stats()
        }
        
        return report
    
    def _generate_recommendations(self, fraud_scores: List[float]) -> List[str]:
        """
        Generate recommendations based on fraud scores.
        """
        recommendations = []
        
        critical_count = sum(1 for score in fraud_scores if score >= 0.81)
        if critical_count > 0:
            recommendations.append(f"URGENT: {critical_count} accounts flagged as critical. Immediate action required.")
        
        high_risk_count = sum(1 for score in fraud_scores if 0.61 <= score < 0.81)
        if high_risk_count > 0:
            recommendations.append(f"HIGH PRIORITY: {high_risk_count} accounts require verification.")
        
        avg_score = np.mean(fraud_scores)
        if avg_score > 0.5:
            recommendations.append("Batch contains significant fraud risk. Enhanced monitoring recommended.")
        
        return recommendations
    
    def _get_gpu_stats(self) -> Dict:
        """
        Get GPU statistics.
        """
        stats = {
            'gpu_type': self.gpu_type,
            'device': self.device,
            'model': self.model_name
        }
        
        if self.gpu_type == "rocm":
            try:
                import torch
                if torch.cuda.is_available():
                    stats['gpu_memory_allocated'] = f"{torch.cuda.memory_allocated() / 1e9:.2f} GB"
                    stats['gpu_memory_reserved'] = f"{torch.cuda.memory_reserved() / 1e9:.2f} GB"
            except:
                pass
        
        return stats


def main():
    """
    Main execution function.
    """
    print("="*70)
    print("AMD ROCm vLLM Fraud Detection System")
    print("Module 4: vLLM + AMD ROCm Integration")
    print("="*70)
    
    # Initialize analyzer
    analyzer = VLLMFraudAnalyzer(gpu_type="rocm")
    
    # Example customer
    example_customer = {
        'customer_id': 'CUST-789456',
        'full_name': 'Ahmed Hassan',
        'country': 'Iran',
        'country_risk_level': 'high',
        'account_age_days': 5,
        'risk_level': 'CRITICAL',
        'pep_status': True,
        'sanctions_list_match': False,
        'kyc_completed': False,
        'previous_alerts': 15,
        'transaction_pattern': {'type': 'structured'}
    }
    
    # Generate explanation
    print("\nGenerating fraud explanation for sample customer...")
    explanation = analyzer.generate_fraud_explanation(example_customer)
    print(f"\nExplanation:\n{explanation}")
    
    print("\n" + "="*70)
    print("✓ vLLM integration completed successfully!")
    print("="*70)


if __name__ == "__main__":
    main()
