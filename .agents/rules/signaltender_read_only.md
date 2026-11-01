---
trigger: always_on
---

# Strict Read-Only Lock on SignalTender Directories (`d:\Daas` & `d:\Data API Ecosystem`)

- **ZERO MODIFICATIONS ALLOWED IN SIGNALTENDER:** You **MUST NEVER** create, edit, overwrite, rename, delete, or run any mutating command on any file inside `d:\Daas` or `d:\Data API Ecosystem`.
- **Read-Only Access Only:** You may only read files from `d:\Daas` and `d:\Data API Ecosystem` for reference (or invoke `D:\Daas\daas_env\Scripts\python.exe` to execute scripts located inside `D:\RubricWard`).
- **Strict RubricWard Boundary:** Every file creation, file edit, build output, and git operation for RubricWard must take place strictly inside `D:\RubricWard`.

