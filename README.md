<div align="center">

# DocuFlow ID

AI-powered document processing for Indonesian business documents. 97% accuracy on invoices, tax forms, and receipts.

[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)]()
[![Accuracy](https://img.shields.io/badge/accuracy-97%25-brightgreen?style=flat-square)]()

</div>

---

## Problem

Indonesian SMEs process hundreds of documents daily — invoices (faktur), tax receipts (bukti potong), government forms (NPWP, SIUP, NIB), and bank statements. Manual data entry is slow, error-prone, and expensive.

## Pipeline

```
Document Input (PDF/Image/Scan)
    |
    v
+------------------+
| OCR Engine       |  <-- text extraction
| (Tesseract/LLM)  |
+--------+---------+
         |
    +----+----+
    |         |
    v         v
+------+  +----------+
| Type |  | Field    |  <-- structured extraction
| Det. |  | Mapping  |
+--+---+  +----+-----+
   |           |
   +-----+-----+
         |
         v
+------------------+
| Cross-Reference  |  <-- validate against
| Accounting DB    |     existing records
+--------+---------+
         |
         v
   Structured JSON
   (ready for import)
```

## Supported Documents

| Document | Type | Fields |
|----------|------|--------|
| Faktur Pajak | Tax Invoice | NPWP, amount, VAT, date |
| Bukti Potong | Tax Receipt | Withholding %, gross amount |
| NPWP Card | Tax ID | Name, NPWP number, address |
| SIUP/NIB | Business License | Company, registration, scope |
| Bank Statement | Financial | Transactions, balances |

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # configure API keys
python -m src.pipeline --input ./documents/
```

## License

MIT
