This project uses pretrained translation models which are not included in the GitHub repository due to size limits. To use the app, you need to manually download the models and place them in the correct directories.

📥 Step 1: Download the Models
Download the following two model folders:

Marian AR-EN Finetuned

Opus MT EN-AR

📂 Step 2: Place the Models
After downloading and extracting the model folders:
 1. Create the following directories inside your project root (same level as translator_app_gui.py):
 ├── marian-ar-en-finetuned
└── opus-mt-en-ar

2. Copy the contents of each downloaded folder into these directories respectively.
   Your final project structure should look like this:
   project-root/
├── marian-ar-en-finetuned/
│   ├── config.json
│   ├── generation_config.json
│   ├── model.safetensors
│   ├── source.spm
│   ├── target.spm
│   ├── tokenizer_config.json
│   └── vocab.json
├── opus-mt-en-ar/
│   ├── config.json
│   ├── generation_config.json
│   ├── model.safetensors
│   ├── source.spm
│   ├── target.spm
│   ├── tokenizer_config.json
│   └── vocab.json
├── translator_app.py
└── ...


Step 3: Run the App
Once the models are placed correctly, you can run the app normally:
python translator_app_gui.py

