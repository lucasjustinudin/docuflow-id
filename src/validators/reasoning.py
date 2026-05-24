"""Reasoning-based validation and cross-referencing."""
import httpx
from dataclasses import dataclass
from src.extractors.vision import ExtractedDocument


class ReasoningValidator:
    def __init__(self, model: str = "mimo-v2.5-reasoning"):
        self.model = model
        import os
        self.api_key = os.environ.get("MIMO_API_KEY", "")
        self.base_url = os.environ.get("LLM_BASE_URL", "https://api.xiaomimimo.com/v1")
    
    async def validate(self, doc: ExtractedDocument) -> ExtractedDocument:
        """Validate extracted data using reasoning model."""
        
        # Rule-based validation first
        doc = self._validate_tax_calculation(doc)
        doc = self._validate_npwp_format(doc)
        
        # LLM reasoning for complex validation
        if doc.confidence < 0.9:
            doc = await self._llm_validate(doc)
        
        return doc
    
    def _validate_tax_calculation(self, doc: ExtractedDocument) -> ExtractedDocument:
        """Verify PPN calculation (11% of DPP)."""
        if doc.subtotal > 0 and doc.tax_amount > 0:
            expected_tax = doc.subtotal * 0.11
            tolerance = doc.subtotal * 0.005  # 0.5% tolerance for rounding
            
            if abs(doc.tax_amount - expected_tax) <= tolerance:
                doc.confidence = min(doc.confidence + 0.02, 1.0)
            else:
                doc.confidence -= 0.1  # Tax mismatch reduces confidence
        
        # Verify total = subtotal + tax
        if doc.subtotal > 0 and doc.total_amount > 0:
            expected_total = doc.subtotal + doc.tax_amount
            if abs(doc.total_amount - expected_total) <= 1:  # Allow 1 IDR rounding
                doc.confidence = min(doc.confidence + 0.01, 1.0)
        
        return doc
    
    def _validate_npwp_format(self, doc: ExtractedDocument) -> ExtractedDocument:
        """Validate NPWP format (XX.XXX.XXX.X-XXX.XXX)."""
        import re
        npwp_pattern = r"^\d{2}\.\d{3}\.\d{3}\.\d-\d{3}\.\d{3}$"
        
        for npwp in [doc.vendor_npwp, doc.buyer_npwp]:
            if npwp and not re.match(npwp_pattern, npwp):
                doc.confidence -= 0.05
        
        return doc
    
    async def _llm_validate(self, doc: ExtractedDocument) -> ExtractedDocument:
        """Use LLM to validate ambiguous extractions."""
        prompt = f"""Validate this extracted Indonesian document data for consistency:

Type: {doc.doc_type}
Vendor: {doc.vendor_name} (NPWP: {doc.vendor_npwp})
Buyer: {doc.buyer_name} (NPWP: {doc.buyer_npwp})
Invoice: {doc.invoice_number}
Date: {doc.date}
Subtotal (DPP): {doc.subtotal:,.0f} IDR
PPN (11%): {doc.tax_amount:,.0f} IDR
Total: {doc.total_amount:,.0f} IDR

Check:
1. Is the tax calculation correct (PPN = 11% of DPP)?
2. Does the total = DPP + PPN?
3. Is the NPWP format valid?
4. Are there any obvious inconsistencies?

Return JSON: {{"valid": bool, "issues": [str], "suggested_corrections": {{}}}}"""

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            # Apply corrections if needed
            # ... simplified
        
        return doc
