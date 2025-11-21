import json
import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from .cv_data import load_cv_data
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

# Global vector store (initialized once)
_vector_store = None

def calculate_total_experience(experience_list):
    """
    Calculate the total professional experience from a list of experience entries.
    Assumes experience_list is a list of dictionaries, each with 'start_date' and 'end_date' keys.
    'start_date' and 'end_date' are expected in 'YYYY-MM-DD' format.
    If 'end_date' is 'Present', it uses the current date.
    
    Args:
        experience_list (list): A list of dictionaries, each representing an experience entry.
    
    Returns:
        str: A formatted string representing the total experience (e.g., "5 years and 3 months").
    """
    total_months = 0
    
    for job in experience_list:
        start_date_str = job.get("start_date")
        end_date_str = job.get("end_date")

        if not start_date_str:
            continue

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            
            if end_date_str and end_date_str.lower() == "present":
                end_date = datetime.now()
            elif end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            else:
                continue # Skip if no end date and not 'Present'

            # Calculate months difference
            delta = end_date - start_date
            months_diff = delta.days / 30.44 # Average days in a month
            total_months += months_diff

        except ValueError:
            # Handle cases where date format might be incorrect
            print(f"Warning: Could not parse date for job: {job}")
            continue
            
    years = int(total_months // 12)
    months = int(total_months % 12)

    if years > 0 and months > 0:
        return f"{years} years and {months} months"
    elif years > 0:
        return f"{years} years"
    elif months > 0:
        return f"{months} months"
    else:
        return "Less than a month of experience"


def _create_vector_store(cv_data):
    """
    Create a FAISS vector store from CV data
    
    Args:
        cv_data (dict): The CV data dictionary
    
    Returns:
        FAISS: Vector store instance
    """
    # Convert CV data into documents
    documents = []
    
    # Add total experience summary
    total_experience_str = calculate_total_experience(cv_data.get("experience", []))
    cv_data["total_experience_summary"] = total_experience_str
    
    # Create documents from each section
    for section, content in cv_data.items():
        if isinstance(content, (dict, list)):
            content_str = json.dumps(content, indent=2)
        else:
            content_str = str(content)
        
        # Create a document with section name as metadata
        doc = Document(
            page_content=f"Section: {section}\n{content_str}",
            metadata={"section": section}
        )
        documents.append(doc)
    
    # Use a lightweight embedding model
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Create FAISS vector store
    vector_store = FAISS.from_documents(documents, embeddings)
    
    return vector_store


def _get_or_create_vector_store():
    """
    Get or create the global vector store (singleton pattern)
    
    Returns:
        FAISS: Vector store instance
    """
    global _vector_store
    
    if _vector_store is None:
        cv_data = load_cv_data()
        if not cv_data:
            raise ValueError("Could not load CV data")
        _vector_store = _create_vector_store(cv_data)
    
    return _vector_store


def handle_recruiter_questions(question, api_key):
    """
    Handle recruiter questions about the candidate's CV using LangChain and vector search
    
    Args:
        question (str): The question to answer
        api_key (str): Gemini API key
    
    Returns:
        str: The answer to the question
    """
    try:
        # Get or create vector store
        vector_store = _get_or_create_vector_store()
        
        # Initialize Gemini LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Create custom prompt with current_date included
        prompt_template = """You are an AI assistant helping to answer questions about Ahlam Yusuf's professional background and CV.

**Current Date for Reference:** {current_date}

**Question:** {question}

**Relevant CV Information:**
{context}

**Instructions:**
- Provide a concise, informative, and friendly answer based on the CV information
- Keep your tone conversational and human-like, as if talking to a friend
- Use a natural tone relevant to the topic and add a little gen z slang to make it more friendly and approachable
- Make it professional but with a joke here and there
- Only answer based on the information provided in the CV
- If the question asks for information not in the CV, respond with "I don't have that information in Ahlam's CV"
- Focus on being helpful and accurate
- Use specific details from the CV when possible

**Example of how to handle off-topic questions (e.g., code):**
"Wooooowww there buddy, that's out of my scope. Let's focus on the main show."

**Begin your answer now:**
"""
        
        # Format prompt with current_date
        formatted_prompt_template = prompt_template.format(
            current_date=current_date,
            question="{question}",
            context="{context}"
        )
        
        prompt = PromptTemplate(
            template=formatted_prompt_template,
            input_variables=["question", "context"]
        )
        
        # Create retrieval chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 3}),  # Get top 3 relevant chunks
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False
        )
        
        # Generate answer
        result = qa_chain.invoke({"query": question})
        
        answer = result.get("result", "I'm sorry, I do not know what you're talking about buddy.")
        
        return answer
        
    except Exception as e:
        return f"Oops 404 {str(e)}. Do you mind rephrasing that for me, I lost you there buddy."

