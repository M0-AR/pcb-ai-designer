import matplotlib.pyplot as plt
from pcb_generator import PCBGenerator
import numpy as np
from shapely.geometry import Polygon, Point, LineString
import matplotlib.patches as patches

def plot_board_design(outline: Polygon, components: list, routes: list = None):
    """رسم تصميم اللوحة مع المكونات والمسارات"""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # رسم حدود اللوحة
    x, y = outline.exterior.xy
    ax.plot(x, y, 'b-', linewidth=2, label='Board Outline')
    
    # رسم المكونات
    colors = plt.cm.Set3(np.linspace(0, 1, len(components)))
    for comp, color in zip(components, colors):
        rect = patches.Rectangle(
            (comp['x'], comp['y']),
            comp['width'],
            comp['height'],
            linewidth=1,
            edgecolor='black',
            facecolor=color,
            alpha=0.5,
            label=comp.get('name', 'Component')
        )
        ax.add_patch(rect)
        # إضافة اسم المكون
        ax.text(
            comp['x'] + comp['width']/2,
            comp['y'] + comp['height']/2,
            comp.get('name', ''),
            horizontalalignment='center',
            verticalalignment='center'
        )
    
    # رسم المسارات
    if routes:
        for route in routes:
            x, y = route.xy
            ax.plot(x, y, 'r--', linewidth=1, alpha=0.5)
    
    # تنسيق الرسم
    ax.set_aspect('equal')
    ax.grid(True)
    ax.legend()
    plt.title('PCB Design Layout')
    plt.show()

def test_simple_design():
    """اختبار تصميم بسيط للوحة"""
    generator = PCBGenerator()
    
    # تجربة تصميم بسيط
    description = """
    دائرة تحكم في درجة الحرارة تحتوي على:
    - متحكم دقيق ATmega328P
    - حساس درجة حرارة LM35
    - شاشة LCD 16x2
    - منظم جهد 7805
    """
    
    # تحليل المتطلبات
    print("تحليل المتطلبات...")
    requirements = generator.analyze_requirements(description)
    
    # إنشاء مكونات للاختبار
    test_components = [
        {
            'name': 'ATmega328P',
            'width': 20,
            'height': 20,
            'x': 0,
            'y': 0,
            'type': 'microcontroller'
        },
        {
            'name': 'LM35',
            'width': 10,
            'height': 10,
            'x': 30,
            'y': 0,
            'type': 'sensor'
        },
        {
            'name': 'LCD16x2',
            'width': 30,
            'height': 15,
            'x': 0,
            'y': 30,
            'type': 'display'
        },
        {
            'name': 'LM7805',
            'width': 10,
            'height': 10,
            'x': 40,
            'y': 30,
            'type': 'power'
        }
    ]
    
    print("توليد حدود اللوحة...")
    outline = generator.generate_board_outline(test_components, {})
    
    print("تحسين توزيع المكونات...")
    placed_components = generator.optimize_component_placement(outline, test_components)
    
    print("توليد مسارات التوصيل...")
    routes = generator.generate_routing(placed_components, outline)
    
    # عرض النتائج
    print("\nنتائج التصميم:")
    print(f"عدد المكونات: {len(placed_components)}")
    print(f"مساحة اللوحة: {outline.area:.2f} مم²")
    
    # رسم التصميم
    plot_board_design(outline, placed_components, routes)

def test_complex_design():
    """اختبار تصميم معقد للوحة"""
    generator = PCBGenerator()
    
    # وصف لدائرة أكثر تعقيداً
    description = """
    دائرة تحكم روبوت تحتوي على:
    - متحكم STM32F103
    - حساس MPU6050 للحركة
    - محرك سيرفو SG90 عدد 2
    - شاشة OLED 128x64
    - بطارية ليثيوم مع دائرة شحن
    - مستشعر مسافة ultrasonic
    """
    
    # إنشاء مكونات معقدة للاختبار
    test_components = [
        {
            'name': 'STM32F103',
            'width': 25,
            'height': 25,
            'x': 0,
            'y': 0,
            'type': 'microcontroller'
        },
        {
            'name': 'MPU6050',
            'width': 15,
            'height': 15,
            'x': 30,
            'y': 0,
            'type': 'sensor'
        },
        {
            'name': 'Servo1',
            'width': 20,
            'height': 10,
            'x': 0,
            'y': 30,
            'type': 'motor'
        },
        {
            'name': 'Servo2',
            'width': 20,
            'height': 10,
            'x': 25,
            'y': 30,
            'type': 'motor'
        },
        {
            'name': 'OLED',
            'width': 30,
            'height': 20,
            'x': 50,
            'y': 0,
            'type': 'display'
        },
        {
            'name': 'Battery',
            'width': 40,
            'height': 20,
            'x': 50,
            'y': 30,
            'type': 'power'
        },
        {
            'name': 'Ultrasonic',
            'width': 20,
            'height': 15,
            'x': 0,
            'y': 50,
            'type': 'sensor'
        }
    ]
    
    print("توليد حدود اللوحة...")
    outline = generator.generate_board_outline(test_components, {})
    
    print("تحسين توزيع المكونات...")
    placed_components = generator.optimize_component_placement(outline, test_components)
    
    print("توليد مسارات التوصيل...")
    routes = generator.generate_routing(placed_components, outline)
    
    # عرض النتائج
    print("\nنتائج التصميم:")
    print(f"عدد المكونات: {len(placed_components)}")
    print(f"مساحة اللوحة: {outline.area:.2f} مم²")
    
    # رسم التصميم
    plot_board_design(outline, placed_components, routes)

if __name__ == "__main__":
    print("اختبار تصميم بسيط...")
    test_simple_design()
    
    print("\nاختبار تصميم معقد...")
    test_complex_design()
