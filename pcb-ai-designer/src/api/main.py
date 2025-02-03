from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
from datetime import datetime
import os

from ..core.pcb_generator import PCBGenerator

app = FastAPI(title="PCB AI Designer API")

# إضافة دعم CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PCBRequest(BaseModel):
    description: str
    constraints: Optional[Dict] = {}
    preferences: Optional[Dict] = {}

class PCBResponse(BaseModel):
    design_id: str
    board_outline: Dict
    components: List[Dict]
    routes: List[Dict]
    manufacturing_notes: List[str]
    estimated_cost: float
    design_time: float

# إنشاء مثيل من مولد PCB
pcb_generator = PCBGenerator()

@app.post("/generate-design", response_model=PCBResponse)
async def generate_design(request: PCBRequest):
    try:
        # تحليل المتطلبات
        start_time = datetime.now()
        requirements = pcb_generator.analyze_requirements(request.description)
        
        # توليد حدود اللوحة
        board_outline = pcb_generator.generate_board_outline(
            requirements['components'],
            {**requirements['constraints'], **request.constraints}
        )
        
        # تحسين توزيع المكونات
        placed_components = pcb_generator.optimize_component_placement(
            board_outline,
            requirements['components']
        )
        
        # توليد مسارات التوصيل
        routes = pcb_generator.generate_routing(placed_components, board_outline)
        
        # حساب الوقت المستغرق
        design_time = (datetime.now() - start_time).total_seconds()
        
        # تحضير الاستجابة
        return {
            'design_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'board_outline': board_outline.__geo_interface__,
            'components': placed_components,
            'routes': [route.__geo_interface__ for route in routes],
            'manufacturing_notes': [
                f"تم تحسين تصميم اللوحة باستخدام الذكاء الاصطناعي",
                f"تم توزيع {len(placed_components)} مكون بشكل أمثل",
                f"مساحة اللوحة: {board_outline.area:.2f} مم²"
            ],
            'estimated_cost': self._estimate_cost(board_outline, placed_components),
            'design_time': design_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _estimate_cost(self, outline, components: List[Dict]) -> float:
    """تقدير تكلفة تصنيع اللوحة"""
    # تكلفة أساسية لكل سم مربع من اللوحة
    base_cost_per_cm2 = 0.5
    board_cost = outline.area * base_cost_per_cm2 / 100  # تحويل من مم² إلى سم²
    
    # تكلفة المكونات
    component_cost = sum(comp.get('price', 0) for comp in components)
    
    # تكلفة التصنيع والتجميع
    manufacturing_cost = board_cost * 1.5  # تقدير تكلفة التصنيع
    assembly_cost = len(components) * 0.1  # تكلفة تجميع لكل مكون
    
    return board_cost + component_cost + manufacturing_cost + assembly_cost

@app.get("/export/{design_id}")
async def export_design(design_id: str, format: str = "kicad"):
    """تصدير التصميم بالصيغة المطلوبة"""
    try:
        # استرجاع التصميم من قاعدة البيانات
        # تصدير التصميم بالصيغة المطلوبة
        if format == "kicad":
            content = pcb_generator.export_to_kicad(...)
            return {"content": content}
        else:
            raise HTTPException(status_code=400, detail="صيغة غير مدعومة")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
