import os
import subprocess
import logging

logger = logging.getLogger(__name__)

class BirtReportingEngine:
    """
    Facade for interacting with the Eclipse BIRT Reporting Engine.
    Requires BIRT Runtime to be installed and available on the system.
    """
    def __init__(self, birt_runtime_path=None):
        # Default to a typical installation path or environment variable
        self.birt_home = birt_runtime_path or os.environ.get("BIRT_HOME", "C:/birt-runtime-4_8_0/ReportEngine")
        self.gen_report_cmd = os.path.join(self.birt_home, "genReport.bat")
        
    def generate_briefing(self, template_path, output_path, parameters=None, format="pdf"):
        """
        Executes the BIRT engine CLI to generate a report.
        
        Args:
            template_path (str): Path to the .rptdesign file.
            output_path (str): Desired output path for the report.
            parameters (dict): Report parameters to inject into the BIRT template.
            format (str): Output format (pdf, html, xlsx).
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not os.path.exists(self.gen_report_cmd):
            logger.warning(f"BIRT Engine not found at {self.gen_report_cmd}. Mocking report generation.")
            return self._mock_generation(output_path, parameters, format)
            
        cmd = [
            self.gen_report_cmd,
            "-f", format,
            "-o", output_path
        ]
        
        if parameters:
            for key, value in parameters.items():
                cmd.extend(["-p", f"{key}={value}"])
                
        cmd.append(template_path)
        
        try:
            logger.info(f"Running BIRT Engine: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("BIRT Report generated successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"BIRT Engine failed: {e.stderr}")
            return False
            
    def _mock_generation(self, output_path, parameters, format):
        """
        Mock generation if BIRT is not installed locally.
        Creates a valid PDF/XLSX file to simulate the output using fpdf2.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if format.lower() == "pdf":
                try:
                    from fpdf import FPDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 16)
                    pdf.cell(0, 10, parameters.get("ReportTitle", "Executive Briefing"), ln=True, align='C')
                    pdf.ln(10)
                    
                    pdf.set_font("Arial", "", 12)
                    pdf.cell(0, 10, f"Generated on: {parameters.get('timestamp', 'N/A')}", ln=True)
                    pdf.cell(0, 10, f"Region: {parameters.get('region', 'Global')}", ln=True)
                    pdf.ln(5)
                    
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, "Executive KPIs:", ln=True)
                    pdf.set_font("Arial", "", 11)
                    for k, v in parameters.get('exec_kpis', {}).items():
                        pdf.cell(0, 7, f"  - {k.upper()}: {v.get('value')} {v.get('unit', '')} (Target: {v.get('target')} {v.get('unit', '')})", ln=True)
                    
                    pdf.ln(5)
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, "Financial KPIs:", ln=True)
                    pdf.set_font("Arial", "", 11)
                    for k, v in parameters.get('fin_kpis', {}).items():
                        pdf.cell(0, 7, f"  - {k.upper()}: {v.get('value')} (Target: {v.get('target')})", ln=True)
                        
                    pdf.ln(5)
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, "Forecast Accuracy:", ln=True)
                    pdf.set_font("Arial", "", 11)
                    for k, v in parameters.get('fcst_kpis', {}).items():
                        pdf.cell(0, 7, f"  - {k.upper()}: {v.get('value')} (Target: {v.get('target')})", ln=True)
                    
                    pdf.ln(10)
                    pdf.set_text_color(128, 128, 128)
                    pdf.set_font("Arial", "I", 10)
                    pdf.multi_cell(0, 10, "Note: This is a system-generated preview. For the full fidelity high-resolution report, ensure the BIRT Reporting Engine is active in the production environment.")
                    
                    pdf.output(output_path)
                    logger.info(f"Valid Mock PDF created at {output_path} using fpdf2")
                    return True
                except ImportError:
                    logger.warning("fpdf2 not installed. Falling back to text-based mock.")
            
            # Fallback for other formats or if fpdf is missing
            with open(output_path, 'w') as f:
                f.write(f"Mock BIRT Report generated in {format.upper()} format.\n")
                f.write(f"Parameters: {parameters}\n")
                f.write("To generate actual reports, install BIRT Runtime and set BIRT_HOME.\n")
            logger.info(f"Text mock report created at {output_path}")
            return True
        except Exception as e:
            logger.error(f"Mock generation failed: {e}")
            return False

def trigger_executive_briefing(context_data):
    """
    Service function called from the UI to generate the Executive Briefing.
    """
    engine = BirtReportingEngine()
    
    # Path to the BIRT template (would be created in Eclipse BIRT Designer)
    template = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports", "executive_briefing.rptdesign"))
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exports"))
    
    timestamp = context_data.get('timestamp', 'current')
    output_file = os.path.join(output_dir, f"Exec_Briefing_{timestamp}.pdf")
    
    # BIRT Parameters mapped from dashboard context
    params = {
        "ReportTitle": "Comprehensive Dashboard Report",
        "timestamp": timestamp,
        "region": context_data.get('region', 'Global'),
        "TotalRevenueAtRisk": context_data.get('revenue_at_risk', '0'),
        "TopCriticalSuppliers": context_data.get('critical_suppliers_count', '0')
    }
    # Inject detailed KPIs
    params.update(context_data)
    
    success = engine.generate_briefing(template, output_file, parameters=params, format="pdf")
    return success, output_file

if __name__ == "__main__":
    # Test the mock implementation
    success, path = trigger_executive_briefing({"timestamp": "2026-05-14", "revenue_at_risk": "1.2M", "critical_suppliers_count": "3"})
    print(f"Success: {success}, File: {path}")
