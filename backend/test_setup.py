import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_email():
    """Test email configuration"""
    print("🧪 Testing Email Setup...")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        msg = MIMEMultipart()
        msg['From'] = config['email']['sender_email']
        msg['To'] = config['email']['recipient_email']
        msg['Subject'] = "SIH Monitor Test - Email Working!"
        
        body = f"""
        ✅ Email Test Successful!
        
        Your SIH monitor email configuration is working correctly.
        
        Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        From: {config['email']['sender_email']}
        To: {config['email']['recipient_email']}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(config['email']['smtp_server'], config['email']['smtp_port'])
        server.starttls()
        server.login(config['email']['sender_email'], config['email']['sender_password'])
        server.send_message(msg)
        server.quit()
        
        print("✅ Email sent successfully! Check your inbox.")
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def test_whatsapp():
    """Test WhatsApp configuration"""
    print("🧪 Testing WhatsApp Setup...")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        if not config['whatsapp']['enabled']:
            print("⚠️  WhatsApp is disabled in config")
            return False
            
        from twilio.rest import Client
        
        client = Client(config['whatsapp']['twilio_sid'], config['whatsapp']['twilio_token'])
        
        message_body = f"""
🧪 SIH Monitor Test

✅ WhatsApp notification working!

Test Time: {datetime.now().strftime('%H:%M:%S')}

Your monitoring setup is ready! 🚀
        """
        
        message = client.messages.create(
            body=message_body,
            from_=config['whatsapp']['from_number'],
            to=config['whatsapp']['to_number']
        )
        
        print(f"✅ WhatsApp sent successfully! Message SID: {message.sid}")
        return True
        
    except ImportError:
        print("❌ Twilio not installed. Run: pip install twilio")
        return False
    except Exception as e:
        print(f"❌ WhatsApp test failed: {e}")
        print("💡 Make sure you've joined the Twilio sandbox and your phone number format is correct")
        return False

def test_web_scraping():
    """Test if we can access the SIH website"""
    print("🧪 Testing Web Scraping...")
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get("https://sih.gov.in/sih2025PS", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Successfully accessed SIH website")
            
            # Quick check if we can find problem statements
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')
            print(f"✅ Found {len(rows)} table rows")
            
            return True
        else:
            print(f"❌ Failed to access website. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Web scraping test failed: {e}")
        return False

def main():
    print("🚀 SIH Monitor Setup Test")
    print("=" * 40)
    
    # Test each component
    email_ok = test_email()
    print()
    
    whatsapp_ok = test_whatsapp()
    print()
    
    web_ok = test_web_scraping()
    print()
    
    # Summary
    print("📊 Test Summary:")
    print(f"Email: {'✅' if email_ok else '❌'}")
    print(f"WhatsApp: {'✅' if whatsapp_ok else '❌'}")
    print(f"Web Scraping: {'✅' if web_ok else '❌'}")
    
    if email_ok and web_ok:
        print("\n🎉 Ready to run the main monitor!")
        print("Run: python sih_monitor.py")
    else:
        print("\n⚠️  Fix the issues above before running the main script")

if __name__ == "__main__":
    main()