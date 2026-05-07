import os
import io
import re
import traceback
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# DB Imports
from app.db.session import get_db
from app.db.models import AnalysisLog

# ML Imports
from app.ml.validity.predict import predict_validity
from app.ml.uml.parser import parse_requirements
from app.ml.uml.graph_builder import build_graph
from app.ml.uml.ai_refiner import refine_graph
from app.ml.ml_utils import (
    load_ambiguity_model, predict_ambiguity, detect_vague_terms,
    calculate_rqi, get_ambiguity_reason, load_classification_model,
    predict_fr_nfr_hybrid, extract_requirements
)

# File parsing
from docx import Document
import pdfplumber

router = APIRouter()

# Global model instances
amb_tokenizer, amb_model, amb_device = None, None, None
clf_tokenizer, clf_model, clf_device, clf_threshold = None, None, None, 0.30
models_loaded = False

def load_models_if_needed():
    global amb_tokenizer, amb_model, amb_device
    global clf_tokenizer, clf_model, clf_device, clf_threshold, models_loaded
    if not models_loaded:
        amb_tokenizer, amb_model, amb_device = load_ambiguity_model()
        clf_tokenizer, clf_model, clf_device, clf_threshold = load_classification_model()
        models_loaded = True

class AnalysisRequest(BaseModel):
    requirements_text: str
    modules: List[str]

class AnalysisResponse(BaseModel):
    results: List[Dict[str, Any]]
    uml_data: Optional[Dict[str, Any]] = None
    summary: Dict[str, Any]

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    try:
        if ext == "txt":
            return file_content.decode("utf-8")
        elif ext == "docx":
            doc = Document(io.BytesIO(file_content))
            return "\n".join(
                p.text.strip() for p in doc.paragraphs if p.text.strip()
            )
        elif ext == "pdf":
            pages = []
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        pages.append(t)
            return "\n".join(pages)
    except Exception as exc:
        print(f"File read error: {exc}")
    return ""

