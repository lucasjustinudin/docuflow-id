"""Vision-based document extraction using multimodal LLMs."""
import base64
import httpx
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ExtractedDocument:
    doc_type: str = ""
    vendor_name: str = ""
    vendor_npwp: str = ""
    buyer_name: str = ""
    buyer_npwp: str = ""
    invoice_number: str = ""
    date: str = ""
    items: List[dict] = field(default_factory=list)
    subtotal: float = 0
    tax_amount: float = 0
    total_amount: float = 0
    currency: str = "IDR"
    confidence: float = 0
    raw_text: str = ""
    
    def to_dict(self):
        return self.__dict__


class VisionExtractor:
    def __init__(self, model: str = "mimo-v2.5-multimodal", base_url: str = ""):
        self.model = model
        self.base_url = base_url or "https://api.xiaomimimo.com/v1"
        import os
        self.api_key = os.environ.get("MIMO_API_KEY", "")
    
    async def extract(self, file_path: Path) -> ExtractedDocument:
        """Extract structured data from document image/PDF."""
        image_data = self._load_image(file_path)
        
        prompt = """Analyze this Indonesian business document and extract ALL information into structured format.

Document types: Faktur Pajak, Bukti Potong, Invoice/Faktur, Kwitansi, Rekening Koran, SPT

Extract:
- doc_type: document type
- vendor_name: seller/vendor name (Nama PKP / Penjual)
- vendor_npwp: seller NPWP number
- buyer_name: buyer name (Pembeli)
- buyer_npwp: buyer NPWP
- invoice_number: nomor faktur / invoice number
- date: tanggal (YYYY-MM-DD format)
- items: array of {description, quantity, unit_price, amount}
- subtotal: DPP (Dasar Pengenaan Pajak)
- tax_amount: PPN amount
- total_amount: total including tax
- currency: IDR/USD

Return as JSON. Use 0 for missing numeric fields, empty string for missing text."""

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]}
                    ],
                    "temperature": 0.1,
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return self._parse_extraction(content)
    
    def _load_image(self, file_path: Path) -> str:
        """Load and encode image to base64."""
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    
    def _parse_extraction(self, content: str) -> ExtractedDocument:
        """Parse LLM output into ExtractedDocument."""
        import json
        try:
            # Strip markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content)
            doc = ExtractedDocument(**{k: v for k, v in data.items() if hasattr(ExtractedDocument, k)})
            doc.confidence = 0.95  # Base confidence from vision model
            return doc
        except Exception as e:
            return ExtractedDocument(confidence=0.3, raw_text=content)
