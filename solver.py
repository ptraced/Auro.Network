import json
import random
import base64
import time
import uuid
import hashlib
import curl_cffi
from curl_cffi import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def fetch_encryption_key(client_guid):
    try:
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'uk',
            'dnt': '1',
            'priority': 'u=1, i',
            'referer': 'https://auro.network/iframe.html',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-storage-access': 'active',
            'x-client': client_guid
        }
        
        print(f"Fetching key with client GUID: {client_guid}")
        
        response = requests.get(
            'https://auro.network/enckey', 
            headers=headers,
            impersonate="chrome136"
        )
        response.raise_for_status()
        data = response.json()
        return data.get('key')
    except Exception as e:
        print(f"Error fetching key: {e}")
        return None

def solve_pow_challenge(prefix, difficulty):
    print(f"Solving PoW challenge: prefix='{prefix}', difficulty={difficulty}")
    target = "0" * difficulty
    nonce = 0
    start_time = time.time()
    
    while True:
        candidate = f"{prefix}{nonce}"
        hash_result = hashlib.sha256(candidate.encode()).hexdigest()
        
        if hash_result.startswith(target):
            elapsed = time.time() - start_time
            print(f"PoW solved! nonce={nonce}, hash={hash_result}")
            print(f"Time taken: {elapsed:.2f} seconds, attempts: {nonce + 1}")
            return nonce, hash_result
        
        nonce += 1
        
        if nonce % 100000 == 0:
            elapsed = time.time() - start_time
            rate = nonce / elapsed if elapsed > 0 else 0
            print(f"Attempt {nonce:,} - Rate: {rate:,.0f} hashes/sec")

def submit_pow_validation(prefix, nonce, client_guid):
    try:
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://auro.network',
            'priority': 'u=1, i',
            'referer': 'https://auro.network/iframe.html',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-storage-access': 'active',
            'x-client': client_guid
        }
        
        payload = {
            'prefix': prefix,
            'nonce': str(nonce)
        }
        
        print(f"Submitting PoW validation with client GUID: {client_guid}")
        print(f"Payload: {payload}")
        
        response = requests.post(
            'https://auro.network/api/pow/validate',
            headers=headers,
            json=payload,
            impersonate="chrome136"
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.text:
            print(f"Response body: {response.text}")
        
        response.raise_for_status()
        return response.json() if response.text else {"status": "success"}
        
    except Exception as e:
        print(f"Error submitting PoW validation: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Error response: {e.response.text}")
        return None

def submit_pow_solution(nonce, hash_result, client_guid):
    try:
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://auro.network',
            'priority': 'u=1, i',
            'referer': 'https://auro.network/iframe.html',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-storage-access': 'active',
            'x-client': client_guid
        }
        
        payload = {
            'nonce': nonce,
            'hash': hash_result
        }
        
        print(f"Submitting PoW solution with client GUID: {client_guid}")
        print(f"Payload: {payload}")
        
        response = requests.post(
            'https://auro.network/api/pow/solve',
            headers=headers,
            json=payload,
            impersonate="chrome136"
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.text:
            print(f"Response body: {response.text}")
        
        response.raise_for_status()
        return response.json() if response.text else {"status": "success"}
        
    except Exception as e:
        print(f"Error submitting PoW solution: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Error response: {e.response.text}")
        return None

def submit_pow_setup(encrypted_data, nonce, client_guid):
    try:
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://auro.network',
            'priority': 'u=1, i',
            'referer': 'https://auro.network/iframe.html',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-storage-access': 'active',
            'x-client': client_guid
        }
        
        mp = curl_cffi.CurlMime()
        mp.addpart(
            name="mouse",
            data=encrypted_data
        )
        mp.addpart(
            name="iv", 
            data=nonce
        )
        
        print(f"Submitting to PoW setup with client GUID: {client_guid}")
        print(f"Mouse data length: {len(encrypted_data)} characters")
        print(f"IV/Nonce: {nonce}")
        
        response = requests.post(
            'https://auro.network/api/pow/setup',
            headers=headers,
            multipart=mp,
            impersonate="chrome136"
        )
        
        mp.close()
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.text:
            print(f"Response body: {response.text}")
        
        response.raise_for_status()
        return response.json() if response.text else {"status": "success"}
        
    except Exception as e:
        print(f"Error submitting PoW setup: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Error response: {e.response.text}")
        return None

