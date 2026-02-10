#!/usr/bin/env python3
"""
RIASEC Career Classifier
========================
AI-powered classification system that maps job skills to RIASEC codes.

Based on Holland's RIASEC model with 120 3-letter superpower stacks:
- Position 1: Core drive (WHY you act)
- Position 2: Primary expression (HOW you act)  
- Position 3: Supporting amplifier (WHAT strengthens your impact)

Usage:
    # Single job classification
    from riasec_classifier import classify_job
    result = classify_job("Python, SQL, Data Analysis", "Data Analyst")
    
    # Batch processing
    python riasec_classifier.py --csv input.csv --output output.csv
    
    # Interactive mode
    python riasec_classifier.py --interactive
"""

import json
import os
import re
import sys
from typing import Dict, List, Tuple, Optional
from collections import Counter

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')
FRAMEWORK_PATH = os.path.join(DATA_DIR, 'riasec_framework.json')

# Scoring weights
STRONG_INDICATOR_WEIGHT = 3.0
MODERATE_INDICATOR_WEIGHT = 1.5
KEYWORD_WEIGHT = 1.0
TITLE_BONUS_WEIGHT = 2.0  # Extra weight for job title matches

# ============================================================================
# LOAD FRAMEWORK
# ============================================================================

def load_framework():
    """Load the RIASEC framework from JSON."""
    if os.path.exists(FRAMEWORK_PATH):
        with open(FRAMEWORK_PATH, 'r') as f:
            return json.load(f)
    else:
        # Fallback to embedded minimal framework
        return get_embedded_framework()

def get_embedded_framework():
    """Minimal embedded framework for standalone use."""
    return {
        "riasec_types": {
            "R": {
                "name": "Realistic", "title": "The Doers",
                "skill_indicators": {
                    "strong": ["maintenance", "repair", "construction", "welding", "plumbing", "electrical", "HVAC", "carpentry", "machinery", "forklift", "CDL", "truck driving", "warehouse", "manufacturing", "assembly", "installation", "mechanical", "automotive", "diesel", "landscaping", "farming", "firefighting", "EMT", "CPR", "BLS"],
                    "moderate": ["hands-on", "technical", "field work", "troubleshooting", "inspection", "quality control", "building", "fixing"]
                }
            },
            "I": {
                "name": "Investigative", "title": "The Thinkers",
                "skill_indicators": {
                    "strong": ["research", "analysis", "data analysis", "statistics", "analytics", "programming", "software development", "Python", "Java", "JavaScript", "SQL", "machine learning", "AI", "data science", "algorithms", "debugging", "laboratory", "clinical research", "diagnosis", "engineering", "mathematics", "physics", "chemistry", "biology"],
                    "moderate": ["problem-solving", "critical thinking", "investigation", "evaluation", "assessment", "documentation", "technical writing", "analytical"]
                }
            },
            "A": {
                "name": "Artistic", "title": "The Creators",
                "skill_indicators": {
                    "strong": ["graphic design", "UI design", "UX design", "visual design", "web design", "illustration", "photography", "videography", "video editing", "animation", "creative writing", "copywriting", "content creation", "music", "acting", "dance", "fashion design", "interior design", "Adobe", "Photoshop", "Illustrator", "Figma", "art direction"],
                    "moderate": ["creative", "innovative", "artistic", "aesthetic", "visual", "media", "content", "brand", "design"]
                }
            },
            "S": {
                "name": "Social", "title": "The Helpers",
                "skill_indicators": {
                    "strong": ["teaching", "education", "training", "nursing", "patient care", "caregiving", "home health", "counseling", "therapy", "psychology", "social work", "case management", "customer service", "customer support", "coaching", "mentoring", "healthcare", "medical", "clinical", "pediatric", "geriatric", "special education"],
                    "moderate": ["communication", "interpersonal", "empathy", "listening", "teamwork", "collaboration", "support", "helping", "service"]
                }
            },
            "E": {
                "name": "Enterprising", "title": "The Persuaders",
                "skill_indicators": {
                    "strong": ["sales", "business development", "account management", "management", "leadership", "executive", "director", "supervisor", "marketing", "advertising", "public relations", "entrepreneurship", "negotiation", "persuasion", "recruiting", "real estate", "project management", "operations management"],
                    "moderate": ["strategic", "competitive", "goal-oriented", "results-driven", "influencing", "presenting", "pitching", "networking", "business"]
                }
            },
            "C": {
                "name": "Conventional", "title": "The Organizers",
                "skill_indicators": {
                    "strong": ["accounting", "bookkeeping", "auditing", "tax preparation", "payroll", "administrative", "clerical", "data entry", "filing", "records management", "scheduling", "compliance", "regulatory", "inventory management", "logistics", "supply chain", "billing", "invoicing", "Microsoft Office", "Excel", "QuickBooks", "SAP"],
                    "moderate": ["organized", "detail-oriented", "systematic", "accurate", "precise", "process", "procedure", "documentation", "reporting"]
                }
            }
        },
        "combinations": {}
    }

