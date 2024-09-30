import os
import requests
from dotenv import load_dotenv  # Library to load environment variables
from bs4 import BeautifulSoup  # Library for parsing HTML
from openai import OpenAI  # OpenAI library to interact with the API
import streamlit as st  # Streamlit library for creating web apps


class WebsiteSummarizer:
    def __init__(self, url):
        # Load environment variables and set OpenAI API key
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY', 'your-key-if-not-using-env')
        self.url = url  # URL of the website to be summarized
        self.title = None  # Title of the website
        self.text = None  # Text content of the website
        self.system_prompt = (  # System prompt for the AI assistant
            "You are an assistant that analyzes the contents of a website "
            "and provides a short summary, ignoring text that might be navigation related. "
            "Respond in markdown."
        )

        # Extract the website's content
        self.extract_website_content()

    def extract_website_content(self):
        """Extracts the title and relevant text from the website."""
        response = requests.get(self.url)  # Send GET request to the URL
        soup = BeautifulSoup(response.content, 'html.parser')  # Parse HTML content using BeautifulSoup
        self.title = soup.title.string if soup.title else "No title found"  # Get website title if available

        # Remove irrelevant tags like script, style, img, and input
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()

        # Get clean text from the body of the website
        self.text = soup.body.get_text(separator="\n", strip=True)

    def user_prompt_for(self):
        """Generates the prompt for the user message based on the website's content."""
        user_prompt = f"You are looking at a website titled '{self.title}'. "
        user_prompt += ("The contents of this website are as follows; "
                        "please provide a short summary of this website in markdown. ")
        user_prompt += ("If it includes news or announcements, "
                        "then summarize these too and include the main links with the summary.\n\n")
        user_prompt += self.text
        return user_prompt

    def messages_for(self):
        """Prepares the messages to be sent to the OpenAI API."""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt_for()}
        ]

    def summarize(self):
        """Generates a summary of the website content using OpenAI API."""
        openai_client = OpenAI(api_key=self.api_key)  # Initialize OpenAI client with API key
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Select the model to use
            messages=self.messages_for()  # Send prepared messages
        )
        return response.choices[0].message.content  # Return the summary from the API response

    def display_summary(self):
        """Returns the summary of the website content for display."""
        summary = self.summarize()
        return summary


# Integration with Streamlit
st.title("Website Summarizer")  # Display the title of the web application
st.write("Enter the URL of a website to get a summary of its content.")  # Instruction for the user

# Input field for the URL
url_input = st.text_input("Website URL:", value="https://example.com")

# Button to trigger summary generation
if st.button("Generate Summary"):
    if url_input:
        # Create an instance of the WebsiteSummarizer class
        summarizer = WebsiteSummarizer(url_input)

        # Display the website's title
        st.subheader(f"Website Title: {summarizer.title}")

        # Generate and display the summary
        summary = summarizer.display_summary()
        st.markdown(summary)
    else:
        st.warning("Please enter a valid URL.")  # Warning message if URL is empty
