from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Dict, Optional
import json
import os
from datetime import datetime
import schemdraw
from schemdraw import elements as elm
from schemdraw.segments import *
from transformers import pipeline
import re

app = FastAPI(title="PCB Designer API")

# إضافة دعم CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تهيئة نموذج معالجة اللغة الطبيعية
generator = pipeline('text-generation', model='gpt2')

def analyze_circuit_requirements(description: str) -> Dict:
    """تحليل متطلبات الدائرة باستخدام نموذج اللغة الطبيعية"""
    # إنشاء نص الإدخال للنموذج
    prompt = f"""
    Based on this circuit description: "{description}"
    Analyze and list all required components with their specifications.
    Consider voltage levels, current requirements, and temperature constraints.
    Format the response as a structured list of components.
    Include specific part numbers, voltage ratings, and key specifications.
    """
    
    # توليد الاستجابة من النموذج
    response = generator(prompt, max_length=500, num_return_sequences=1)[0]['generated_text']
    
    # تحليل الاستجابة وتحويلها إلى قائمة مكونات منظمة
    components = parse_llm_response(response)
    return components

def parse_llm_response(response: str) -> List[Dict]:
    """تحليل استجابة نموذج اللغة وتحويلها إلى قائمة مكونات"""
    components = []
    
    # استخراج المكونات من النص
    component_sections = re.split(r'\n\d+\.|\n-', response)
    
    for section in component_sections:
        if not section.strip():
            continue
            
        # تحليل كل قسم للحصول على معلومات المكون
        comp = extract_component_info(section)
        if comp:
            components.append(comp)
    
    return components

def extract_component_info(text: str) -> Optional[Dict]:
    """استخراج معلومات المكون من النص"""
    # أنماط للبحث عن المعلومات الرئيسية
    patterns = {
        'name': r'([A-Z0-9]+(?:-[A-Z0-9]+)*)',
        'voltage': r'(\d+(?:\.\d+)?V)',
        'current': r'(\d+(?:\.\d+)?[mu]?A)',
        'temperature': r'(-?\d+°C)',
        'package': r'(SOT-?23|TO-?220|DIP-?\d+|SOIC-?\d+)',
    }
    
    info = {}
    
    # البحث عن المعلومات باستخدام الأنماط
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            info[key] = match.group(1)
    
    # إضافة معلومات إضافية
    if info:
        info['description'] = text.split('\n')[0].strip()
        info['price'] = estimate_component_price(info)
        
    return info if info else None

def estimate_component_price(component_info: Dict) -> float:
    """تقدير سعر المكون بناءً على مواصفاته"""
    base_price = 1.0
    
    # تعديل السعر بناءً على نوع المكون
    if 'name' in component_info:
        name = component_info['name'].lower()
        if 'stm32' in name or 'arm' in name:
            base_price = 6.0
        elif 'atmega' in name:
            base_price = 4.0
        elif 'sensor' in name or 'mpu' in name:
            base_price = 3.0
            
    # تعديل السعر بناءً على الجهد
    if 'voltage' in component_info:
        voltage = float(component_info['voltage'].replace('V', ''))
        if voltage > 12:
            base_price *= 1.5
            
    # تعديل السعر بناءً على نوع الحزمة
    if 'package' in component_info:
        if 'SOIC' in component_info['package'] or 'SOT' in component_info['package']:
            base_price *= 1.2
            
    return round(base_price, 2)

def generate_schematic(components: List[Dict]) -> str:
    """إنشاء المخطط الكهربائي للدائرة"""
    d = schemdraw.Drawing()
    
    # تنظيم المكونات حسب نوعها
    component_layout = organize_components(components)
    
    # رسم المكونات
    x, y = 0, 0
    spacing = 3
    
    for comp_type, comps in component_layout.items():
        for comp in comps:
            if 'microcontroller' in comp_type.lower():
                d += (elm.Dot().at((x, y))
                     + elm.Rect().at((x, y)).label(comp['name']))
                x += spacing
                
            elif 'sensor' in comp_type.lower():
                d += (elm.Dot().at((x, y))
                     + elm.Rect2().at((x, y)).label(comp['name']))
                y += spacing
                
            elif 'display' in comp_type.lower():
                d += (elm.Dot().at((x, y))
                     + elm.Rect().at((x, y)).label(comp['name']))
                x -= spacing
                
            elif 'power' in comp_type.lower():
                d += (elm.Dot().at((x, y))
                     + elm.BatteryCell().at((x, y)).label(comp['name']))
                y -= spacing
                
            # إضافة التوصيلات
            if x != 0 or y != 0:
                d += elm.Line().at((x-spacing, y)).to((x, y))
    
    # حفظ المخطط
    filename = f'temp_files/schematic_{datetime.now().strftime("%Y%m%d_%H%M%S")}.svg'
    d.save(filename)
    return filename

def organize_components(components: List[Dict]) -> Dict[str, List[Dict]]:
    """تنظيم المكونات حسب نوعها"""
    organized = {}
    
    for comp in components:
        comp_type = determine_component_type(comp)
        if comp_type not in organized:
            organized[comp_type] = []
        organized[comp_type].append(comp)
    
    return organized

def determine_component_type(component: Dict) -> str:
    """تحديد نوع المكون"""
    name = component['name'].lower()
    
    if any(x in name for x in ['atmega', 'stm32', 'mcu']):
        return 'microcontroller'
    elif any(x in name for x in ['sensor', 'mpu', 'lm35']):
        return 'sensor'
    elif any(x in name for x in ['lcd', 'oled', 'display']):
        return 'display'
    elif any(x in name for x in ['7805', 'regulator', 'mp1584']):
        return 'power'
    else:
        return 'other'

@app.post("/generate-design")
async def generate_design(request: dict):
    try:
        # تحليل الوصف باستخدام نموذج اللغة
        components = analyze_circuit_requirements(request['description'])
        
        # حساب التكلفة الإجمالية
        total_cost = sum(comp['price'] for comp in components)
        
        # إنشاء المخطط
        schematic_file = generate_schematic(components)
        
        # تحضير الاستجابة
        return {
            'circuit_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'components': components,
            'schematic_url': f'/download/schematic/{os.path.basename(schematic_file)}',
            'estimated_cost': total_cost,
            'manufacturing_time': '7-10 أيام',
            'design_notes': [
                f'تم اختيار {len(components)} مكونات للدائرة',
                f'التكلفة التقديرية: ${total_cost:.2f}',
                'تم تحسين اختيار المكونات باستخدام الذكاء الاصطناعي'
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/schematic/{filename}")
async def download_schematic(filename: str):
    """تحميل ملف المخطط"""
    try:
        file_path = f"temp_files/{filename}"
        return FileResponse(file_path,
                          media_type="image/svg+xml",
                          filename=filename)
    except Exception as e:
        raise HTTPException(status_code=404, detail="الملف غير موجود")
