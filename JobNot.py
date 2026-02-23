import os
import requests
import pandas as pd
from datetime import datetime
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# CONFIGURATION
# ==========================================
CV_FILE = r"YOUR CV PATH HERE"  
LOCATION = "Quebec"             

# We changed this to a Python List!
SEARCH_TERMS = ["ADD YOUR TERMS"]

# Free API keys from developer.adzuna.com
ADZUNA_APP_ID = "YOUR_APP_ID_HERE"   
ADZUNA_APP_KEY = "YOUR_APP_ID_HERE" 
# ==========================================

def get_cv_text(filepath):
    """Extracts text from the PDF CV or uses your exact profile as a fallback."""
    if not os.path.exists(filepath):
        print(f"⚠️ Could not find '{filepath}'. Using hardcoded CV profile...")
        return """Bachelor's in Environmental Studies. Minors in Sustainable Agriculture and Food Systems, and Pre-Law. 
                  Experience as Teaching Assistant for GIS and Underwater Research Intern. 
                  Skills include QGIS, ArcGIS, ArcGIS Storymaps, Auto CAD, Cloud Compare, Web ODM, ArcGIS Deep Learning and Machine Learning. 
                  Technical skills: Land Analysis, Species Identification, Drone Flight, PADI Open Water, FQAS. Bilingual. Currently learning Python, SQL, and French."""
    
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def fetch_jobs(search_terms, location):
    """Fetches real jobs from Adzuna API, looping through multiple keywords."""
    all_jobs = []
    seen_urls = set() # This acts as our duplicate catcher
    
    for term in search_terms:
        print(f"🔍 Pulling jobs for keyword: '{term}'...")
        url = "https://api.adzuna.com/v1/api/jobs/ca/search/1"
        params = {
            'app_id': ADZUNA_APP_ID,
            'app_key': ADZUNA_APP_KEY,
            'results_per_page': 50,
            'what': term,
            'where': location,
            'content-type': 'application/json'
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                results = response.json().get('results', [])
                
                # Add unique jobs to our master list
                for job in results:
                    job_url = job.get('redirect_url')
                    if job_url not in seen_urls:
                        seen_urls.add(job_url)
                        all_jobs.append(job)
            else:
                print(f"❌ API ERROR for '{term}': {response.status_code}")
        except Exception as e:
            print(f"❌ NETWORK ERROR for '{term}': {e}")
            
    return all_jobs

def calculate_match(cv_text, job_desc):
    """Calculates a 0-100% match score using NLP."""
    if not cv_text or not job_desc:
        return 0.0
        
    documents = [cv_text, job_desc]
    vectorizer = TfidfVectorizer(stop_words='english')
    sparse_matrix = vectorizer.fit_transform(documents)
    
    return cosine_similarity(sparse_matrix)[0][1] * 100

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("-" * 60)
    print(f"🚀 SCANNING JOBS IN {LOCATION.upper()}")
    print("-" * 60)
    
    my_cv_text = get_cv_text(CV_FILE)
    jobs = fetch_jobs(SEARCH_TERMS, LOCATION)
    
    if jobs:
        print(f"\n✅ Successfully pulled {len(jobs)} unique jobs! Calculating match scores...")
        ranked_jobs = []
        for job in jobs:
            score = calculate_match(my_cv_text, job.get('description', ''))
            ranked_jobs.append({
                'Match %': round(score, 1),
                'Job Title': job.get('title', 'Unknown'),
                'Company': job.get('company', {}).get('display_name', 'Unknown'),
                'City': job.get('location', {}).get('display_name', 'Unknown'),
                'Apply Link': job.get('redirect_url', '#')
            })
            
        ranked_jobs.sort(key=lambda x: x['Match %'], reverse=True)
        df = pd.DataFrame(ranked_jobs)
        
        print("\n--- TOP 5 MATCHES ---")
        print(df.head(5).to_string(index=False))
        
        timestamp = datetime.now().strftime("%Y-%m-%d")
        filename = rf"C:\Users\prana\Desktop\Quebec_Job_Matches_{timestamp}.xlsx"
        df.to_excel(filename, index=False)
        
        print("-" * 60)
        print(f"📁 Success! Saved all {len(jobs)} jobs to {filename}")
    else:
        print("⚠️ No jobs found across any keywords. The Excel file was not created.")