#!/usr/bin/env python3
"""
AMD ROCm vLLM Fraud Detection System
Module 6: End-to-End Fraud Detection Pipeline

This module orchestrates the complete fraud detection workflow from
data generation through analysis and report generation.
"""

import sys
import time
from datetime import datetime
import pandas as pd

# Import modules
try:
    from customer_data_generation import RiskyCustomerDataGenerator
    from ai_agent_framework import FraudAnalysisAgent
    from fraud_report_system import FraudReportGenerator
except ImportError:
    print("Warning: Could not import all modules. Make sure all modules are in the same directory.")


class FraudDetectionPipeline:
    """
    End-to-end fraud detection pipeline.
    """
    
    def __init__(self, config: dict = None):
        """Initialize pipeline with configuration."""
        self.config = config or self._default_config()
        self.pipeline_start = None
        self.pipeline_end = None
        self.results = {}
    
    def _default_config(self) -> dict:
        """
        Default pipeline configuration.
        """
        return {
            'num_customers': 1000,
            'output_dir': './',
            'gpu_type': 'rocm',
            'batch_size': 32,
            'verbose': True
        }
    
    def log(self, message: str, level: str = "INFO"):
        """
        Log message with timestamp.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def step_1_generate_customer_data(self):
        """
        Step 1: Generate risky customer data.
        """
        self.log("Step 1: Generating customer data", "START")
        
        try:
            generator = RiskyCustomerDataGenerator(seed=42)
            df = generator.generate_dataset(num_customers=self.config['num_customers'])
            
            # Save dataset
            output_file = f"{self.config['output_dir']}/risky_customers.csv"
            generator.save_dataset(df, output_file)
            
            self.results['customer_data'] = df
            
            stats = generator.generate_summary_stats(df)
            self.log(f"✓ Generated {len(df)} customer records", "SUCCESS")
            self.log(f"  Critical Risk: {stats.get('risk_distribution', {}).get('critical', 0)}", "INFO")
            self.log(f"  High Risk: {stats.get('risk_distribution', {}).get('high', 0)}", "INFO")
            self.log(f"  Sanctions Matches: {stats.get('sanctions_matches', 0)}", "INFO")
            
            return True
        
        except Exception as e:
            self.log(f"✗ Error generating customer data: {e}", "ERROR")
            return False
    
    def step_2_analyze_with_agent(self):
        """
        Step 2: Analyze customers with AI agent.
        """
        self.log("Step 2: Analyzing customers with AI Agent", "START")
        
        try:
            if 'customer_data' not in self.results:
                self.log("✗ Customer data not found. Run step 1 first.", "ERROR")
                return False
            
            agent = FraudAnalysisAgent()
            self.log(f"✓ Initialized agent: {agent.name}", "INFO")
            
            analysis_df = agent.analyze_batch(self.results['customer_data'])
            
            # Save analysis results
            output_file = f"{self.config['output_dir']}/fraud_analysis_results.csv"
            analysis_df.to_csv(output_file, index=False)
            
            self.results['analysis_results'] = analysis_df
            
            critical = len(analysis_df[analysis_df['risk_level'] == 'CRITICAL'])
            high = len(analysis_df[analysis_df['risk_level'] == 'HIGH'])
            
            self.log(f"✓ Analyzed {len(analysis_df)} customers", "SUCCESS")
            self.log(f"  Critical: {critical}", "INFO")
            self.log(f"  High: {high}", "INFO")
            
            return True
        
        except Exception as e:
            self.log(f"✗ Error analyzing customers: {e}", "ERROR")
            return False
    
    def step_3_generate_reports(self):
        """
        Step 3: Generate fraud reports and blocking actions.
        """
        self.log("Step 3: Generating fraud reports", "START")
        
        try:
            if 'analysis_results' not in self.results:
                self.log("✗ Analysis results not found. Run step 2 first.", "ERROR")
                return False
            
            report_gen = FraudReportGenerator()
            
            # Generate fraud report
            fraud_report = report_gen.generate_fraud_report(self.results['analysis_results'])
            fraud_report_file = f"{self.config['output_dir']}/fraud_detection_report.txt"
            with open(fraud_report_file, 'w') as f:
                f.write(fraud_report)
            
            self.log(f"✓ Generated fraud report: {fraud_report_file}", "SUCCESS")
            
            # Process blocking
            blocking_summary = report_gen.process_fraud_results(self.results['analysis_results'])
            
            blocking_report = report_gen.generate_blocking_report(blocking_summary)
            blocking_report_file = f"{self.config['output_dir']}/account_blocking_report.txt"
            with open(blocking_report_file, 'w') as f:
                f.write(blocking_report)
            
            self.log(f"✓ Generated blocking report: {blocking_report_file}", "SUCCESS")
            self.log(f"  Accounts Blocked: {blocking_summary['accounts_blocked']}", "INFO")
            self.log(f"  Accounts Flagged: {blocking_summary['accounts_flagged']}", "INFO")
            
            self.results['blocking_summary'] = blocking_summary
            
            return True
        
        except Exception as e:
            self.log(f"✗ Error generating reports: {e}", "ERROR")
            return False
    
    def run_pipeline(self):
        """
        Execute complete pipeline.
        """
        self.pipeline_start = datetime.now()
        
        print("\n" + "="*80)
        print("  AMD ROCm vLLM FRAUD DETECTION SYSTEM - COMPLETE PIPELINE")
        print("="*80 + "\n")
        
        self.log("Pipeline starting...", "START")
        self.log(f"Configuration: {self.config}", "INFO")
        
        # Execute pipeline steps
        success = True
        
        if not self.step_1_generate_customer_data():
            success = False
        
        if success and not self.step_2_analyze_with_agent():
            success = False
        
        if success and not self.step_3_generate_reports():
            success = False
        
        self.pipeline_end = datetime.now()
        
        if success:
            self.print_final_summary()
        else:
            self.log("Pipeline failed!", "ERROR")
        
        return success
    
    def print_final_summary(self):
        """
        Print final pipeline summary.
        """
        duration = (self.pipeline_end - self.pipeline_start).total_seconds()
        
        print("\n" + "="*80)
        print("  PIPELINE EXECUTION SUMMARY")
        print("="*80 + "\n")
        
        # Step summaries
        if 'customer_data' in self.results:
            print(f"✓ Step 1 - Data Generation:")
            print(f"    Customers Generated: {len(self.results['customer_data'])}")
        
        if 'analysis_results' in self.results:
            print(f"\n✓ Step 2 - Fraud Analysis:")
            analysis_df = self.results['analysis_results']
            print(f"    Critical: {len(analysis_df[analysis_df['risk_level'] == 'CRITICAL'])}")
            print(f"    High: {len(analysis_df[analysis_df['risk_level'] == 'HIGH'])}")
            print(f"    Medium: {len(analysis_df[analysis_df['risk_level'] == 'MEDIUM'])}")
            print(f"    Low: {len(analysis_df[analysis_df['risk_level'] == 'LOW'])}")
        
        if 'blocking_summary' in self.results:
            print(f"\n✓ Step 3 - Report Generation:")
            summary = self.results['blocking_summary']
            print(f"    Accounts Blocked: {summary['accounts_blocked']}")
            print(f"    Accounts Flagged: {summary['accounts_flagged']}")
        
        print(f"\n" + "="*80)
        print(f"Pipeline Status: SUCCESS")
        print(f"Total Duration: {duration:.2f} seconds")
        print(f"Completed: {self.pipeline_end.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"="*80 + "\n")


def main():
    """
    Main execution function.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="AMD ROCm vLLM Fraud Detection Pipeline")
    parser.add_argument('--num-customers', type=int, default=1000, help='Number of customers to generate')
    parser.add_argument('--output-dir', type=str, default='./', help='Output directory for results')
    parser.add_argument('--gpu-type', type=str, default='rocm', help='GPU type (rocm or cuda)')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size for processing')
    
    args = parser.parse_args()
    
    config = {
        'num_customers': args.num_customers,
        'output_dir': args.output_dir,
        'gpu_type': args.gpu_type,
        'batch_size': args.batch_size,
        'verbose': True
    }
    
    # Create and run pipeline
    pipeline = FraudDetectionPipeline(config=config)
    success = pipeline.run_pipeline()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
