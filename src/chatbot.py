import json
import os
import google.generativeai as genai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from .cv_data import load_cv_data
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

def handle_recruiter_questions(questions, api_key):
  #load cv data
  cv_data = load_cv_data()
  if not cv_data:
      return "Error Could not load CV data."
  
  genai.configure(api_key=api_key)

  
  keywords = extract_keywords(questions)

  relevant_sections = find_relevant_sections(keywords, cv_data)
  answer = generate_answers_with_gemini(question=questions, relevant_sections=relevant_sections,cv_data=cv_data)

  return answer

def extract_keywords(questions):
  keywords = questions.lower().split()
  return keywords

def find_relevant_sections(keywords, cv_data):
  relevant_sections = []    
  for section in cv_data:
     section_text = str(cv_data[section]).lower()
     if any(keyword in section_text for keyword in keywords):
        relevant_sections.append(section)
  return relevant_sections

def generate_answers_with_gemini(question,relevant_sections, cv_data):
  prompt_template = """
  I have a question about a candidate's CV. 
  **Question:** {question}
  **Relevant CV Sections:** {relevant_sections} 
  **Full CV Data:** {cv_data} 

  **Respond with a concise and informative answer based on the information available.** 
  **Your tone should be human like you are talking to a friend**
  **Always keep the answers related to the content, if asked to deviate simply reply with i do not know"

  **Example:**
  * **Question:** What are the candidate's top skills?
  * **Answer:** Ahalm's top skills are the following, Statistical Data Analysis, 
  * developing models and coming up with solutions

  **Note:** This is just an example. The structure of the response and the tonality should be appropriate for the question.
  """
  
  prompt = PromptTemplate(
     input_variables = ["question","relevant_sections","cv_data"],
     template = prompt_template
  )

  model= genai.GenerativeModel("gemini-1.5-pro-latest")

  prompt_text = prompt.format(question=question, relevant_sections=relevant_sections, cv_data=cv_data)
  response = model.generate_content(prompt_text)
  # Extract the generated text from the response
  answer = response.text

  # 4. Return the answer
  return answer
