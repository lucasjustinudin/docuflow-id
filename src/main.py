"""DocuFlow ID - Indonesian document processing pipeline."""
import asyncio
import argparse
from pathlib import Path
from src.extractors.vision import VisionExtractor
from src.validators.reasoning import ReasoningValidator


async def main():
    parser = argparse.ArgumentParser(description="DocuFlow ID - Document Processing")
    parser.add_argument("--input", required=True, help="Input directory or file")
    parser.add_argument("--output", default="./results", help="Output directory")
    parser.add_argument("--format", choices=["json", "csv", "xlsx"], default="json")
    parser.add_argument("--sync", choices=["jurnal", "accurate", "zahir"], help="Sync to accounting")
    args = parser.parse_args()
    
    extractor = VisionExtractor()
    validator = ReasoningValidator()
    
    input_path = Path(args.input)
    documents = []
    
    if input_path.is_dir():
        documents = list(input_path.glob("*.pdf")) + list(input_path.glob("*.png")) + list(input_path.glob("*.jpg"))
    else:
        documents = [input_path]
    
    print(f"Processing {len(documents)} documents...")
    
    results = []
    for doc in documents:
        # Extract
        extracted = await extractor.extract(doc)
        # Validate
        validated = await validator.validate(extracted)
        results.append(validated)
        print(f"  {doc.name}: {validated.doc_type} | {validated.total_amount:,.0f} IDR | confidence: {validated.confidence:.2f}")
    
    # Output
    output_path = Path(args.output)
    output_path.mkdir(exist_ok=True)
    
    if args.format == "json":
        import json
        with open(output_path / "results.json", "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2, ensure_ascii=False)
    
    print(f"\nProcessed: {len(results)} documents")
    print(f"Total amount: {sum(r.total_amount for r in results):,.0f} IDR")
    print(f"Avg confidence: {sum(r.confidence for r in results)/len(results):.2f}")


if __name__ == "__main__":
    asyncio.run(main())