def process_requirements(requirements_list: List[str], selected_modules: List[str], db: Optional[Session] = None):
    start_time = time.time()
    status = "success"
    error_msg = None
    
    try:
        print(f"\n[BACKEND] Analysis started for {len(requirements_list)} requirements.")
        print(f"[BACKEND] Selected Modules: {selected_modules}")
        load_models_if_needed()
        results = []
        uml_data = {}

        for idx, req in enumerate(requirements_list, start=1):
            print(f"\n[PIPELINE] Processing Requirement {idx}/{len(requirements_list)}: '{req[:50]}...'")
            item = {"#": idx, "Requirement": req}

            # Validity
            print(f"  [Validity] Checking requirement structure...")
            validity = predict_validity(req)
            item.update({
                "Validity": validity["label"],
                "Val. Score": f"{validity['confidence']:.1%}",
                "Val. Reason": validity["reason"],
            })

            if validity["label"] == "Valid Requirement":
                # Ambiguity
                if "ambiguity" in selected_modules:
                    print(f"  [Ambiguity] Two-Stage Analysis: BERT -> Gemini Refinement...")
                    pred = predict_ambiguity(req, amb_tokenizer, amb_model, amb_device)
                    if pred:
                        vague, modals = detect_vague_terms(req)
                        item.update({
                            "Ambiguity": pred["label_text"],
                            "Amb. Score": f"{pred['confidence']:.1%}",
                            "RQI Score": calculate_rqi(pred["prob_ambiguous"], req),
                            "Reason": pred.get("llm_reason") or get_ambiguity_reason(req, vague, modals, pred["label_text"])
                        })
                
                # Classification
                if "classification" in selected_modules:
                    print(f"  [Classification] Two-Stage Analysis: Fine-tuned BERT -> Gemini Refinement...")
                    pred = predict_fr_nfr_hybrid(req, clf_tokenizer, clf_model, clf_device, clf_threshold)
                    if pred:
                        item.update({
                            "Type": pred["label_text"],
                            "Type Score": f"{pred['confidence']:.1%}",
                            "Method": pred.get("method_used", "hybrid")
                        })
                        if pred.get("refinement_reason"):
                            existing_reason = item.get("Reason", "")
                            if existing_reason:
                                item["Reason"] = f"{existing_reason} | Refinement: {pred['refinement_reason']}"
                            else:
                                item["Reason"] = pred["refinement_reason"]
            else:
                print(f"  [Skipped] Invalid requirement detected.")
                if "ambiguity" in selected_modules:
                    item.update({
                        "Ambiguity": "N/A", "Amb. Score": "N/A", 
                        "RQI Score": None, "Reason": "Skipped - Invalid requirement"
                    })
                if "classification" in selected_modules:
                    item.update({
                        "Type": "N/A", "Type Score": "N/A", 
                        "P(FR)": "N/A", "P(NFR)": "N/A"
                    })

            results.append(item)

        # Batch LLM Refinement
        if "ambiguity" in selected_modules or "classification" in selected_modules:
            try:
                from app.ml.ml_utils import batch_refine_requirements
                print("\n[LLM REFINEMENT] Executing synchronous batch refinement over all valid requirements...")
                batch_refine_requirements(results, selected_modules)
                print("[LLM REFINEMENT] Batch analysis completed successfully.")
            except Exception as e:
                print(f"[LLM REFINEMENT ERROR] Failed to execute batch process: {e}")

        if "uml" in selected_modules:
            try:
                print("\n[UML] Starting Design Pipeline...")
                parsed = parse_requirements(requirements_list)
                uml_data = build_graph(parsed)
                uml_data = refine_graph(requirements_list, uml_data)
                
                from app.ml.uml.diagram_renderer import draw_uml_diagram_png
                from app.ml.uml.plantuml_generator import generate_plantuml, generate_mermaid
                import base64
                
                uml_data["plantuml"] = generate_plantuml(uml_data)
                uml_data["mermaid"] = generate_mermaid(uml_data)
                
                png_bytes = draw_uml_diagram_png(uml_data)
                if png_bytes:
                    b64_img = base64.b64encode(png_bytes).decode('utf-8')
                    uml_data["png_base64"] = b64_img
                print("[UML] Design Pipeline complete.\n")
            except Exception as exc:
                print(f"[UML ERROR] Extraction failure: {exc}")
                traceback.print_exc()

        summary = {
            "Total Requirements": len(results),
            "Valid Requirements": sum(1 for r in results if r.get("Validity") == "Valid Requirement"),
            "Invalid Requirements": sum(1 for r in results if r.get("Validity") == "Invalid Requirement"),
        }
        if "ambiguity" in selected_modules:
            summary["Clear Requirements"] = sum(1 for r in results if r.get("Ambiguity") == "Clear")
            summary["Ambiguous Requirements"] = sum(1 for r in results if r.get("Ambiguity") == "Ambiguous")
            rqi_scores = [r["RQI Score"] for r in results if r.get("RQI Score") is not None]
            summary["Average RQI Score"] = round(sum(rqi_scores)/len(rqi_scores), 2) if rqi_scores else 0.0

        if "classification" in selected_modules:
            summary["Functional (FR)"] = sum(1 for r in results if r.get("Type") == "Functional (FR)")
            summary["Non-Functional (NFR)"] = sum(1 for r in results if r.get("Type") == "Non-Functional (NFR)")

        latency = (time.time() - start_time) * 1000
        if db:
            log = AnalysisLog(latency_ms=latency, status="success", module_count=len(selected_modules))
            db.add(log)
            db.commit()

        return {
            "results": results,
            "uml_data": uml_data,
            "summary": summary
        }
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        if db:
            log = AnalysisLog(latency_ms=latency, status="error", error_message=str(e), module_count=len(selected_modules))
            db.add(log)
            db.commit()
        raise e

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest, db: Session = Depends(get_db)):
    req_list = extract_requirements(request.requirements_text)
    if not req_list:
        raise HTTPException(status_code=400, detail="No valid requirements found.")
    
    return process_requirements(req_list, request.modules, db)

@router.post("/upload", response_model=AnalysisResponse)
async def analyze_file(
    file: UploadFile = File(...),
    modules: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()
        text = extract_text_from_file(content, file.filename)
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from file.")
        
        req_list = extract_requirements(text)
        if not req_list:
            raise HTTPException(status_code=400, detail="No valid requirements found.")
            
        mod_list = [m.strip() for m in modules.split(",") if m.strip()]
        return process_requirements(req_list, mod_list, db)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
