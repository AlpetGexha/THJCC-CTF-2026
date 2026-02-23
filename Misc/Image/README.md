# IMAGE?

**Point: 100**

Check the hex of this image

### Solution

1. **Analyze the Image**: Initial inspection of `THJCC_IMAGE.png` reveals it contains more data than a standard image.
2. **Identification**: Using a binary analysis (or a simple hex search), we find the ZIP header `PK\x03\x04` embedded within the PNG's data.
3. **Extraction (Carving)**:
   - A Python script (`script.py`) was used to scan for the `\x50\x4B\x03\x04` signature.
   - All data from that offset to the end of the file was saved as `hidden_data.zip`.
4. **Result**: Extracting the ZIP archive reveals the directory `cute/` containing additional image files.

Flag `THJCC{fRierEN-SO_cUTe:)}`