def generate_mouse_data(num_points=50):
    data = []
    current_time = int(time.time() * 1000)
    x, y = 200, 50
    
    for i in range(num_points):
        x += random.randint(-3, 3)
        y += random.randint(-1, 2)
        
        x = max(50, min(400, x))
        y = max(10, min(300, y))
        
        data.append({
            "x": x,
            "y": y,
            "t": current_time + (i * random.randint(1, 5))
        })
    
    return data

def add_mouse_jitter(mouse_data, jitter_range=3, time_jitter_ms=5):
    jittered_data = []
    
    for point in mouse_data:
        x_jitter = random.randint(-jitter_range, jitter_range)
        y_jitter = random.randint(-jitter_range, jitter_range)
        
        time_jitter = random.randint(-time_jitter_ms, time_jitter_ms)
        
        jittered_point = {
            "x": max(0, point["x"] + x_jitter),
            "y": max(0, point["y"] + y_jitter),
            "t": point["t"] + time_jitter
        }
        
        jittered_data.append(jittered_point)
    
    jittered_data.sort(key=lambda p: p["t"])
    
    return jittered_data

def update_timestamps(mouse_data, current_time_ms=None):
    if current_time_ms is None:
        current_time_ms = int(time.time() * 1000)
    
    if not mouse_data:
        return mouse_data
    
    original_start = mouse_data[0]["t"]
    updated_data = []
    
    for point in mouse_data:
        time_offset = point["t"] - original_start
        new_timestamp = current_time_ms + time_offset
        
        updated_point = {
            "x": point["x"],
            "y": point["y"],
            "t": new_timestamp
        }
        updated_data.append(updated_point)
    
    return updated_data

def encrypt_mouse_data(data, key_b64, nonce_b64=None):
    json_data = json.dumps(data, separators=(',', ':'))
    data_bytes = json_data.encode('utf-8')
    
    key = base64.b64decode(key_b64)
    
    if nonce_b64:
        nonce = base64.b64decode(nonce_b64)
    else:
        nonce = os.urandom(12)
    
    aesgcm = AESGCM(key)
    encrypted_data = aesgcm.encrypt(nonce, data_bytes, None)
    
    return {
        'key': key_b64,
        'nonce': base64.b64encode(nonce).decode('utf-8'),
        'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8')
    }

def main():
    client_guid = str(uuid.uuid4())
    print(f"Using client GUID for all requests: {client_guid}")
    
    print("\nFetching encryption key from auro.network...")
    key_b64 = fetch_encryption_key(client_guid)
    
    if not key_b64:
        print("Failed to fetch encryption key. Exiting.")
        return
    
    print(f"Retrieved key: {key_b64}")
    
    print("\nGenerating mouse movement data...")
    original_data = generate_mouse_data(50)
    print(f"Generated {len(original_data)} data points")
    
    print("Adding jitter...")
    mouse_data = add_mouse_jitter(original_data, jitter_range=2, time_jitter_ms=3)
    
    print(f"Sample data point: x={mouse_data[0]['x']}, y={mouse_data[0]['y']}, t={mouse_data[0]['t']}")
    
    print("\nEncrypting mouse data...")
    encrypted_result = encrypt_mouse_data(mouse_data, key_b64)
    
    print("\nEncryption Results:")
    print(f"Key: {encrypted_result['key']}")
    print(f"Nonce: {encrypted_result['nonce']}")
    print(f"Encrypted Data: {encrypted_result['encrypted_data']}")
    
    print(f"\nEncrypted data length: {len(encrypted_result['encrypted_data'])} characters")
    
    print("\nSubmitting to PoW setup endpoint...")
    pow_response = submit_pow_setup(encrypted_result['encrypted_data'], encrypted_result['nonce'], client_guid)
    
    if pow_response:
        print(f"PoW setup response: {pow_response}")
        
        if 'prefix' in pow_response and 'difficulty' in pow_response:
            prefix = pow_response['prefix']
            difficulty = pow_response['difficulty']
            
            print(f"\nReceived PoW challenge: prefix='{prefix}', difficulty={difficulty}")
            nonce, hash_result = solve_pow_challenge(prefix, difficulty)
            
            print("\nSubmitting PoW validation...")
            validation_response = submit_pow_validation(prefix, nonce, client_guid)
            
            if validation_response:
                print(f"PoW validation response: {validation_response}")
            else:
                print("Failed to submit PoW validation")
        else:
            print("No PoW challenge received")
    else:
        print("Failed to submit to PoW setup endpoint")

if __name__ == "__main__":
    main()