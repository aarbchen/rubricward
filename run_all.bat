@echo off
cd /d D:\RubricWard
echo [1/6] Building RubricWard Frontend & API Studio Catalog...
"D:\Daas\daas_env\Scripts\python.exe" build_rubricward_site.py
echo [2/6] Running 52-Portal DOT & Public Works Scraper...
"D:\Daas\daas_env\Scripts\python.exe" mainscraper.py
echo [3/6] Generating Tier 2 Preconstruction Dossiers & Static pSEO Pages...
"D:\Daas\daas_env\Scripts\python.exe" pseo_generator.py
echo [4/6] Running Subscriber Delivery, Planholder/MLOT Outbound Sync, 50%% Revenue Mailbox Scaler & 'SEND ZIP' Reply Responder...
"D:\Daas\daas_env\Scripts\python.exe" client_delivery.py
"D:\Daas\daas_env\Scripts\python.exe" sync_instantly_campaign.py
"D:\Daas\daas_env\Scripts\python.exe" autonomous_mailbox_scaler.py
"D:\Daas\daas_env\Scripts\python.exe" outbound_reply_responder.py
echo [5/6] Deploying Full-Stack Edge Bundle to https://rubricward.com, Seeding 12 RapidAPI Green Badges & Submitting IndexNow...
"D:\Daas\daas_env\Scripts\python.exe" build_cloudflare_edge_worker.py --deploy
"D:\Daas\daas_env\Scripts\python.exe" indexnow_submitter.py
"D:\Daas\daas_env\Scripts\python.exe" seed_rubricward_telemetry.py
echo [6/6] Running End-to-End RubricWard Integrity Verification, Error Healer & 3-Pillar Omniscient Auditor...
"D:\Daas\daas_env\Scripts\python.exe" verify_rubricward_integrity.py
"D:\Daas\daas_env\Scripts\python.exe" auto_error_healer.py --smoke --clear-resolved
"D:\Daas\daas_env\Scripts\python.exe" omniscient_auditor.py --mode full --force-now
