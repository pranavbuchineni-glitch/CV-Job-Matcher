
An automated Python script that searches for open job roles, reads a user's PDF CV, and uses Natural Language Processing (TF-IDF Cosine Similarity) to calculate a percentage match for each job.

## Features
* Rapidly queries the Adzuna API for targeted industry keywords.
* Extracts and parses text directly from a PDF resume.
* Ranks open positions based on hard-skill keyword matches (e.g., QGIS, Deep Learning, Python).
* Exports an organized `.xlsx` file with match scores and direct application links.

## How to Run
1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Get free API keys from developer.adzuna.com and add them to the script.
4. Place your PDF CV in the script folder and update the `CV_FILE` path.
5. Run `python JobNot.py`!