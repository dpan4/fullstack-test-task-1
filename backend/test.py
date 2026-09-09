import sys
import time
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "http://localhost:8000"
LOG_FILE = Path("test_results.log")

def log(msg: str):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def make_multipart_body(fields: dict, files: dict):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = bytearray()
    
    for key, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode('utf-8'))
        body.extend(f"{value}\r\n".encode('utf-8'))
        
    for key, (filename, content, mime_type) in files.items():
        body.extend(f"--{boundary}\r\n".encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'.encode('utf-8'))
        body.extend(f'Content-Type: {mime_type}\r\n\r\n'.encode('utf-8'))
        if isinstance(content, str):
            body.extend(content.encode('utf-8'))
        else:
            body.extend(content)
        body.extend(b"\r\n")
        
    body.extend(f"--{boundary}--\r\n".encode('utf-8'))
    return boundary, bytes(body)

def request(url: str, method: str = "GET", data: bytes = None, headers: dict = None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read()
            return response.status, res_body, response.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers
    except Exception as e:
        return 0, str(e).encode('utf-8'), {}

def run_tests():
    # Clear log
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    log("=========================================")
    log("       BASELINE API INTEGRATION TEST      ")
    log("=========================================")
    
    # Step 1: Health / Initial List
    log("\n[1/7] GET /files")
    status, body, _ = request(f"{BASE_URL}/files")
    log(f"Status: {status}")
    if status != 200:
        log(f"FAILED: Expected 200, got {status}. Body: {body.decode()}")
        return False
    log(f"Initial files count: {len(json.loads(body))}")

    # Step 2: Upload File
    log("\n[2/7] POST /files (Upload)")
    fields = {"title": "Автотест Baseline"}
    files = {"file": ("test_doc.txt", "Hello Baseline Test Content! 12345", "text/plain")}
    boundary, body_bytes = make_multipart_body(fields, files)
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    
    status, body, _ = request(f"{BASE_URL}/files", method="POST", data=body_bytes, headers=headers)
    log(f"Status: {status}")
    if status != 201:
        log(f"FAILED: Upload failed with status {status}. Body: {body.decode()}")
        return False
    
    file_data = json.loads(body)
    file_id = file_data["id"]
    log(f"Created File ID: {file_id}")
    log(f"Processing Status: {file_data.get('processing_status')}")

    # Step 3: Wait for Celery Worker
    log("\n[3/7] Waiting 3 seconds for Celery processing...")
    time.sleep(3)

    # Step 4: Verify Celery Processing
    log(f"\n[4/7] GET /files/{file_id}")
    status, body, _ = request(f"{BASE_URL}/files/{file_id}")
    log(f"Status: {status}")
    if status != 200:
        log(f"FAILED: Get file failed with status {status}")
        return False
    
    file_data = json.loads(body)
    log(f"Processing Status: {file_data.get('processing_status')}")
    log(f"Scan Status: {file_data.get('scan_status')}")
    log(f"Metadata: {json.dumps(file_data.get('metadata_json'))}")
    
    if file_data.get("processing_status") != "processed":
        log(f"WARNING: File status is '{file_data.get('processing_status')}', expected 'processed'")

    # Step 5: Check Alerts
    log("\n[5/7] GET /alerts")
    status, body, _ = request(f"{BASE_URL}/alerts")
    log(f"Status: {status}")
    if status == 200:
        alerts = json.loads(body)
        file_alerts = [a for a in alerts if a.get("file_id") == file_id]
        log(f"Alerts for file {file_id}: {json.dumps(file_alerts)}")

    # Step 6: Download File
    log(f"\n[6/7] GET /files/{file_id}/download")
    status, body, headers = request(f"{BASE_URL}/files/{file_id}/download")
    log(f"Status: {status}")
    if status == 200 and body == b"Hello Baseline Test Content! 12345":
        log("Downloaded content matches uploaded content! PASS")
    else:
        log(f"FAILED: Download mismatch or error status {status}")

    # Step 7: Delete File
    log(f"\n[7/7] DELETE /files/{file_id}")
    status, body, _ = request(f"{BASE_URL}/files/{file_id}", method="DELETE")
    log(f"Status: {status}")
    if status == 204:
        log("File deleted successfully. PASS")
    else:
        log(f"FAILED: Delete failed with status {status}")

    log("\n=========================================")
    log("      ALL BASELINE TESTS COMPLETED       ")
    log("=========================================")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
