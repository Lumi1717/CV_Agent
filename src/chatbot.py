import json
import os
import google.generativeai as genai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from .cv_data import load_cv_data
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def handle_recruiter_questions(question, api_key):
    """
    Handle recruiter questions about the candidate's CV
    
    Args:
        question (str): The question to answer
        api_key (str): Gemini API key
    
    Returns:
        str: The answer to the question
    """
    try:
        # Load CV data
        cv_data = load_cv_data()
        if not cv_data:
            return "Error: Could not load CV data. Please check if the CV file exists."
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Extract keywords from the question
        keywords = extract_keywords(question)
        
        # Find relevant sections based on keywords
        relevant_sections = find_relevant_sections(keywords, cv_data)
        
        # Generate answer using Gemini
        answer = generate_answers_with_gemini(
            question=question, 
            relevant_sections=relevant_sections, 
            cv_data=cv_data
        )
        
        return answer
        
    except Exception as e:
        return f"Error processing your question: {str(e)}"

def extract_keywords(question):
    """
    Extract keywords from the question for relevance matching
    
    Args:
        question (str): The input question
    
    Returns:
        list: List of keywords
    """
    if not question:
        return []
    
    # Convert to lowercase and split into words
    keywords = question.lower().split()
    
    # Filter out common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'what', 'when', 'where', 'how', 'why', 'who'}
    keywords = [word for word in keywords if word not in stop_words and len(word) > 2]
    
    return keywords

def find_relevant_sections(keywords, cv_data):
    """
    Find CV sections that are relevant to the keywords
    
    Args:
        keywords (list): List of keywords from the question
        cv_data (dict): The CV data
    
    Returns:
        list: List of relevant section names
    """
    relevant_sections = []
    
    if not keywords or not cv_data:
        return list(cv_data.keys()) if cv_data else []
    
    for section in cv_data:
        section_text = str(cv_data[section]).lower()
        if any(keyword in section_text for keyword in keywords):
            relevant_sections.append(section)
    
    # If no specific sections found, return all sections for comprehensive answer
    if not relevant_sections:
        relevant_sections = list(cv_data.keys())
    
    return relevant_sections

def generate_answers_with_gemini(question, relevant_sections, cv_data):
    """
    Generate answers using Gemini AI based on the question and relevant CV sections
    
    Args:
        question (str): The question to answer
        relevant_sections (list): List of relevant CV sections
        cv_data (dict): The complete CV data
    
    Returns:
        str: Generated answer
    """
    try:
        # Create focused data for relevant sections
        focused_data = {section: cv_data[section] for section in relevant_sections if section in cv_data}
        
        prompt_template = """
        You are an AI assistant helping to answer questions about Ahlam Yusuf's professional background and CV.
        
        **Question:** {question}
        
        **Relevant CV Information:** {focused_data}
        
        **Full CV Context:** {cv_data}
        
        **Instructions:**
        - Provide a concise, informative, and friendly answer based on the CV information
        - Keep your tone conversational and human-like, as if talking to a friend
        - Only answer based on the information provided in the CV
        - If the question asks for information not in the CV, respond with "I don't have that information in Ahlam's CV"
        - Focus on being helpful and accurate
        - Use specific details from the CV when possible
        - If asked about skills, experience, education, etc., provide concrete examples
        
        **Example Response Style:**
        - For skills questions: "Ahlam's top skills include [specific skills from CV]..."
        - For experience questions: "At [Company], Ahlam worked as [position] where she [specific achievements]..."
        - For education questions: "Ahlam has a [degree] from [institution]..."
        
        Remember to keep responses relevant to the CV content only.
        """
        
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        
        # Format the prompt with the actual data
        prompt_text = prompt_template.format(
            question=question,
            focused_data=json.dumps(focused_data, indent=2),
            cv_data=json.dumps(cv_data, indent=2)
        )
        
        # Generate response
        response = model.generate_content(prompt_text)
        
        # Extract the generated text from the response
        answer = response.text if response.text else "I'm sorry, I couldn't generate an answer to your question."
        
        return answer
        
    except Exception as e:
        return f"Error generating answer: {str(e)}. Please try rephrasing your question."
