import requests
from bs4 import BeautifulSoup
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import schedule
import logging
from config_loader import load_config, load_problem_config

class SIHSubmissionMonitor:
    def __init__(self, config_file='config.json', problem_config_file='problem_config.json'):
        """
        Initialize the monitor with configuration
        """
        # Use the new config loader that supports environment variables
        self.config = load_config()
        self.problem_config = load_problem_config()
        self.url = "https://sih.gov.in/sih2025PS"
        self.target_id = self.problem_config.get('problem_statement_id', '25057')
        self.last_count = None
        self.setup_logging()
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config if not exists (without problem_id)
            default_config = {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "your_email@gmail.com",
                    "sender_password": "your_app_password",
                    "recipient_email": "recipient@gmail.com"
                },
                "whatsapp": {
                    "enabled": False,
                    "twilio_sid": "your_twilio_sid",
                    "twilio_token": "your_twilio_token",
                    "from_number": "whatsapp:+1234567890",
                    "to_number": "whatsapp:+0987654321"
                }
            }
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default config file: {config_file}")
            print("Please update the configuration with your credentials.")
            return default_config
    
    def load_problem_config(self, problem_config_file):
        """Load problem statement configuration from dedicated file"""
        try:
            with open(problem_config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default problem config if not exists
            default_problem_config = {
                "problem_statement_id": "25057",
                "description": "SIH 2025 Problem Statement ID to monitor",
                "last_updated": "2025-09-18",
                "notes": "Change this ID to monitor a different problem statement. The system will automatically pick up changes on restart."
            }
            with open(problem_config_file, 'w') as f:
                json.dump(default_problem_config, f, indent=2)
            print(f"Created default problem config file: {problem_config_file}")
            return default_problem_config
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sih_monitor.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_session_with_headers(self):
        """Create a session with proper headers to avoid blocking"""
        import os
        session = requests.Session()
        
        # Add proxy support if environment variable is set
        proxy_url = os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY')
        if proxy_url:
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            self.logger.info(f"Using proxy: {proxy_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Referer': 'https://www.google.com/',
        }
        session.headers.update(headers)
        return session
    
    def fetch_page_content(self):
        """Fetch the SIH page content with retry logic"""
        import random
        session = self.get_session_with_headers()
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Fetching page content (attempt {attempt + 1})")
                
                # Add random delay to avoid rate limiting
                if attempt > 0:
                    delay = random.uniform(10, 30) + (attempt * 5)
                    self.logger.info(f"Waiting {delay:.1f} seconds before retry...")
                    time.sleep(delay)
                
                # Add a small random delay even on first attempt
                time.sleep(random.uniform(2, 5))
                
                response = session.get(self.url, timeout=45, allow_redirects=True)
                
                # Check for specific error responses
                if response.status_code == 403:
                    self.logger.warning(f"403 Forbidden - Server is blocking requests")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        raise requests.exceptions.HTTPError(f"403 Forbidden after {max_retries} attempts")
                
                response.raise_for_status()
                return response.text
            
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    continue
                else:
                    # On final failure, try to provide more context
                    if "403" in str(e):
                        self.logger.error("Server is consistently blocking requests. This might be due to:")
                        self.logger.error("1. Rate limiting or anti-bot measures")
                        self.logger.error("2. IP-based blocking")
                        self.logger.error("3. Changes in website security")
                    raise
    
    def parse_submission_count(self, html_content):
        """Parse HTML to extract submission count for target problem ID"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all table rows
        rows = soup.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            
            if len(cells) >= 15:  # Based on debug output, we need at least 15 columns
                try:
                    # Method 1: Check SIH code column (position 14, 0-indexed)
                    sih_code_cell = cells[14] if len(cells) > 14 else None
                    if sih_code_cell and f"SIH{self.target_id}" in sih_code_cell.get_text().strip():
                        # Submission count is in position 15 (0-indexed)
                        submission_count = cells[15].get_text().strip()
                        self.logger.info(f"Found via SIH code: {submission_count}")
                        return int(submission_count)
                    
                    # Method 2: Check problem ID column (position 3, 0-indexed)
                    problem_id_cell = cells[3] if len(cells) > 3 else None
                    if problem_id_cell and self.target_id in problem_id_cell.get_text().strip():
                        # Submission count is in position 15 (0-indexed)
                        submission_count = cells[15].get_text().strip()
                        self.logger.info(f"Found via Problem ID: {submission_count}")
                        return int(submission_count)
                        
                except (ValueError, IndexError) as e:
                    continue
        
        # Fallback: Search in all text content
        all_text = soup.get_text()
        if f"SIH{self.target_id}" in all_text:
            self.logger.warning(f"Found SIH{self.target_id} in page but couldn't parse submission count")
            self.logger.warning("The page structure might have changed")
            
            # Try to find it manually in the raw text
            import re
            pattern = f"SIH{self.target_id}.*?(\\d+)"
            match = re.search(pattern, all_text)
            if match:
                count = int(match.group(1))
                self.logger.info(f"Found via regex fallback: {count}")
                return count
        
        raise ValueError(f"Could not find problem statement with ID {self.target_id}")
    
    def send_email_notification(self, current_count, previous_count):
        """Send email notification about count change"""
        if not self.config['email']['enabled']:
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['sender_email']
            msg['To'] = self.config['email']['recipient_email']
            msg['Subject'] = f"SIH Submission Count Update - Problem ID {self.target_id}"
            
            body = f"""
            SIH Submission Count Update
            
            Problem Statement ID: {self.target_id}
            Previous Count: {previous_count if previous_count is not None else 'N/A'}
            Current Count: {current_count}
            Change: {'+' if previous_count is None else ''}{current_count - (previous_count or 0)}
            
            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            URL: {self.url}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['sender_email'], self.config['email']['sender_password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info("Email notification sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
    
    def send_whatsapp_notification(self, current_count, previous_count):
        """Send WhatsApp notification using Twilio"""
        if not self.config['whatsapp']['enabled']:
            return
            
        try:
            from twilio.rest import Client
            
            client = Client(self.config['whatsapp']['twilio_sid'], self.config['whatsapp']['twilio_token'])
            
            message_body = f"""
SIH Submission Update

Problem ID: {self.target_id}
Previous: {previous_count or 'N/A'}
Current: {current_count}
Change: {'+' if previous_count is None else ''}{current_count - (previous_count or 0)}

Time: {datetime.now().strftime('%H:%M:%S')}
            """
            
            message = client.messages.create(
                body=message_body,
                from_=self.config['whatsapp']['from_number'],
                to=self.config['whatsapp']['to_number']
            )
            
            self.logger.info(f"WhatsApp notification sent: {message.sid}")
            
        except Exception as e:
            self.logger.error(f"Failed to send WhatsApp notification: {e}")
    
    def check_submissions(self):
        """Main method to check submission count"""
        try:
            self.logger.info("Starting submission count check...")
            
            # Fetch and parse the page
            html_content = self.fetch_page_content()
            current_count = self.parse_submission_count(html_content)
            
            self.logger.info(f"Current submission count for ID {self.target_id}: {current_count}")
            
            # Check if count has changed
            if self.last_count is not None and current_count != self.last_count:
                self.logger.info(f"Count changed from {self.last_count} to {current_count}")
                
                # Send notifications
                self.send_email_notification(current_count, self.last_count)
                self.send_whatsapp_notification(current_count, self.last_count)
            
            elif self.last_count is None:
                self.logger.info("First run - establishing baseline count")
                self.send_email_notification(current_count, None)
            
            # Update last known count
            self.last_count = current_count
            
            # Save state
            self.save_state()
            
        except Exception as e:
            self.logger.error(f"Error during submission check: {e}")
            
            # If it's a 403 error, provide specific guidance
            if "403" in str(e) or "Forbidden" in str(e):
                self.logger.error("The website is blocking requests. Possible solutions:")
                self.logger.error("1. The site may have implemented stronger anti-bot measures")
                self.logger.error("2. Try accessing from a different IP address")
                self.logger.error("3. Consider using a proxy service")
                self.logger.error("4. Check if the website structure has changed")
                
                # Send notification about the blocking
                try:
                    self.send_error_notification(str(e))
                except Exception as notify_err:
                    self.logger.error(f"Failed to send error notification: {notify_err}")
    
    def send_error_notification(self, error_message):
        """Send notification about monitoring errors"""
        if not self.config['email']['enabled']:
            return
            
        try:
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            import smtplib
            
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['sender_email']
            msg['To'] = self.config['email']['recipient_email']
            msg['Subject'] = f"SIH Monitor Error - Problem ID {self.target_id}"
            
            body = f"""
            SIH Monitor Error Alert
            
            Problem Statement ID: {self.target_id}
            Error: {error_message}
            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            The monitoring system encountered an error and may need attention.
            
            If this is a 403 Forbidden error, the website may be blocking automated requests.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['sender_email'], self.config['email']['sender_password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info("Error notification sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send error notification: {e}")
    
    def save_state(self):
        """Save current state to file"""
        state = {
            'last_count': self.last_count,
            'last_check': datetime.now().isoformat(),
            'target_id': self.target_id,
            'problem_id': self.target_id  # For frontend compatibility
        }
        with open('monitor_state.json', 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self):
        """Load previous state if exists"""
        try:
            with open('monitor_state.json', 'r') as f:
                state = json.load(f)
                self.last_count = state.get('last_count')
                self.logger.info(f"Loaded previous state: last_count = {self.last_count}")
        except FileNotFoundError:
            self.logger.info("No previous state found, starting fresh")
    
    def run_scheduler(self):
        """Run the monitoring with 12-hour intervals"""
        self.logger.info("Starting SIH Submission Monitor")
        self.load_state()
        
        # Schedule the job every 12 hours
        schedule.every(12).hours.do(self.check_submissions)
        
        # Run once immediately
        self.check_submissions()
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute if it's time to run

def main():
    """Main function to run the monitor"""
    monitor = SIHSubmissionMonitor()
    
    # For testing, you can run a single check
    # monitor.check_submissions()
    
    # For continuous monitoring every 12 hours
    monitor.run_scheduler()

if __name__ == "__main__":
    main()