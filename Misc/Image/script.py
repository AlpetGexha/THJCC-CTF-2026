import os
import zipfile

def extract_hidden_zip(image_path, output_zip="hidden_data.zip", extract_dir="extracted_files"):
    print("\n" + "="*40)
    print(f"[*] Analyzing '{image_path}' for hidden ZIP archives...")
    
    try:
        with open(image_path, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"[-] Error: Could not find '{image_path}'")
        return

    # Look for the standard ZIP Local File Header: PK\x03\x04
    zip_header = b'\x50\x4B\x03\x04'
    offset = data.find(zip_header)

    if offset == -1:
        print("[-] No ZIP header found in the file.")
        return

    print(f"[+] Found ZIP header at byte offset: {offset}")
    
    # Carve out the ZIP data from the offset to the end of the file
    zip_data = data[offset:]
    
    # Save the carved ZIP to your disk
    with open(output_zip, 'wb') as f:
        f.write(zip_data)
    print(f"[+] Saved hidden archive as: '{output_zip}'")

    # Automatically unzip the contents
    print(f"\n[*] Attempting to extract contents to the '{extract_dir}' directory...")
    try:
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(output_zip, 'r') as z:
            z.extractall(extract_dir)
            print("[+] Extraction successful! Found the following files:")
            for file_name in z.namelist():
                print(f"    -> {file_name}")
    except zipfile.BadZipFile:
        print("[-] Error: The extracted data is not a valid ZIP file. It might be corrupted.")

if __name__ == "__main__":
    # Make sure this matches your exact filename
    target_image = "THJCC_IMAGE.png" 
    extract_hidden_zip(target_image)