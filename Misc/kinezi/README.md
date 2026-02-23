# CTF Write-up: Kinezi (Hidden Password)

## Challenge Description

The goal was to find the password to a protected ZIP archive (`hidden_archive.zip`) using clues provided in a hint and a companion file (`challenge.HEIC`).

### Provided Hints

- **Text Hint**: "這是一個一個一個重要提示" (This is a very, very, very important hint).
- **Song Hint**: "在這特別的日子裡，送給你們一首非常特別的歌曲，特別的八字給特別的你" (On this special day, giving you a very special song... a special 8-digits for a special you).
- **Implicit Context**: The phrasing used is a well-known reference to the Japanese internet meme "Yajuu Senpai" (野獸先輩), which is often associated with the numbers `114514` and the date `August 10th` (8/10).

---

## Step-by-Step Solution

### 1. Initial Analysis

The directory contained:

- `hidden_archive.zip`: The target file.
- `challenge.HEIC`: An iPhone image file.
- `script.py`: A failed brute-force script that tried all dates from 1900 to 2030.

### 2. Identifying the Meme

The phrase "這是一個一個一個..." and the "special day" strongly pointed towards the **8/10 (August 10th)** meme culture. Since the provided `script.py` already exhausted all standard dates up to the year 2030, the "special year" had to be something outside that range.

### 3. Metadata Investigation

I used a Python script with the `pi-heif` and `exifread` libraries to inspect the metadata (EXIF) of the `challenge.HEIC` file.

```python
from pi_heif import register_heif_opener
import exifread

register_heif_opener()
with open('challenge.HEIC', 'rb') as f:
    tags = exifread.process_file(f)
    print(tags['EXIF DateTimeOriginal'])
```

**Result:**
The EXIF data revealed a modified timestamp:
`EXIF DateTimeOriginal: 3000:08:10 00:00:00`

### 4. Cracking the ZIP

The date `3000:08:10` translates to the 8-digit string **`30000810`**.

I ran a script to test this password against the archive:

```python
import zipfile
with zipfile.ZipFile('hidden_archive.zip', 'r') as zf:
    zf.extractall(pwd=b'30000810')
```

The extraction was successful, yielding `flag.txt`.

### 5. Obtaining the Flag

Reading the extracted file:

```powershell
type flag.txt
```

**Flag:** `THJCC{Y@JUNlKU}`

---

## Conclusion

The challenge combined Steganography (metadata manipulation) with OSINT/Meme culture. The key was recognizing the specific "Yajuu Senpai" linguistic patterns and checking the image's EXIF data for a non-standard year.

**Password:** `30000810`
**Flag:** `THJCC{Y@JUNlKU}`
