import json
import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from .cv_data import load_cv_data
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

# Global vector store (initialized once)
_vector_store = None

def _parse_date(date_str):
    """
    Parse date string in various formats: "YYYY-MM-DD", "Month YYYY", or "MM/YYYY"
    
    Args:
        date_str (str): Date string to parse
    
    Returns:
        datetime: Parsed datetime object
    """
    if not date_str:
        raise ValueError("Empty date string")
    
    date_str = date_str.strip()
    
    # Try "YYYY-MM-DD" format first
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass
    
    # Try "Month YYYY" format (e.g., "May 2023")
    month_names = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    
    parts = date_str.lower().split()
    if len(parts) == 2:
        month_str, year_str = parts
        if month_str in month_names and year_str.isdigit():
            try:
                return datetime(int(year_str), month_names[month_str], 1)
            except ValueError:
                pass
    
    # Try "MM/YYYY" format
    if "/" in date_str:
        try:
            parts = date_str.split("/")
            if len(parts) == 2:
                month, year = int(parts[0]), int(parts[1])
                return datetime(year, month, 1)
        except (ValueError, IndexError):
            pass
    
    # If all else fails, raise an error
    raise ValueError(f"Unable to parse date: {date_str}")

def _merge_overlapping_ranges(ranges):
    """
    Merge overlapping date ranges together.
    
    Args:
        ranges (list): List of tuples (start_date, end_date) where dates are datetime objects
    
    Returns:
        list: List of merged non-overlapping ranges
    """
    if not ranges:
        return []
    
    # Sort ranges by start date
    sorted_ranges = sorted(ranges, key=lambda x: x[0])
    
    merged = [sorted_ranges[0]]
    
    for current_start, current_end in sorted_ranges[1:]:
        last_start, last_end = merged[-1]
        
        # Check if current range overlaps with the last merged range
        # Overlaps if current_start <= last_end (touching or overlapping)
        if current_start <= last_end:
            # Merge: extend the end date if current_end is later
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            # No overlap, add as new range
            merged.append((current_start, current_end))
    
    return merged

def calculate_total_experience(experience_list):
    """
    Calculate the total professional experience from a list of experience entries.
    Handles both 'dates.start'/'dates.end' format and 'start_date'/'end_date' format.
    Dates can be in 'YYYY-MM-DD' format or 'Month YYYY' format.
    If 'end_date' or 'dates.end' is 'Present', it uses the current date.
    Overlapping date ranges are merged together to avoid double-counting.
    
    Args:
        experience_list (list): A list of dictionaries, each representing an experience entry.
    
    Returns:
        str: A formatted string representing the total experience (e.g., "5 years and 3 months").
    """
    date_ranges = []
    
    # Collect all date ranges
    for job in experience_list:
        # Try to get dates from either format
        dates_obj = job.get("dates", {})
        start_date_str = dates_obj.get("start") if dates_obj else job.get("start_date")
        end_date_str = dates_obj.get("end") if dates_obj else job.get("end_date")

        if not start_date_str:
            continue

        try:
            # Parse date - handles both "YYYY-MM-DD" and "Month YYYY" formats
            start_date = _parse_date(start_date_str)
            
            if end_date_str and end_date_str.lower() == "present":
                end_date = datetime.now()
            elif end_date_str:
                end_date = _parse_date(end_date_str)
            else:
                continue # Skip if no end date and not 'Present'

            # Store the date range
            date_ranges.append((start_date, end_date))

        except (ValueError, TypeError) as e:
            # Handle cases where date format might be incorrect
            print(f"Warning: Could not parse date for job: {job.get('company', 'Unknown')} - {e}")
            continue
    
    # Merge overlapping ranges
    merged_ranges = _merge_overlapping_ranges(date_ranges)
    
    # Calculate total months from merged ranges
    total_months = 0
    for start_date, end_date in merged_ranges:
        delta = end_date - start_date
        months_diff = delta.days / 30.44  # Average days in a month
        total_months += months_diff
            
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


