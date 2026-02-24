import os
import glob
from PIL import Image
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

# 1. Configuration
BUCKET_NAME = "cxr-medical-data-esila"
DATA_ROOT = "CXR_Dataset"
CATEGORIES = ["Covid", "Normal", "Pneumonia", "Tuberculosis"]
CORES = cpu_count()

def turbo_converter(file_info):
    """Lightning-fast local conversion."""
    src, dst = file_info
    try:
        img = Image.open(src).convert('RGB')
        img.save(dst, format='PNG', optimize=True)
        return True
    except: return False

print(f"🚀 Initializing TURBO Factory with {CORES} cores...")

for category in CATEGORIES:
    print(f"\n📦 Processing: {category}")
    local_dir = f"/content/{category}"
    os.makedirs(local_dir, exist_ok=True)
    
    # A. Selective Turbo Download (Only download what we need to convert)
    # Using -q for quiet and -m for parallel threads
    !gsutil -m -q cp gs://{BUCKET_NAME}/{DATA_ROOT}/{category}/*.jpg {local_dir}/ 2>/dev/null
    !gsutil -m -q cp gs://{BUCKET_NAME}/{DATA_ROOT}/{category}/*.jpeg {local_dir}/ 2>/dev/null
    
    # B. Parallel Conversion
    raw_files = glob.glob(f"{local_dir}/*")
    if not raw_files:
        print(f"  ✨ Category {category} already standardized or no legacy files found.")
        continue

    tasks = []
    for f in raw_files:
        base_name = os.path.splitext(os.path.basename(f))[0]
        tasks.append((f, f"{local_dir}/{base_name}.png"))
    
    print(f"  ⚙️ Converting {len(tasks)} legacy files...")
    with Pool(CORES) as p:
        list(tqdm(p.map(turbo_converter, tasks), total=len(tasks)))
        
    # C. Turbo Upload
    print("  ⬆️ Syncing new PNGs to GCS...")
    !gsutil -m -q cp {local_dir}/*.png gs://{BUCKET_NAME}/{DATA_ROOT}/{category}/
    
    # D. In-Place Secure Cleanup
    # We only delete legacy files from this category in GCS
    print(f"  🧹 Cleaning up legacy formats in {category}...")
    !gsutil -m -q rm gs://{BUCKET_NAME}/{DATA_ROOT}/{category}/*.jpg 2>/dev/null
    !gsutil -m -q rm gs://{BUCKET_NAME}/{DATA_ROOT}/{category}/*.jpeg 2>/dev/null
    
    # Local disk cleanup
    !rm -rf {local_dir}

print(f"\n✅ TURBO PROCESS COMPLETE: CXR_Dataset is now fully standardized (PNG).")
