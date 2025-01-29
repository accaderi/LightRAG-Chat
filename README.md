<h1 align="center"><strong>LightRAG Chat - Setup Guide</strong></h1>

<p align="center">
  <a href="https://youtu.be/cAO-oDGmIqs">
    <img src="https://img.youtube.com/vi/cAO-oDGmIqs/0.jpg" alt="Youtube Video">
  </a>
</p>

<p align="center">
  <a href="https://youtu.be/cAO-oDGmIqs">Chatbot using Telegram or WhatsApp and local ollama models with LightRAG</a>
</p>

## Summary
LightRAG Chat is a locally hosted AI chatbot that leverages both conventional Retrieval-Augmented Generation (RAG) and the LightRAG framework. It integrates with Django API, runs Ollama models on a separate GPU-powered computer, and is automated using n8n. The chatbot interacts via Telegram or WhatsApp, ensuring private, efficient, and customizable AI responses. This guide provides a step-by-step process for setting up the server, configuring messaging services, and optimizing model performance.  

The guide assumes familiarity with setting up home servers, `n8n`, and authentication processes. For detailed steps on those topics, refer to this [YouTube playlist](https://youtube.com/playlist?list=PL0dJpoLxZYoFGMFqQVCsgiCVujoNh1VxP&si=icLRk2F_F3QZImhD).  

Visit the [LightRAG GitHub](https://github.com/HKUDS/LightRAG) repository to gain a deeper understanding of this unique RAG method and access the latest release.

## 1st Step: Set Up the Server API

### 1. Set up the Django API

Clone the repository:
```bash
git clone https://github.com/accaderi/LightRAG-Chat.git
cd LightRAG-Chat
python -m venv env
source env/bin/activate
```

### Update `utils.py` (if using the latest LightRAG version—only the `lightrag` folder is required from the LightRAG repository)
Ensure the import statement in `utils.py` is:
```python
from .prompt import PROMPTS
```

### Install Dependencies
```bash
pip install -r lightrag/requirements.txt
pip install -r requirements.txt
```

#### Optional: Fix C++ Compiler Error (Linux)
```bash
sudo apt-get update
sudo apt-get install build-essential python3-dev python3.11-dev
```

### Run Migrations and Create Superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Generate Access Token
Replace `'admin'` in `generate_token.py` with your superuser username, then run:
```bash
python manage.py shell < generate_token.py
```
Save the displayed token.

### Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## 2. Set Up Google Cloud Project
- Create a project in Google Cloud Console.
- Generate an OAuth Client ID and download `credentials.json` (choose "Web application" from the dropdown).
- Place `credentials.json` in the app’s main folder.

### Test API with cURL
```bash
curl -X POST \
  http://your-server/api/process/ \
  -H 'Authorization: Token YOUR_TOKEN_HERE' \
  -H 'Content-Type: application/json' \
  -d '{"question":"Your question", "mode":"hybrid"}'
```

## 3. Configure Nginx

### Nginx Configuration for Django
```nginx
server {
    server_name subdomain.your.domain.com;

    location /static/ {
        alias /path/to/static/;
        expires 1y;
        add_header Cache-Control "public, no-transform";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Authorization $http_authorization;
        proxy_pass_header Authorization;
        proxy_connect_timeout 75s;
        proxy_read_timeout 300s;
    }
}

server {
    listen 80;
    server_name subdomain.your.domain.com;
    return 301 https://$host$request_uri;
}
```

### Test and Restart Nginx
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Obtain SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

## 2nd Step: Set Up the Computer to Serve the Ollama Models

### Set Up Wake on LAN
#### BIOS/UEFI Configuration
- Enter BIOS/UEFI settings during system startup.
- Locate the WOL option (may be called "Wake on PCI/PCI-E," "Power on PCI/PCI-E," or "S5 Wake on LAN").
- Enable the WOL option.
- Save settings and restart.

#### Windows Configuration
**Device Manager Setup:**
1. Open Device Manager (Windows Key + X).
2. Expand **Network Adapters**.
3. Right-click your network adapter and select **Properties**.
4. In the **Advanced** tab: Enable **Wake on Magic Packet**.
5. In the **Power Management** tab:
   - Enable **Allow this device to wake the computer**.
   - Enable **Only allow a magic packet to wake the computer**.

#### Debian Linux Configuration
Using `ethtool`:
1. Install `ethtool`:
   ```bash
   sudo apt install ethtool
   ```
2. Check WOL support:
   ```bash
   sudo ethtool <interface-name> | grep "Wake-on"
   ```
3. Enable WOL:
   ```bash
   sudo ethtool --change <interface-name> wol g
   ```

**Make WOL Persistent:**
Choose one of these methods:
- **Using NetworkManager:**
  ```bash
  sudo nmcli c modify "connection-name" 802-3-ethernet.wake-on-lan magic
  ```
- **Using systemd:**
  ```bash
  sudo systemctl edit wol.service --full --force
  ```
  Add the following configuration:
  ```text
  [Unit]
  Description=Enable Wake-on-LAN
  After=network-online.target

  [Service]
  Type=oneshot
  ExecStart=/sbin/ethtool --change <interface-name> wol g

  [Install]
  WantedBy=network-online.target
  ```

**Testing WOL**
To test WOL functionality, you'll need:
- The target computer's MAC address.
- A tool to send the magic packet (e.g., **Wake On LAN** app on Android/iPhone).
- The computer should wake up when receiving the magic packet while in sleep mode.

## 5. Set Up Ollama for Model Serving
### Windows Installation
1. Download and install **Ollama**.
2. Set system environment variables:
   ```plaintext
   OLLAMA_HOST=0.0.0.0
   OLLAMA_ORIGINS=*
   OLLAMA_MODELS=C:\ProgramData\Ollama\models
   ```
3. Create a batch file to start Ollama automatically or skip this step if Ollama is installed that way or you want to start it manually:
   ```batch
   @echo off
   cd /d "C:\Program Files\Ollama"
   start ollama.exe
   ```
4. Place the batch file in the Windows Startup folder.
Alternative Startup Folder Locations
For current user only:
`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
For all users:
`%ALLUSERSPROFILE%\Microsoft\Windows\Start Menu\Programs\Startup`

### Linux Installation
```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable ollama
sudo systemctl start ollama
```
This will:
Download and install the Ollama binary
Create an Ollama user
Set up the systemd service
Start Ollama automatically (for manual start see the ‘Manual start but keep running after wake up’ section)

### Configure Remote Access
Create or edit the systemd service file:
```bash
sudo nano /etc/systemd/system/ollama.service
```

Add these environment variables to the [Service] section:
```text
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_ORIGINS=*"
```
Enable Services  
Reload systemd and enable Ollama:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
```

To ensure Ollama runs automatically after the system wakes from suspend, create a systemd service:
Create a new systemd service file:
```bash
sudo nano /etc/systemd/system/ollama-resume.service
```
Add the following content:
```text
[Unit]
Description=Restart Ollama after suspend
After=suspend.target hibernate.target hybrid-sleep.target suspend-then-hibernate.target

[Service]
Type=oneshot
ExecStart=/usr/bin/systemctl restart ollama.service

[Install]
WantedBy=suspend.target hibernate.target hybrid-sleep.target suspend-then-hibernate.target
```

Enable and start the service:
```bash
sudo systemctl enable ollama-resume.service
sudo systemctl start ollama-resume.service
```

#### Verify Installation
```bash
systemctl status ollama
curl localhost:11434
```

### Manual start but keep running after wake up
Initial Service Configuration
First, disable Ollama from starting at boot:
```bash
sudo systemctl disable ollama
```

Create a service file for handling resume after suspend:
```bash
sudo nano /etc/systemd/system/ollama-resume.service
```
Add this content to the file:
```text
[Unit]
Description=Restart Ollama after resume
After=suspend.target hibernate.target hybrid-sleep.target suspend-then-hibernate.target

[Service]
Type=oneshot
ExecStart=/usr/bin/systemctl try-restart ollama.service

[Install]
WantedBy=suspend.target hibernate.target hybrid-sleep.target suspend-then-hibernate.target
```

Enable Resume Service
Enable the resume service while keeping Ollama disabled at boot:
```bash
sudo systemctl enable ollama-resume.service
```
Usage
When you want to use Ollama, start it manually:
```bash
sudo systemctl start ollama
```
The system will now automatically maintain Ollama's state across suspend/resume cycles as long as it was running before suspend


### Download Required Models
```bash
ollama pull qwen2
ollama pull nomic-embed-text
```

## 6. Configure Messaging and Database Services
### WhatsApp API Setup
Get required authentications:
1. Visit the facebook developer page: https://developers.facebook.com/
2. Create new app
- Follow the instructions select other from the Add use case menu
- Then select business (verified business portfolio is required)
3. Add whatsapp
4. Select quickstart from whatsapp menu on the left side
- Select a business portfolio
- Continue
5. App settings > Basic
- Copy App ID to the Whatsapp trigger node or just create credentials for whatsapp in credentials in n8n > credentials Client ID text input.
- App secret goes to Client Secret. Here to see the secret in meta need to provide your fb webpage password

Whatsapp send message node credentials:  
1. On the developer page of meta go to whatsapp > API Setup
2. From Test number given we are giving our number in production
3. Copy Whatsapp Business Account ID and paste it to Business Account ID in the whatsapp send message node create credential text input
4. In the To input phone numbers needs to be provided where the response will be sent, for test max 5 numbers are possible to be provided, for test provide your own whatsapp phone number
- For the first time the number receives a code from whatsapp this need to be provided back to accept the number
5. Click on Generate Access Token
- this will ask permission from our fb account to have access to it
- Choose the same number what u inserted into the whatsapp trigger node credential or all but it might not the safest
6. Copy the generated Access Token and past it to Access Token n the whatsapp send message node create credential text input


### Telegram Bot Setup
1. Open [BotFather](https://telegram.me/BotFather)
2. Create a new bot: `/newbot`
3. Add a name for the bot
4. Create the Username for the bot
5. Obtain the bot token provided by BotFather.
6. Use the token in the Telegram trigger and message nodes.

### Supabase VectorDB Setup
#### Create a New Project and Add SQL Schema
In the SQL Editor insert:
```sql
-- Drop the function first (since it depends on the table)
drop function if exists match_documents;


-- Drop the table
drop table if exists documents;


-- Drop the extension (optional, only if you need to change it)
drop extension if exists vector;




-- Enable the pgvector extension to work with embedding vectors
create extension vector;


-- Create a table to store your documents
create table documents (
 id bigserial primary key,
 content text, -- corresponds to Document.pageContent
 metadata jsonb, -- corresponds to Document.metadata
 embedding vector(768) -- 768 works for Huggingface distilbert embeddings, change if needed
);


-- Create a function to search for documents
create function match_documents (
 query_embedding vector(768),
 match_count int default null,
 filter jsonb DEFAULT '{}'
) returns table (
 id bigint,
 content text,
 metadata jsonb,
 similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
 return query
 select
   id,
   content,
   metadata,
   1 - (documents.embedding <=> query_embedding) as similarity
 from documents
 where metadata @> filter
 order by documents.embedding <=> query_embedding
 limit match_count;
end;
$$;
```
#### Add Credentials to `n8n`
Find credentials under Project Setting in API submenu.
- **Host**: Supabase Project URL
- **Service Role Secret**: Supabase service_role

## 7. Start the Django RAG App
```bash
uvicorn web_support_n8n.asgi:application --workers 3 --host 127.0.0.1 --port 8000 --loop asyncio
```

## 8. Set Up the `n8n` Workflow
- Add credentials for:
  - Google Drive
  - Supabase
  - Groq
  - Hugging Face
  - Telegram or WhatsApp
  - Http Request - Django API node (URL and Token)

## 9. Usage
1. Enable "When clicking 'Test workflow'".
2. Upload a document to Google Drive.
3. Select the document in the Google Drive node from the list.
4. Click **Test workflow**.
5. Deactivate "When clicking 'Test workflow'".
6. Activate Telegram/WhatsApp trigger node.
7. Enable the workflow.
8. Interact with the chatbot via Telegram or WhatsApp.
  - Querying the traditional vector RAG system: `sup What is your question?`
  - Querying the LightRAG system: `mix/naive/local/global/hybrid What is your question?`
  - If no mode is specified, `What is your question` defaults to mix mode.