def _create_vector_store(cv_data, api_key):
    """
    Create a FAISS vector store from CV data
    
    Args:
        cv_data (dict): The CV data dictionary
        api_key (str): Google API key for embeddings
    
    Returns:
        FAISS: Vector store instance
    """
    # Convert CV data into documents
    documents = []
    
    # Add total experience summary
    total_experience_str = calculate_total_experience(cv_data.get("experience", []))
    cv_data["total_experience_summary"] = total_experience_str

    # Extract current employment information
    current_jobs = []
    experience_list = cv_data.get("experience", [])
    
    for job in experience_list:
        dates_obj = job.get("dates", {})
        end_date_str = dates_obj.get("end") if dates_obj else job.get("end_date")
        
        # Check if this is a current job (ends with "Present")
        if end_date_str and end_date_str.lower() == "present":
            company = job.get("company", "")
            position = job.get("position", "")
            start_date = dates_obj.get("start") if dates_obj else job.get("start_date", "")
            
            current_jobs.append({
                "company": company,
                "position": position,
                "start_date": start_date,
                "end_date": "Present"
            })
    
    # Create a dedicated current employment document
    if current_jobs:
        current_employment_text = "CURRENT EMPLOYMENT:\n\n"
        for job in current_jobs:
            current_employment_text += f"Company: {job['company']}\n"
            current_employment_text += f"Position: {job['position']}\n"
            current_employment_text += f"Period: {job['start_date']} to Present\n\n"
        
        doc = Document(
            page_content=current_employment_text,
            metadata={"section": "current_employment", "is_current": True}
        )
        documents.append(doc)
    
    # Create documents from each section
    for section, content in cv_data.items():
        # For experience section, create separate documents for each job
        if section == "experience" and isinstance(content, list):
            for idx, job in enumerate(content):
                job_text = f"WORK EXPERIENCE - Job #{idx + 1}:\n"
                job_text += f"Company: {job.get('company', 'N/A')}\n"
                job_text += f"Position: {job.get('position', 'N/A')}\n"
                
                dates_obj = job.get("dates", {})
                start_date = dates_obj.get("start") if dates_obj else job.get("start_date", "N/A")
                end_date = dates_obj.get("end") if dates_obj else job.get("end_date", "N/A")
                
                job_text += f"Period: {start_date} to {end_date}\n"
                job_text += f"Location: {job.get('location', 'N/A')}\n\n"
                
                if job.get("achievements"):
                    job_text += "Achievements:\n"
                    for achievement in job.get("achievements", []):
                        job_text += f"- {achievement}\n"
                
                if job.get("responsibilities"):
                    job_text += "\nResponsibilities:\n"
                    for resp in job.get("responsibilities", []):
                        job_text += f"- {resp}\n"
                
                if job.get("skills"):
                    job_text += "\nSkills:\n"
                    for skill in job.get("skills", []):
                        job_text += f"- {skill}\n"
                
                is_current = (end_date and end_date.lower() == "present")
                doc = Document(
                    page_content=job_text,
                    metadata={"section": "experience", "company": job.get("company", ""), "is_current": is_current}
                )
                documents.append(doc)
        elif isinstance(content, (dict, list)):
            content_str = json.dumps(content, indent=2)
            doc = Document(
                page_content=f"Section: {section}\n{content_str}",
                metadata={"section": section}
            )
            documents.append(doc)
        else:
            content_str = str(content)
            doc = Document(
                page_content=f"Section: {section}\n{content_str}",
                metadata={"section": section}
            )
            documents.append(doc)
    
    # Use Google Generative AI embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )
    
    # Create FAISS vector store
    vector_store = FAISS.from_documents(documents, embeddings)
    
    return vector_store


def _get_or_create_vector_store(api_key):
    """
    Get or create the global vector store (singleton pattern)
    
    Args:
        api_key (str): Google API key for embeddings
    
    Returns:
        FAISS: Vector store instance
    """
    global _vector_store
    
    if _vector_store is None:
        cv_data = load_cv_data()
        if not cv_data:
            raise ValueError("Could not load CV data")
        _vector_store = _create_vector_store(cv_data, api_key)
    
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
        vector_store = _get_or_create_vector_store(api_key)
        
        # Initialize Gemini LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Create retriever - get more chunks for better context, with metadata filter if needed
        retriever = vector_store.as_retriever(search_kwargs={"k": 7})
        
        # Create prompt template (combining everything in one prompt since Gemini doesn't support system messages)
        prompt_template = """You are an AI assistant helping to answer questions about Ahlam Yusuf's professional background and CV.

**Current Date for Reference:** {current_date}

**IMPORTANT INSTRUCTIONS FOR CURRENT EMPLOYMENT QUESTIONS:**
- When asked about "where is she working now", "current employment", "where does she work", or similar questions:
  - Look for entries marked as "CURRENT EMPLOYMENT" or jobs with "Present" in the dates
  - The CV information below contains current employment details - find them and list all current positions
  - If you see "end": "Present" or "Period: X to Present", that means it's a current position
  - List ALL current companies and positions - someone can work at multiple places simultaneously

**General Instructions:**
        - Provide a concise, informative, and friendly answer based on the CV information
        - Keep your tone conversational and human-like, as if talking to a friend
        - Use a natural tone relevant to the topic and add a little gen z slang to make it more friendly and approachable
- Make it professional but with a joke here and there
        - Only answer based on the information provided in the CV
        - If the question asks for information not in the CV, respond with "I don't have that information in Ahlam's CV"
        - Focus on being helpful and accurate
        - Use specific details from the CV when possible
- Be specific about company names, positions, and dates when available

        **Example of how to handle off-topic questions (e.g., code):**
"Wooooowww there buddy, that's out of my scope. Let's focus on the main show."

**Question:** {question}

**Relevant CV Information:**
{context}

        **Begin your answer now:**
        """

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["question", "context", "current_date"]
        )
        
        # Create the chain using LCEL (LangChain Expression Language)
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        def format_prompt_input(query):
            docs = retriever.invoke(query)
            context = format_docs(docs)
            return {
                "question": query,
                "context": context,
                "current_date": current_date
            }
        
        # Create the chain - convert prompt to chat message, then pass to LLM
        def invoke_llm(inputs):
            formatted_prompt = prompt.format(**inputs)
            message = HumanMessage(content=formatted_prompt)
            response = llm.invoke([message])
            # Extract content from the response
            if hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
        
        # Create the chain
        chain = RunnablePassthrough() | format_prompt_input | invoke_llm
        
        # Generate answer
        answer = chain.invoke(question)
        
        return answer if answer else "I'm sorry, I do not know what you're talking about buddy."
        
    except Exception as e:
        return f"Oops 404 {str(e)}. Do you mind rephrasing that for me, I lost you there buddy."

