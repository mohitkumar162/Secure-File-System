from flask import Flask, request, render_template, session, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
import bcrypt
import pyotp
import qrcode
from io import BytesIO
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import boto3

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key')
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simple AWS S3 Configuration
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

s3_enabled = False
s3_client = None

if AWS_BUCKET_NAME:
    try:
        # Initialize boto3 S3 Client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        s3_enabled = True
        print(f"AWS S3 Storage is enabled. Bucket: {AWS_BUCKET_NAME}")
    except Exception as e:
        print(f"Failed to connect to S3: {e}. Falling back to local storage.")

# Set up user credentials from environment variables (or defaults)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
TOTP_SECRET = os.environ.get('TOTP_SECRET', pyotp.random_base32())

users = {
    "admin": {
        "password": bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()),
        "role": "admin",
        "totp_secret": TOTP_SECRET
    }
}

# Configure AES encryption key from environment variable or generate random key
env_key = os.environ.get('ENCRYPTION_KEY')
if env_key:
    try:
        # If it is a base64 encoded key, decode it
        ENCRYPTION_KEY = base64.b64decode(env_key)
        if len(ENCRYPTION_KEY) != 32:
            raise ValueError("Key must be 32 bytes")
    except Exception:
        # Otherwise, pad/truncate to 32 bytes
        ENCRYPTION_KEY = env_key.encode('utf-8').ljust(32, b'\0')[:32]
else:
    ENCRYPTION_KEY = get_random_bytes(32) # 256-bit random key

def encrypt_file(file_path):
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX)
    with open(file_path, 'rb') as f:
        data = f.read()
    ciphertext, tag = cipher.encrypt_and_digest(data)
    with open(file_path + '.enc', 'wb') as f:
        f.write(cipher.nonce + tag + ciphertext)
    os.remove(file_path)
    return file_path + '.enc'

def decrypt_file(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext

@app.route('/')
def index():
    if 'username' not in session or 'totp_verified' not in session:
        return redirect(url_for('login'))
    
    # If S3 is enabled, list objects from AWS S3 bucket
    if s3_enabled:
        try:
            response = s3_client.list_objects_v2(Bucket=AWS_BUCKET_NAME)
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append(obj['Key'])
        except Exception as e:
            print(f"Error listing S3 objects: {e}")
            files = []
    else:
        # Otherwise, list files from local uploads folder
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        
    return render_template('dashboard.html', files=files)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'totp' in request.form:  # Second step: TOTP verification
            username = session.get('temp_username')
            totp_code = request.form['totp']
            if username in users:
                totp = pyotp.TOTP(users[username]['totp_secret'])
                if totp.verify(totp_code):
                    session['username'] = username
                    session['role'] = users[username]['role']
                    session['totp_verified'] = True
                    session.pop('temp_username', None)
                    return redirect(url_for('index'))
                return render_template('login.html', error="Invalid 2FA code", step="totp", qr_code=session['qr_code'])
        
        # First step: Username/password
        username = request.form['username']
        password = request.form['password'].encode()
        
        if username in users and bcrypt.checkpw(password, users[username]['password']):
            # Generate QR code for first-time setup
            totp = pyotp.TOTP(users[username]['totp_secret'])
            qr_uri = totp.provisioning_uri(name=username + "@securefiles", issuer_name="SecureFileSystem")
            qr_img = qrcode.make(qr_uri)
            buffered = BytesIO()
            qr_img.save(buffered, format="PNG")
            qr_img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            session['temp_username'] = username
            session['qr_code'] = qr_img_str
            return render_template('login.html', step="totp", qr_code=qr_img_str)
        return render_template('login.html', error="Invalid credentials", step="login")
    
    return render_template('login.html', step="login")

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    session.pop('totp_verified', None)
    session.pop('temp_username', None)
    session.pop('qr_code', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session or 'totp_verified' not in session:
        return redirect(url_for('login'))
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Encrypt the file locally
        encrypted_path = encrypt_file(file_path)
        
        # If AWS S3 is enabled, upload it and remove local copy
        if s3_enabled:
            try:
                s3_client.upload_file(encrypted_path, AWS_BUCKET_NAME, filename + '.enc')
                os.remove(encrypted_path)
            except Exception as e:
                print(f"S3 Upload failed: {e}")
                
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    if 'username' not in session or 'totp_verified' not in session:
        return redirect(url_for('login'))
    
    filename = secure_filename(filename)
    encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # If using AWS S3, download the file locally first
    if s3_enabled:
        try:
            s3_client.download_file(AWS_BUCKET_NAME, filename, encrypted_path)
        except Exception as e:
            return f"S3 Download failed: {str(e)}", 404
            
    if not os.path.exists(encrypted_path):
        return "File not found", 404
        
    try:
        plaintext = decrypt_file(encrypted_path)
        
        # If S3 is enabled, remove the temp downloaded file after decryption
        if s3_enabled and os.path.exists(encrypted_path):
            os.remove(encrypted_path)
            
        original_filename = filename.replace('.enc', '')
        return send_file(
            BytesIO(plaintext),
            as_attachment=True,
            download_name=original_filename
        )
    except Exception as e:
        return f"Decryption failed: {str(e)}", 500

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if 'username' not in session or 'totp_verified' not in session:
        return redirect(url_for('login'))

    filename = secure_filename(filename)
    
    # If S3 is enabled, delete from bucket
    if s3_enabled:
        try:
            s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=filename)
        except Exception as e:
            print(f"S3 Delete failed: {e}")
    else:
        # Otherwise, delete from local folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # Print current TOTP token at startup for ease of development/testing
    totp = pyotp.TOTP(users['admin']['totp_secret'])
    print("\n" + "="*60)
    print("SECURE FILE SYSTEM - DEVELOPMENT ASSISTANT ACTIVE")
    print(f"Username: admin")
    print(f"Password: {ADMIN_PASSWORD}")
    print(f"TOTP Secret: {users['admin']['totp_secret']}")
    print(f"Current active 2FA Token: {totp.now()}")
    print("="*60 + "\n")
    app.run(debug=True)