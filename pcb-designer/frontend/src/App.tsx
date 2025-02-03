import { useState } from 'react'
import './App.css'

interface CircuitSpecifications {
  maxBudget: number;
  tempRange: 'normal' | 'industrial' | 'extreme';
  boardSize: 'small' | 'medium' | 'large';
}

interface Component {
  name: string;
  description: string;
  voltage: string;
  price: number;
  quantity: number;
  package: string;
}

interface CircuitResponse {
  components: Component[];
  schematic_url: string;
  gerber_url: string;
  bom_url: string;
  estimated_cost: number;
  manufacturing_time: string;
  circuit_id: string;
  design_notes: string[];
  specifications: CircuitSpecifications;
  thermal_analysis: {
    max_temperature: number;
    ambient_temperature: number;
    temperature_rise: number;
    thermal_resistance: number;
  };
  power_consumption: number;
}

function App() {
  const [description, setDescription] = useState('')
  const [specifications, setSpecifications] = useState<CircuitSpecifications>({
    maxBudget: 100,
    tempRange: 'normal',
    boardSize: 'medium'
  })
  const [design, setDesign] = useState<CircuitResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const generateDesign = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/generate-design', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description,
          specifications
        })
      })
      const data = await response.json()
      setDesign(data)
    } catch (error) {
      console.error('Error:', error)
      alert('حدث خطأ أثناء إنشاء التصميم')
    }
    setLoading(false)
  }

  const submitOrder = async () => {
    if (!design?.circuit_id) return
    try {
      const response = await fetch('http://localhost:8000/submit-order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          circuit_id: design.circuit_id
        })
      })
      const data = await response.json()
      alert('تم استلام طلبك بنجاح!\nرقم الطلب: ' + data.order_id)
    } catch (error) {
      console.error('Error:', error)
      alert('حدث خطأ أثناء تأكيد الطلب')
    }
  }

  return (
    <div className="container mx-auto p-4" dir="rtl">
      <header className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">مصمم الدوائر الإلكترونية الذكي</h1>
        <p className="text-gray-600">وصف دائرتك بكلمات بسيطة، ودع الذكاء الاصطناعي يقوم بالباقي</p>
      </header>

      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            وصف الدائرة المطلوبة
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={4}
            placeholder="مثال: دائرة تحكم في درجة الحرارة مع شاشة LCD ومروحة تبريد"
          />
        </div>

        <div className="mb-4">
          <details className="bg-gray-50 rounded p-2">
            <summary className="text-gray-700 font-semibold cursor-pointer">خيارات متقدمة</summary>
            <div className="mt-2 space-y-2">
              <div>
                <label className="block text-sm text-gray-600">الميزانية القصوى (دولار)</label>
                <input
                  type="number"
                  value={specifications.maxBudget}
                  onChange={(e) => setSpecifications({...specifications, maxBudget: parseFloat(e.target.value)})}
                  className="border rounded px-2 py-1"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600">درجة الحرارة المحيطة</label>
                <select
                  value={specifications.tempRange}
                  onChange={(e) => setSpecifications({...specifications, tempRange: e.target.value as 'normal' | 'industrial' | 'extreme'})}
                  className="border rounded px-2 py-1"
                >
                  <option value="normal">عادية (0-50°C)</option>
                  <option value="industrial">صناعية (-40-85°C)</option>
                  <option value="extreme">متطرفة (-55-125°C)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-600">حجم اللوحة</label>
                <select
                  value={specifications.boardSize}
                  onChange={(e) => setSpecifications({...specifications, boardSize: e.target.value as 'small' | 'medium' | 'large'})}
                  className="border rounded px-2 py-1"
                >
                  <option value="small">صغير</option>
                  <option value="medium">متوسط</option>
                  <option value="large">كبير</option>
                </select>
              </div>
            </div>
          </details>
        </div>

        <button
          onClick={generateDesign}
          disabled={loading}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors disabled:bg-gray-400"
        >
          {loading ? 'جاري إنشاء التصميم...' : 'إنشاء التصميم'}
        </button>
      </div>

      {design && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold mb-4">مخطط الدائرة</h2>
              <div className="border rounded-lg p-4 mb-4 min-h-[300px]">
                <img src={`http://localhost:8000${design.schematic_url}`} alt="مخطط الدائرة" className="w-full h-auto" />
              </div>
              <a
                href={`http://localhost:8000${design.schematic_url}`}
                download
                className="block w-full bg-green-500 text-white text-center py-2 px-4 rounded-lg hover:bg-green-600 transition-colors"
              >
                تحميل المخطط (SVG)
              </a>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold mb-4">قائمة المكونات</h2>
              <div className="mb-4">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-right py-2">المكون</th>
                      <th className="text-right py-2">الكمية</th>
                      <th className="text-right py-2">السعر</th>
                    </tr>
                  </thead>
                  <tbody>
                    {design.components.map((comp, index) => (
                      <tr key={index} className="border-b">
                        <td className="py-2">{comp.name}</td>
                        <td className="py-2">{comp.quantity}</td>
                        <td className="py-2">${comp.price}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="flex space-x-4 rtl:space-x-reverse">
                <a
                  href={`http://localhost:8000${design.bom_url}`}
                  download
                  className="flex-1 bg-green-500 text-white text-center py-2 px-4 rounded-lg hover:bg-green-600 transition-colors"
                >
                  تحميل BOM
                </a>
                <a
                  href={`http://localhost:8000${design.gerber_url}`}
                  download
                  className="flex-1 bg-green-500 text-white text-center py-2 px-4 rounded-lg hover:bg-green-600 transition-colors"
                >
                  تحميل Gerber
                </a>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
            <h2 className="text-xl font-bold mb-4">تفاصيل المشروع</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border rounded-lg p-4">
                <h3 className="font-bold text-gray-700 mb-2">التكلفة التقديرية</h3>
                <p className="text-2xl font-bold text-green-600">${design.estimated_cost}</p>
              </div>
              <div className="border rounded-lg p-4">
                <h3 className="font-bold text-gray-700 mb-2">وقت التصنيع</h3>
                <p className="text-2xl font-bold text-blue-600">{design.manufacturing_time}</p>
              </div>
              <div className="border rounded-lg p-4">
                <h3 className="font-bold text-gray-700 mb-2">استهلاك الطاقة</h3>
                <p className="text-2xl font-bold text-purple-600">{design.power_consumption}W</p>
              </div>
            </div>

            <div className="mt-4">
              <h3 className="font-bold text-gray-700 mb-2">التحليل الحراري</h3>
              <ul className="list-disc list-inside space-y-1">
                <li>درجة الحرارة القصوى: {design.thermal_analysis.max_temperature}°C</li>
                <li>درجة الحرارة المحيطة: {design.thermal_analysis.ambient_temperature}°C</li>
                <li>ارتفاع درجة الحرارة: {design.thermal_analysis.temperature_rise}°C</li>
                <li>المقاومة الحرارية: {design.thermal_analysis.thermal_resistance}°C/W</li>
              </ul>
            </div>

            <div className="mt-4">
              <h3 className="font-bold text-gray-700 mb-2">ملاحظات التصميم</h3>
              <ul className="list-disc list-inside space-y-1">
                {design.design_notes.map((note, index) => (
                  <li key={index}>{note}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="flex justify-between mt-6">
            <button
              onClick={() => setDesign(null)}
              className="bg-yellow-500 text-white py-2 px-6 rounded-lg hover:bg-yellow-600 transition-colors"
            >
              تعديل التصميم
            </button>
            <button
              onClick={submitOrder}
              className="bg-blue-500 text-white py-2 px-6 rounded-lg hover:bg-blue-600 transition-colors"
            >
              تأكيد الطلب
            </button>
          </div>
        </>
      )}
    </div>
  )
}

export default App
