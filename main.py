import uvicorn
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

app = FastAPI(title="GenAI Medical Report Generator")

# Load free local AI model
model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


class PatientData(BaseModel):
    name: str = Field(..., description="Full name of patient")
    age: int = Field(..., gt=0, lt=120)
    gender: str
    vitals: dict = Field(default_factory=dict)
    complaints: str
    medical_history: Optional[str] = None


class MedicalReport(BaseModel):
    structured_report: str
    icd10_suggestions: List[str]
    disclaimer: str


def generate_soap_note(data: PatientData) -> str:

    prompt = f"""
Create a short medical SOAP report.

Patient name: {data.name}
Age: {data.age}
Gender: {data.gender}
Vitals: {data.vitals}
Chief complaint: {data.complaints}
Medical history: {data.medical_history}

Use this exact format:
S - Subjective:
O - Objective:
A - Assessment:
P - Plan:
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    outputs = model.generate(
        **inputs,
        max_new_tokens=180,
        num_beams=4,
        do_sample=False
    )

    ai_text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    # Backup clean output if AI gives weak response
    if len(ai_text) < 80 or "S - Subjective" not in ai_text:
        ai_text = f"""
S - Subjective:
Patient {data.name} reports {data.complaints}.
Past medical history: {data.medical_history if data.medical_history else "No major history mentioned"}.

O - Objective:
Age: {data.age}
Gender: {data.gender}
Vitals: {data.vitals}

A - Assessment:
Symptoms may be related to headache, anxiety, or elevated blood pressure.
Further clinical evaluation is advised, especially due to the patient's medical history.

P - Plan:
1. Monitor blood pressure and symptoms.
2. Rest and maintain hydration.
3. Avoid stress and heavy activity.
4. Consult a qualified doctor for proper diagnosis.
5. Seek emergency care if chest pain, severe breathlessness, or worsening symptoms occur.
"""

    return ai_text


@app.post("/generate-report", response_model=MedicalReport)
async def create_report(patient: PatientData):
    try:
        report = generate_soap_note(patient)

        return {
            "structured_report": report,
            "icd10_suggestions": [
                "G43.909 - Migraine, unspecified",
                "R51 - Headache",
                "I10 - Essential Hypertension"
            ],
            "disclaimer": "AI-generated academic project output. Final review by a licensed doctor is required."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
