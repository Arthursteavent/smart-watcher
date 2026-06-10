import json
import re
from pathlib import Path
from datetime import datetime
from file_reader import extract_text

def load_keywords():
    try:
        import sys
        if getattr(sys, 'frozen', False):
            keywords_path = Path(sys._MEIPASS) / "keywords.json"
        else:
            keywords_path = Path("keywords.json")
            
        if keywords_path.exists():
            with open(keywords_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Failed to load keywords.json: {e}")
        
    return {
        'Work': ['laporan', 'kerja', 'work', 'invoice', 'cv', 'resume', 'project'],
        'Education': ['tugas', 'kuliah', 'sekolah', 'skripsi', 'jurnal', 'makalah'],
        'Finance': ['struk', 'tagihan', 'pajak', 'tax', 'bill', 'receipt'],
        'Personal': ['pribadi', 'personal', 'keluarga', 'family', 'liburan', 'foto'],
        'Digital Assets': ['design', 'mockup', 'psd', 'movie', 'video', 'music', 'setup', 'software', 'app'],
        'Archives': ['backup', 'archive', 'arsip', 'bundle']
    }

KEYWORD_MAP = load_keywords()

def get_subcategory(ext: str) -> str:
    if ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
        return "Documents"
    if ext in ['.xlsx', '.xls', '.csv']:
        return "Spreadsheets"
    if ext in ['.pptx', '.ppt']:
        return "Presentations"
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']:
        return "Images"
    if ext in ['.mp4', '.mkv', '.avi', '.mov']:
        return "Videos"
    if ext in ['.mp3', '.wav', '.flac']:
        return "Audio"
    if ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
        return "Archives"
    if ext in ['.html', '.php', '.css', '.js', '.py', '.cpp', '.java', '.json', '.sql']:
        return "Code"
    if ext in ['.exe', '.msi', '.apk']:
        return "Software"
    return "Others"

def categorize_file(file_path: str):
    path = Path(file_path)
    file_size = path.stat().st_size if path.exists() else 0
    created_at = datetime.fromtimestamp(path.stat().st_ctime).strftime('%Y-%m-%d') if path.exists() else ""
    
    full_path_lower = path.as_posix().lower()
    ext = path.suffix.lower()
    parent_dir = path.parent.name.lower()
    
    category_scores = {cat: 0 for cat in KEYWORD_MAP.keys()}
    subcategory = get_subcategory(ext)
    
    if parent_dir in ["sekolah", "kuliah", "tugas", "kampus", "materi", "university", "school"]:
        category_scores["Education"] += 15
    elif parent_dir in ["kantor", "kerja", "pt", "cv", "perusahaan", "office", "work"]:
        category_scores["Work"] += 15
    elif parent_dir in ["finance", "keuangan", "pajak", "tagihan", "invoice"]:
        category_scores["Finance"] += 15
        
    if file_size > 1_000_000_000 and subcategory in ["Archives", "Software", "Videos", "Others"]:
        category_scores["Digital Assets"] += 10
        
    exact_phrases = {
        "Work": ["laporan keuangan", "slip gaji", "surat keputusan", "meeting notes", "dokumen perusahaan", "kontrak kerja"],
        "Finance": ["kartu kredit", "bukti transfer", "mutasi rekening", "rekening koran", "tagihan listrik"],
        "Personal": ["kartu keluarga", "boarding pass", "tiket pesawat", "buku nikah", "akta kelahiran", "paspor", "resep dokter"],
        "Education": ["tugas akhir", "skripsi final", "kartu tanda mahasiswa", "jadwal kuliah", "silabus matakuliah"],
        "Digital Assets": ["mockup ui", "source code", "logo final", "installer windows", "crack patch"]
    }
    
    for cat, keywords in KEYWORD_MAP.items():
        for keyword in keywords:
            normalized_path = full_path_lower.replace('\\', ' ').replace('/', ' ').replace('_', ' ').replace('-', ' ')
            if re.search(rf'\b{re.escape(keyword)}\b', normalized_path):
                category_scores[cat] += 3 
                
    for cat, phrases in exact_phrases.items():
        for phrase in phrases:
            if phrase in full_path_lower.replace('_', ' ').replace('-', ' '):
                category_scores[cat] += 100 
                
    content_text = ""
    if ext in ['.pdf', '.txt', '.doc', '.docx', '.csv', '.xlsx']:
        try:
            content_text = extract_text(file_path)
            if content_text:
                content_text_lower = content_text.lower()
                for cat, phrases in exact_phrases.items():
                    for phrase in phrases:
                        if phrase in content_text_lower:
                            category_scores[cat] += 100
                            
                if subcategory in ["Documents", "Spreadsheets"]:
                    currency_matches = re.findall(r'\b(rp|idr|usd|eur|saldo|kredit|debit)\b', content_text_lower)
                    if len(currency_matches) > 3:
                        category_scores["Finance"] += 20
                        
                for cat, keywords in KEYWORD_MAP.items():
                    for keyword in keywords:
                        matches = re.findall(rf'\b{re.escape(keyword)}\b', content_text_lower)
                        count = len(matches)
                        category_scores[cat] += min(count, 3)
        except Exception as e:
            print(f"Failed to read content: {e}")
            
    if "tugas" in full_path_lower or (content_text and "tugas" in content_text.lower()):
        if any(w in full_path_lower for w in ["kantor", "manajer", "divisi", "karyawan"]):
            category_scores["Work"] += 20
            category_scores["Education"] -= 20
        elif any(w in full_path_lower for w in ["sekolah", "kuliah", "dosen", "mahasiswa", "kampus"]):
            category_scores["Education"] += 20
            category_scores["Work"] -= 20
            
    if ext in ['.xlsx', '.csv'] and ("budget" in full_path_lower or "uang" in full_path_lower):
        if any(w in full_path_lower for w in ["kantor", "proyek", "laporan", "divisi"]):
            category_scores["Work"] += 30
        elif any(w in full_path_lower for w in ["pribadi", "keluarga", "bulanan"]):
            category_scores["Personal"] += 30
        else:
            category_scores["Finance"] += 20
            
    if "laporan" in full_path_lower or "report" in full_path_lower:
        category_scores["Digital Assets"] -= 20
        
    best_category = max(category_scores, key=category_scores.get)
    
    # Heuristic: Documents about Apps/Software often get misclassified as Digital Assets
    if subcategory == "Documents" and best_category == "Digital Assets":
        # If it's a document (PDF, DOCX) but scored as Digital Assets (maybe because it contains "app", "software", "ui")
        # We should strongly prefer Work, unless it's literally a design file or something.
        if category_scores["Work"] > 0 or category_scores["Education"] > 0:
            if category_scores["Work"] >= category_scores["Education"]:
                best_category = "Work"
            else:
                best_category = "Education"
        else:
            best_category = "Work" # Default to Work
            
    if category_scores[best_category] <= 0:
        if subcategory in ["Spreadsheets", "Documents", "Presentations"]:
            category = "Work"
        elif subcategory in ["Code", "Videos", "Audio", "Software"]:
            category = "Digital Assets"
        elif subcategory in ["Images"]:
            category = "Personal"
            if "screenshot" in full_path_lower or "design" in full_path_lower:
                category = "Digital Assets"
        elif subcategory == "Archives":
            category = "Archives"
        else:
            category = "Others"
    else:
        category = best_category
        
    if category == "Personal" and subcategory in ["Images", "Videos"]:
        if created_at:
            year = created_at.split("-")[0]
            subcategory = f"{subcategory}\\{year}"
            
    return category, subcategory