# Load framework at module level
FRAMEWORK = load_framework()
RIASEC_TYPES = FRAMEWORK.get('riasec_types', {})
COMBINATIONS = FRAMEWORK.get('combinations', {})

# ============================================================================
# TEXT PROCESSING
# ============================================================================

def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    if not text:
        return ""
    text = text.lower()
    # Replace common separators with spaces
    text = re.sub(r'[-_/\\.,;:|]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_title_from_url(job_link: str) -> str:
    """Extract job title from LinkedIn job URL."""
    if not job_link:
        return ""
    try:
        # Pattern: .../view/job-title-at-company-1234567890
        if '/view/' in job_link:
            path = job_link.split('/view/')[-1]
            # Remove the ID at the end
            path = re.sub(r'-\d+$', '', path)
            # Split on -at- to get just the title
            if '-at-' in path:
                path = path.split('-at-')[0]
            # Replace hyphens with spaces
            title = path.replace('-', ' ').strip()
            return title.title()
    except:
        pass
    return ""

# ============================================================================
# CLASSIFICATION LOGIC
# ============================================================================

def calculate_riasec_scores(skills_text: str, job_title: str = "") -> Tuple[Dict[str, float], Dict[str, List[str]]]:
    """
    Calculate RIASEC scores based on skills and job title.
    
    Returns:
        Tuple of (scores dict, matched_indicators dict)
    """
    # Combine and normalize text
    combined_text = normalize_text(f"{job_title} {skills_text}")
    title_text = normalize_text(job_title)
    
    scores = {letter: 0.0 for letter in "RIASEC"}
    matched = {letter: [] for letter in "RIASEC"}
    
    for letter, type_data in RIASEC_TYPES.items():
        indicators = type_data.get('skill_indicators', {})
        
        # Check strong indicators (3 points each)
        for skill in indicators.get('strong', []):
            skill_lower = skill.lower()
            if skill_lower in combined_text:
                scores[letter] += STRONG_INDICATOR_WEIGHT
                matched[letter].append(f"{skill}(+{STRONG_INDICATOR_WEIGHT})")
                
                # Bonus if in job title specifically
                if skill_lower in title_text:
                    scores[letter] += TITLE_BONUS_WEIGHT
        
        # Check moderate indicators (1.5 points each)
        for skill in indicators.get('moderate', []):
            skill_lower = skill.lower()
            if skill_lower in combined_text:
                # Only count if not already matched as strong
                if not any(skill_lower in m.lower() for m in matched[letter]):
                    scores[letter] += MODERATE_INDICATOR_WEIGHT
                    matched[letter].append(f"{skill}(+{MODERATE_INDICATOR_WEIGHT})")
        
        # Check type keywords (1 point each)
        for keyword in type_data.get('keywords', []):
            keyword_lower = keyword.lower()
            # Only count if not already matched
            strong_list = [s.lower() for s in indicators.get('strong', [])]
            moderate_list = [s.lower() for s in indicators.get('moderate', [])]
            if keyword_lower in combined_text and keyword_lower not in strong_list and keyword_lower not in moderate_list:
                scores[letter] += KEYWORD_WEIGHT
                matched[letter].append(f"{keyword}(+{KEYWORD_WEIGHT})")
    
    return scores, matched

def determine_riasec_code(scores: Dict[str, float]) -> str:
    """Determine the 3-letter RIASEC code from scores."""
    # Sort scores descending
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Get top 3 letters with positive scores
    top_3 = []
    for letter, score in sorted_scores:
        if score > 0 and len(top_3) < 3:
            top_3.append(letter)
    
    # If we don't have 3 letters with positive scores, fill with remaining
    if len(top_3) < 3:
        remaining = [letter for letter, _ in sorted_scores if letter not in top_3]
        top_3.extend(remaining[:3 - len(top_3)])
    
    return ''.join(top_3[:3])

def calculate_confidence(scores: Dict[str, float]) -> float:
    """Calculate confidence level for the classification."""
    total_score = sum(scores.values())
    if total_score == 0:
        return 0.0
    
    sorted_scores = sorted(scores.values(), reverse=True)
    top_score = sorted_scores[0]
    
    # Confidence based on:
    # 1. How dominant the top score is
    # 2. How much total evidence we found
    dominance = top_score / total_score
    evidence_factor = min(total_score / 10, 1.0)  # Caps at 10 points of evidence
    
    confidence = (dominance * 0.6 + evidence_factor * 0.4)
    return min(confidence, 1.0)

# ============================================================================
# MAIN CLASSIFICATION FUNCTION
# ============================================================================

def classify_job(skills_text: str, job_title: str = "", job_link: str = "") -> Dict:
    """
    Classify a job into a 3-letter RIASEC code.
    
    Args:
        skills_text: Comma-separated skills or job description
        job_title: Optional job title
        job_link: Optional LinkedIn job URL (title will be extracted if job_title not provided)
    
    Returns:
        Dictionary containing:
        - riasec_code: 3-letter code (e.g., "IRC")
        - primary_type: Name of primary type (e.g., "Investigative")
        - scores: Individual letter scores
        - confidence: Confidence level (0-1)
        - description: Description of the code combination
        - gift: The "superpower gift" description
        - matched_indicators: Skills that matched each letter
    """
    # Extract title from URL if not provided
    if not job_title and job_link:
        job_title = extract_title_from_url(job_link)
    
    # Calculate scores
    scores, matched = calculate_riasec_scores(skills_text, job_title)
    
    # Determine code
    riasec_code = determine_riasec_code(scores)
    
    # Calculate confidence
    confidence = calculate_confidence(scores)
    
    # Get description from framework
    combo_info = COMBINATIONS.get(riasec_code, {})
    if isinstance(combo_info, dict):
        description = combo_info.get('description', 'No description available')
        gift = combo_info.get('gift', '')
    else:
        description = combo_info if combo_info else 'No description available'
        gift = ''
    
    # Get primary type name
    primary_letter = riasec_code[0] if riasec_code else 'I'
    primary_type = RIASEC_TYPES.get(primary_letter, {}).get('name', 'Unknown')
    
    return {
        "riasec_code": riasec_code,
        "primary_type": primary_type,
        "scores": dict(scores),
        "confidence": round(confidence, 3),
        "total_score": sum(scores.values()),
        "description": description,
        "gift": gift,
        "matched_indicators": {k: v for k, v in matched.items() if v}
    }

def classify_job_simple(skills_text: str, job_title: str = "") -> str:
    """Simple version that just returns the 3-letter code."""
    return classify_job(skills_text, job_title)["riasec_code"]

# ============================================================================
# BATCH PROCESSING
# ============================================================================

def process_dataframe(df, skills_col: str = 'job_skills', title_col: str = None, 
                      link_col: str = None, show_progress: bool = True):
    """
    Process a pandas DataFrame and add RIASEC classifications.
    
    Args:
        df: pandas DataFrame
        skills_col: Column containing skills
        title_col: Column containing job title (optional)
        link_col: Column containing job link (optional)
        show_progress: Whether to show progress
    
    Returns:
        DataFrame with new columns: riasec_code, riasec_confidence, primary_riasec_type
    """
    import pandas as pd
    
    codes = []
    confidences = []
    primary_types = []
    
    total = len(df)
    for idx, row in df.iterrows():
        skills = str(row.get(skills_col, '')) if skills_col and skills_col in df.columns else ''
        title = str(row.get(title_col, '')) if title_col and title_col in df.columns else ''
        link = str(row.get(link_col, '')) if link_col and link_col in df.columns else ''
        
        result = classify_job(skills, title, link)
        codes.append(result['riasec_code'])
        confidences.append(result['confidence'])
        primary_types.append(result['primary_type'])
        
        if show_progress and (idx + 1) % 10000 == 0:
            print(f"  Processed {idx + 1:,}/{total:,} ({(idx+1)/total*100:.1f}%)")
    
    df = df.copy()
    df['riasec_code'] = codes
    df['riasec_confidence'] = confidences
    df['primary_riasec_type'] = primary_types
    
    return df

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="RIASEC Career Classifier - Map skills to Holland Codes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Classify a single job
  python riasec_classifier.py --skills "Python, SQL, Machine Learning" --title "Data Scientist"
  
  # Process a CSV file
  python riasec_classifier.py --csv jobs.csv --output jobs_classified.csv
  
  # Interactive mode
  python riasec_classifier.py --interactive
  
  # Show framework info
  python riasec_classifier.py --info
        """
    )
    
    parser.add_argument('--skills', type=str, help='Comma-separated skills')
    parser.add_argument('--title', type=str, default='', help='Job title')
    parser.add_argument('--csv', type=str, help='Input CSV file path')
    parser.add_argument('--output', type=str, help='Output CSV/Parquet file path')
    parser.add_argument('--skills-col', type=str, default='job_skills', help='Skills column name')
    parser.add_argument('--title-col', type=str, default=None, help='Title column name')
    parser.add_argument('--link-col', type=str, default='job_link', help='Job link column name')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--info', action='store_true', help='Show framework information')
    
    args = parser.parse_args()
    
    # Show framework info
    if args.info:
        print("\n" + "="*60)
        print("RIASEC CAREER FRAMEWORK")
        print("="*60)
        for letter, data in RIASEC_TYPES.items():
            name = data.get('name', 'Unknown')
            title = data.get('title', '')
            strong = len(data.get('skill_indicators', {}).get('strong', []))
            moderate = len(data.get('skill_indicators', {}).get('moderate', []))
            print(f"\n{letter} - {name} ({title})")
            print(f"   {strong} strong indicators, {moderate} moderate indicators")
        print(f"\nTotal combinations: {len(COMBINATIONS)}")
        return
    
    # Interactive mode
    if args.interactive:
        print("\n" + "="*60)
        print("RIASEC CLASSIFIER - Interactive Mode")
        print("="*60)
        print("Enter skills and job title to classify. Type 'quit' to exit.\n")
        
        while True:
            skills = input("Skills (comma-separated): ").strip()
            if skills.lower() == 'quit':
                break
            
            title = input("Job Title (optional): ").strip()
            
            result = classify_job(skills, title)
            
            print(f"\n{'─'*40}")
            print(f"RIASEC Code: {result['riasec_code']}")
            print(f"Primary Type: {result['primary_type']}")
            print(f"Confidence: {result['confidence']:.0%}")
            print(f"\nDescription: {result['description']}")
            if result['gift']:
                print(f"\nGift: {result['gift']}")
            print(f"\nScores: ", end='')
            for l in 'RIASEC':
                print(f"{l}={result['scores'][l]:.1f} ", end='')
            print(f"\n{'─'*40}\n")
        return
    
    # Process CSV
    if args.csv:
        try:
            import pandas as pd
        except ImportError:
            print("ERROR: pandas required. Install with: pip install pandas")
            sys.exit(1)
        
        print(f"\nLoading {args.csv}...")
        df = pd.read_csv(args.csv)
        print(f"Loaded {len(df):,} rows")
        
        print("\nClassifying jobs...")
        df = process_dataframe(df, args.skills_col, args.title_col, args.link_col)
        
        output = args.output or args.csv.replace('.csv', '_classified.csv')
        print(f"\nSaving to {output}...")
        
        if output.endswith('.parquet'):
            df.to_parquet(output, compression='zstd')
        else:
            df.to_csv(output, index=False)
        
        # Show distribution
        print("\n" + "="*40)
        print("RIASEC CODE DISTRIBUTION")
        print("="*40)
        for code, count in df['riasec_code'].value_counts().head(15).items():
            pct = count / len(df) * 100
            print(f"  {code}: {count:,} ({pct:.1f}%)")
        
        print(f"\nComplete! Output: {output}")
        return
    
    # Single classification
    if args.skills:
        result = classify_job(args.skills, args.title)
        
        print(f"\nRIASEC Code: {result['riasec_code']}")
        print(f"Primary Type: {result['primary_type']}")
        print(f"Confidence: {result['confidence']:.0%}")
        print(f"Description: {result['description']}")
        
        if args.verbose:
            print(f"\nScores:")
            for letter in 'RIASEC':
                name = RIASEC_TYPES.get(letter, {}).get('name', 'Unknown')
                print(f"  {letter} ({name}): {result['scores'][letter]:.1f}")
            
            if result['matched_indicators']:
                print(f"\nMatched Indicators:")
                for letter, indicators in result['matched_indicators'].items():
                    if indicators:
                        print(f"  {letter}: {', '.join(indicators[:5])}")
        return
    
    # No arguments - show help
    parser.print_help()

if __name__ == "__main__":
    main()
