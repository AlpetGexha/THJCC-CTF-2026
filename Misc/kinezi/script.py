import os
import zipfile
from datetime import datetime, timedelta

def ultimate_date_bruteforce(zip_path):
    if not os.path.exists(zip_path):
        print(f"[-] Error: {zip_path} not found in the current directory!")
        return

    print(f"[*] Generating EVERY date from 1900 to 2030...")
    
    passwords = []
    
    # Generate every single date from Jan 1, 1900 to Dec 31, 2030
    start_date = datetime(1900, 1, 1)
    end_date = datetime(2030, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        # Format as YYYYMMDD (exactly 8 characters)
        date_str = current_date.strftime("%Y%m%d")
        passwords.append(date_str.encode('utf-8'))
        current_date += timedelta(days=1)

    # Throw in a few Inmu numeric combos just in case
    extra_memes = [b'11451419', b'19190810', b'11450810', b'11450514']
    passwords.extend(extra_memes)

    print(f"[*] Generated {len(passwords)} total passwords.")
    print(f"[*] Attacking {zip_path} (ignoring false-positive CRC errors)...\n")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for i, pwd in enumerate(passwords):
                # Print progress every 10,000 attempts
                if i % 10000 == 0 and i > 0:
                    print(f"    ... tried {i} dates ...")
                
                try:
                    zf.extractall(pwd=pwd)
                    # If it extracts WITHOUT a CRC error, it's the real password!
                    print(f"\n[+++] CRACKED IT! The password is: {pwd.decode('utf-8')}")
                    
                    if os.path.exists("flag.txt"):
                        with open("flag.txt", "r", encoding="utf-8", errors="ignore") as f:
                            print("\n========================================")
                            print(f.read().strip())
                            print("========================================")
                    return
                except Exception as e:
                    err_str = str(e)
                    # Catch both bad passwords AND the false-positive CRC errors
                    if 'Bad password' in err_str or 'password required' in err_str or 'Bad CRC-32' in err_str:
                        continue
                    else:
                        # Print any other truly weird errors but keep going
                        pass
                        
            print("\n[-] Exhausted all 47,000+ dates. The password is NOT a YYYYMMDD date.")
            
    except Exception as e:
        print(f"[-] A system error occurred: {e}")

if __name__ == "__main__":
    ultimate_date_bruteforce("hidden_archive.zip")