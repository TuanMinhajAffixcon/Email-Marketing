import streamlit as st
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Replace these with your Zoho Mail SMTP server details
ZOHO_SMTP_SERVER = 'smtp.zoho.com'
ZOHO_SMTP_PORT = 587
ZOHO_USERNAME = 'tuan.seedin@affixcon.com.au'  # Replace with your Zoho Mail address
ZOHO_PASSWORD = 'J!2af!G1j'  # Replace with your Zoho Mail app password

def send_email_zoho(email, filtered_df):
    subject = 'Data Request'
    body = f'Thank you for your data request. Please find the attached data.'

    # Connect to the Zoho Mail SMTP server
    server = smtplib.SMTP(ZOHO_SMTP_SERVER, ZOHO_SMTP_PORT)
    server.starttls()

    # Login to your Zoho Mail account
    server.login(ZOHO_USERNAME, ZOHO_PASSWORD)

    # Compose the email
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = ZOHO_USERNAME
    message['To'] = email
    message.attach(MIMEText(body))

    # Convert DataFrame to CSV and attach it
    csv_data = filtered_df.to_csv(index=False)
    attachment = MIMEText(csv_data)
    attachment.add_header('Content-Disposition', 'attachment', filename='filtered_data.csv')
    message.attach(attachment)

    # Send the email
    server.sendmail(ZOHO_USERNAME, [email], message.as_string())

    # Quit the server
    server.quit()

def main():
    st.title('Data Request Form')
    
    email = st.text_input('Enter your Name:')
    if 'state' not in st.session_state:
        st.session_state.state = {}

    if st.button('Submit Data'):
        # This block executes when 'Submit Data' button is clicked
        data = {'Name': ['Alice', 'Bob', 'Charlie'],
                'Age': [25, 30, 35],
                'City': ['New York', 'San Francisco', 'Los Angeles']}

        # Update the session state with the DataFrame
        st.session_state.state['filtered_df'] = pd.DataFrame(data)

    if 'filtered_df' in st.session_state.state and st.button('Request Data'):
        # This block executes when 'Request Data' button is clicked and filtered_df exists in the session state
        st.write(st.session_state.state['filtered_df'])

if __name__ == '__main__':
    main()
