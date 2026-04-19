import uvicorn
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ---------------------------------------------------
# FastAPI App
# ---------------------------------------------------
app = FastAPI(title="GenAI Medical Report Generator")


# ---------------------------------------------------
# Data Models
# ---------------------------------------------------
class PatientData(BaseModel):
    name: str = Field(..., description="Full name of patient")
    age: int = Field(..., gt=0, lt=120)
    gender: str
    vitals: dict = Field(default_factory=dict)
    complaints: str
    medical_history: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Jane Doe",
                "age": 34,
                "gender": "Female",
                "vitals": {
                    "BP": "120/80",
                    "Temp": "98.6F",
                    "HR": "72"
                },
                "complaints": "Severe headache for 2 days",
                "medical_history": "Migraine"
            }
        }
    }


class MedicalReport(BaseModel):
    structured_report: str
    icd10_suggestions: List[str]
    disclaimer: str


# ---------------------------------------------------
# AI-Free Report Generator
# ---------------------------------------------------
def generate_soap_note(data: PatientData) -> str:

    report = f"""
=========================
MEDICAL SOAP REPORT
=========================

S - SUBJECTIVE:
Patient Name: {data.name}
Patient reports: {data.complaints}

Past Medical History:
{data.medical_history if data.medical_history else "Noted"}

-----------------------------------

O - OBJECTIVE:
Age: {data.age}
Gender: {data.gender}

Vitals:
{data.vitals}

-----------------------------------

A - ASSESSMENT:
Possible headache / migraine related episode.
Further clinical evaluation advised.

-----------------------------------

P - PLAN:
1. Adequate hydration
2. Rest in low-light environment
3. Monitor blood pressure
4. Use physician-prescribed medication
5. Follow-up consultation if symptoms persist

=========================
END OF REPORT
=========================
"""

    return report


# ---------------------------------------------------
# API Route
# ---------------------------------------------------
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
            "disclaimer": "AI-simulated academic project output. Final review by licensed clinician required."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------
# Run App
# ---------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )