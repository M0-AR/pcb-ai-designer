# PCB AI Designer

مشروع لتصميم لوحات الدوائر المطبوعة (PCB) باستخدام الذكاء الاصطناعي. يقوم المشروع بتحويل الوصف النصي إلى تصميم PCB كامل مع تحسين الحدود وتوزيع المكونات.

## المميزات الرئيسية

1. **تحليل المتطلبات باستخدام AI**
   - تحليل الوصف النصي باستخدام نماذج اللغة الطبيعية
   - تحديد المكونات المطلوبة والمواصفات
   - استنتاج القيود والمتطلبات الفنية

2. **توليد حدود اللوحة الأمثل**
   - تحديد الحجم الأمثل للوحة
   - تحسين شكل الحدود لتقليل المساحة غير المستخدمة
   - مراعاة قيود التصنيع

3. **تحسين توزيع المكونات**
   - توزيع المكونات بشكل أمثل
   - تجنب التداخل بين المكونات
   - تحسين المسافات وتقليل طول المسارات

4. **توليد مسارات التوصيل**
   - إنشاء مسارات التوصيل بين المكونات
   - تجنب التقاطعات والتداخلات
   - تحسين طول المسارات

## متطلبات النظام

- Python 3.8+
- FastAPI
- PyTorch
- Transformers
- Shapely
- NetworkX
- OpenCV
- KiCad (للتصدير)

## التثبيت

1. إنشاء بيئة افتراضية:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
.\venv\Scripts\activate  # Windows
```

2. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

## الاستخدام

1. تشغيل الخادم:
```bash
uvicorn src.api.main:app --reload
```

2. إرسال طلب تصميم:
```bash
curl -X POST "http://localhost:8000/generate-design" \
     -H "Content-Type: application/json" \
     -d '{"description": "دائرة تحكم في درجة الحرارة مع شاشة LCD"}'
```

## مثال على الاستخدام

```python
from pcb_ai_designer import PCBGenerator

# إنشاء مثيل من المولد
generator = PCBGenerator()

# تحليل المتطلبات
requirements = generator.analyze_requirements(
    "دائرة تحكم في درجة الحرارة مع شاشة LCD وحساس LM35"
)

# توليد التصميم
board_outline = generator.generate_board_outline(
    requirements['components'],
    requirements['constraints']
)

# تحسين توزيع المكونات
placed_components = generator.optimize_component_placement(
    board_outline,
    requirements['components']
)

# توليد مسارات التوصيل
routes = generator.generate_routing(placed_components, board_outline)

# تصدير التصميم
kicad_file = generator.export_to_kicad(board_outline, placed_components, routes)
```

## المساهمة

نرحب بمساهماتكم! يرجى اتباع الخطوات التالية:

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة
3. تقديم Pull Request

## الترخيص

MIT License
