import os
import pandas as pd

# 1. The host path where the dataset is located
base_path = r'C:\X-RAYS\CXR_Dataset'

data = []

# 2. Browse through the folders (Covid, Pneumonia, Tuberculosis, Normal)
for label in os.listdir(base_path):
    class_path = os.path.join(base_path, label)
    
    if os.path.isdir(class_path):
        for image_name in os.listdir(class_path):
            # I created the file path.
            image_path = os.path.join(class_path, image_name)
            
            # Add data to list. (File path and Label)
            data.append({
                'image_path': image_path,
                'label': label
            })

# 3. I converted the list to a Pandas DataFrame.
df = pd.DataFrame(data)

# 4. I shuffled the data. (Shuffle) - Important for the model to learn better.
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# 5. I saved it as a CSV file.
df.to_csv('cxr_metadata.csv', index=False)
print(f"A total of {len(df)} images were successfully tagged and 'cxr_metadata.csv' was created.")
print(df['label'].value_counts())
