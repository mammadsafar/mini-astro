"use client"

import type React from "react"
import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Modal, ModalHeader, ModalTitle } from "@/components/ui/modal"
import { Checkbox } from "@/components/ui/checkbox"
import { toast } from "@/hooks/use-toast"
import {
  Plus,
  Edit,
  Trash2,
  Copy,
  Moon,
  Sun,
  MapPin,
  Calendar,
  Clock,
  Users,
  Star,
  Zap,
  Heart,
  FileText,
} from "lucide-react"

interface Person {
  id: string
  name: string
  birthdate: string // "YYYY-MM-DD"
  birthtime: string // "HH:mm"
  city: string
  lat: number
  lng: number
  tz_str: string
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || ""

export default function AstrologyChartApp() {
  const [people, setPeople] = useState<Person[]>([])
  const [selectedPeople, setSelectedPeople] = useState<string[]>([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingPerson, setEditingPerson] = useState<Person | null>(null)
  const [isDarkMode, setIsDarkMode] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    birthdate: "",
    birthtime: "",
    city: "",
    lat: 0,
    lng: 0,
    tz_str: "Asia/Tehran",
  })

  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const markerRef = useRef<any>(null)

  const [chartModalOpen, setChartModalOpen] = useState(false)
  const [chartContent, setChartContent] = useState("")
  const [chartType, setChartType] = useState<"json" | "svg" | null>(null)

  // Initialize Leaflet map on modal open
  useEffect(() => {
    if (typeof window !== "undefined" && mapRef.current && isModalOpen) {
      const L = (window as any).L
      if (L && !mapInstanceRef.current) {
        mapInstanceRef.current = L.map(mapRef.current).setView([35.6892, 51.389], 5)
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "© OpenStreetMap contributors",
        }).addTo(mapInstanceRef.current)

        mapInstanceRef.current.on("click", (e: any) => {
          const { lat, lng } = e.latlng
          setFormData((prev) => ({ ...prev, lat, lng }))

          if (markerRef.current) {
            mapInstanceRef.current.removeLayer(markerRef.current)
          }
          markerRef.current = L.marker([lat, lng]).addTo(mapInstanceRef.current)
        })
      }

      if (mapInstanceRef.current) {
        setTimeout(() => mapInstanceRef.current.invalidateSize(), 100)
      }
    }
  }, [isModalOpen])

  // Load people from API
  useEffect(() => {
    loadPeople()
  }, [])

  const loadPeople = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`${API_URL}/users/`)
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`)

      const data = await response.json()

      // Map data to Person[]
      const safePeople: Person[] = data.map((person: any, index: number) => {
        const year = typeof person.year === "number" ? person.year : 0
        const month = typeof person.month === "number" ? person.month : 0
        const day = typeof person.day === "number" ? person.day : 0
        const hour = typeof person.hour === "number" ? person.hour : 0
        const minute = typeof person.minute === "number" ? person.minute : 0

        const birthdate = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`
        const birthtime = `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`

        return {
          id: person.id?.toString() || index.toString(),
          name: person.name || "",
          birthdate,
          birthtime,
          city: person.city || "",
          lat: typeof person.lat === "number" ? person.lat : 0,
          lng: typeof person.lng === "number" ? person.lng : 0,
          tz_str: person.tz_str || "Asia/Tehran",
        }
      })

      setPeople(safePeople)
    } catch (error) {
      console.error("خطا در دریافت اطلاعات:", error)
      alert(`❌ خطا در اتصال به سرور. لطفاً مطمئن شوید که سرور روی ${API_URL} در حال اجرا است.`)
      setPeople([])
    } finally {
      setIsLoading(false)
    }
  }

  // City search function using OpenStreetMap Nominatim API
  const searchCity = async (query: string) => {
    if (!query.trim()) return
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`
      )
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`)

      const data = await response.json()
      if (data.length > 0) {
        const lat = Number.parseFloat(data[0].lat)
        const lng = Number.parseFloat(data[0].lon)

        setFormData((prev) => ({ ...prev, lat, lng }))

        if (mapInstanceRef.current) {
          if (markerRef.current) {
            mapInstanceRef.current.removeLayer(markerRef.current)
          }
          markerRef.current = (window as any).L.marker([lat, lng]).addTo(mapInstanceRef.current)
          mapInstanceRef.current.setView([lat, lng], 10)
        }
      }
    } catch (error) {
      console.error("خطا در جستجوی شهر:", error)
    }
  }

  // Handle form submission to add or update person
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.lat || !formData.lng) {
      alert("لطفاً محل تولد را روی نقشه مشخص کنید")
      return
    }

    // Extract year, month, day from birthdate string "YYYY-MM-DD"
    const [year, month, day] = formData.birthdate.split("-").map(Number)
    // Extract hour, minute from birthtime string "HH:mm"
    const [hour, minute] = formData.birthtime.split(":").map(Number)

    const personData = {
      id: editingPerson?.id || Date.now().toString(),
      name: formData.name,
      year,
      month,
      day,
      hour,
      minute,
      lat: formData.lat,
      lng: formData.lng,
      city: formData.city,
      tz_str: formData.tz_str || Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Tehran",
      birthdate: formData.birthdate,
      birthtime: formData.birthtime,
    }

    try {
      setIsLoading(true)

      if (editingPerson) {
        // Update existing person
        try {
          const response = await fetch(`${API_URL}/users/${editingPerson.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(personData),
          })
          if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`)

          setPeople((prev) => prev.map((p) => (p.id === editingPerson.id ? personData : p)))
          alert("اطلاعات با موفقیت به‌روزرسانی شد")
        } catch {
          setPeople((prev) => prev.map((p) => (p.id === editingPerson.id ? personData : p)))
          alert("سرور در دسترس نیست. اطلاعات به صورت محلی ذخیره شد.")
        }
      } else {
        // Add new person
        try {
          const response = await fetch(`${API_URL}/users/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(personData),
          })
          if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`)

          setPeople((prev) => [...prev, personData])
          alert("فرد جدید با موفقیت اضافه شد")
        } catch {
          setPeople((prev) => [...prev, personData])
          alert("سرور در دسترس نیست. فرد به صورت محلی اضافه شد.")
        }
      }
    } catch (error: any) {
      console.error("خطا در ذخیره اطلاعات:", error)
      alert("خطا در ذخیره اطلاعات: " + error.message)
    } finally {
      setIsLoading(false)
      closeModal()
    }
  }

  // Delete person by ID
  const deletePerson = async (id: string) => {
    if (!confirm("آیا از حذف این فرد مطمئن هستید؟")) return

    try {
      setIsLoading(true)
      try {
        const response = await fetch(`${API_URL}/users/${id}`, { method: "DELETE" })
        if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`)

        setPeople((prev) => prev.filter((p) => p.id !== id))
        setSelectedPeople((prev) => prev.filter((pid) => pid !== id))
        alert("فرد با موفقیت حذف شد")
      } catch {
        setPeople((prev) => prev.filter((p) => p.id !== id))
        setSelectedPeople((prev) => prev.filter((pid) => pid !== id))
        alert("سرور در دسترس نیست. فرد به صورت محلی حذف شد.")
      }
    } catch (error: any) {
      console.error("خطا در حذف:", error)
      alert("خطا در حذف فرد: " + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  // Copy person JSON to clipboard
  const copyPersonJson = (person: Person) => {
    navigator.clipboard.writeText(JSON.stringify(person, null, 2))
    toast({ title: "کپی شد", description: "اطلاعات در کلیپ‌بورد کپی شد" })
  }

  // Open modal for add/edit
  const openModal = (person?: Person) => {
    if (person) {
      setEditingPerson(person)
      setFormData({
        name: person.name,
        birthdate: person.birthdate,
        birthtime: person.birthtime,
        city: person.city,
        lat: person.lat,
        lng: person.lng,
        tz_str: person.tz_str || "Asia/Tehran",
      })

      if (mapInstanceRef.current) {
        if (markerRef.current) {
          mapInstanceRef.current.removeLayer(markerRef.current)
        }
        markerRef.current = (window as any).L.marker([person.lat, person.lng]).addTo(mapInstanceRef.current)
        mapInstanceRef.current.setView([person.lat, person.lng], 10)
      }
    } else {
      setEditingPerson(null)
      setFormData({
        name: "",
        birthdate: "",
        birthtime: "",
        city: "",
        lat: 0,
        lng: 0,
        tz_str: "Asia/Tehran",
      })

      if (markerRef.current && mapInstanceRef.current) {
        mapInstanceRef.current.removeLayer(markerRef.current)
        markerRef.current = null
      }
    }
    setIsModalOpen(true)
  }

  // Close modal and clean up marker
  const closeModal = () => {
    setIsModalOpen(false)
    setEditingPerson(null)
    if (markerRef.current && mapInstanceRef.current) {
      mapInstanceRef.current.removeLayer(markerRef.current)
      markerRef.current = null
    }
  }

  // Generate chart request
  const generateChart = async (type: string) => {
    const selectedPeopleData = people.filter((p) => selectedPeople.includes(p.id))

    if (
      (["natal", "transit", "report"].includes(type) && selectedPeopleData.length !== 1) ||
      (["synastry", "composite"].includes(type) && selectedPeopleData.length !== 2)
    ) {
      alert("تعداد افراد انتخاب شده با نوع چارت مطابقت ندارد")
      return
    }

    const toPayload = (person: Person) => {
      const [year, month, day] = person.birthdate.split("-").map(Number)
      const [hour, minute] = person.birthtime.split(":").map(Number)

      return {
        name: person.name,
        year,
        month,
        day,
        hour,
        minute,
        lat: person.lat,
        lng: person.lng,
        city: person.city,
        tz_str: person.tz_str,
      }
    }

    let url = ""
    let payload: any = {}

    switch (type) {
      case "natal":
        url = `${API_URL}/astro/chart-json`
        payload = toPayload(selectedPeopleData[0])
        break
      case "transit":
        url = `${API_URL}/astro/chart-svg`
        payload = toPayload(selectedPeopleData[0])
        break
      case "report":
        url = `${API_URL}/astro/report`
        payload = toPayload(selectedPeopleData[0])
        break
      case "synastry":
        url = `${API_URL}/astro/synastry`
        payload = {
          person1: toPayload(selectedPeopleData[0]),
          person2: toPayload(selectedPeopleData[1]),
        }
        break
      case "composite":
        url = `${API_URL}/astro/composite`
        payload = {
          person1: toPayload(selectedPeopleData[0]),
          person2: toPayload(selectedPeopleData[1]),
        }
        break
    }

    try {
      setIsLoading(true)
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`)

      const contentType = response.headers.get("content-type")
      if (contentType?.includes("application/json")) {
        const data = await response.json()
        setChartType("json")
        setChartContent(JSON.stringify(data, null, 2))
      } else {
        const svg = await response.text()
        setChartType("svg")
        setChartContent(svg)
      }
      setChartModalOpen(true)
    } catch (error: any) {
      console.error("خطا در تولید چارت:", error)
      if (error.message.includes("fetch")) {
        alert("خطا در اتصال به سرور آسترولوژی. لطفاً مطمئن شوید که سرور روی localhost:3330 در حال اجرا است.")
      } else {
        alert("خطا در تولید چارت: " + error.message)
      }
    } finally {
      setIsLoading(false)
    }
  }

  // Toggle person selection checkbox
  const togglePersonSelection = (personId: string) => {
    setSelectedPeople((prev) =>
      prev.includes(personId) ? prev.filter((id) => id !== personId) : [...prev, personId]
    )
  }

  return (
    <div
      className={`min-h-screen transition-all duration-300 ${
        isDarkMode
          ? "bg-gradient-to-br from-slate-900 via-blue-900 to-emerald-900"
          : "bg-gradient-to-br from-blue-50 via-emerald-50 to-teal-50"
      }`}
    >
      {/* Load Leaflet CSS and JS */}
      <link
        rel="stylesheet"
        href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        integrity="sha256-sA+6XrL2gspzYDk7fDFaLtlAB1kA6eKc06W0c3pJW6M="
        crossOrigin=""
      />
      <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

      <div className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div
          className={`backdrop-blur-md rounded-2xl border p-6 ${
            isDarkMode ? "bg-white/10 border-white/20 text-white" : "bg-white/40 border-white/60 text-gray-800"
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Star className="w-8 h-8 text-emerald-400" />
              <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-blue-500 bg-clip-text text-transparent">
                برنامه تحلیل چارت نجومی
              </h1>
            </div>

            <Button variant="outline" size="sm" onClick={() => setIsDarkMode(!isDarkMode)}>
              {isDarkMode ? <Sun /> : <Moon />}
            </Button>
          </div>
        </div>

        {/* People List & Actions */}
        <div
          className={`backdrop-blur-md rounded-2xl border p-6 ${
            isDarkMode ? "bg-white/10 border-white/20 text-white" : "bg-white/40 border-white/60 text-gray-800"
          }`}
        >
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <h2 className="text-xl font-semibold">افراد</h2>
            <Button onClick={() => openModal()}>
              <Plus className="w-5 h-5" /> اضافه کردن فرد جدید
            </Button>
          </div>

          {isLoading && <p>در حال بارگذاری...</p>}
          {!isLoading && people.length === 0 && <p>هیچ فردی وجود ندارد.</p>}

          {people.length > 0 && (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {people.map((person) => (
                <Card
                  key={person.id}
                  className={`cursor-pointer ${
                    selectedPeople.includes(person.id)
                      ? "bg-emerald-800 text-white"
                      : isDarkMode
                      ? "bg-white/10 text-white"
                      : "bg-white text-gray-800"
                  }`}
                >
                  <CardContent className="flex items-center justify-between gap-2">
                    <Checkbox
                      checked={selectedPeople.includes(person.id)}
                      onChange={() => togglePersonSelection(person.id)}
                      aria-label={`انتخاب ${person.name}`}
                    />
                    <div className="flex-grow" onClick={() => openModal(person)}>
                      <h3 className="font-semibold text-lg">{person.name}</h3>
                      <p>
                        تولد: {person.birthdate} {person.birthtime} - شهر: {person.city}
                      </p>
                    </div>

                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyPersonJson(person)}
                        aria-label="کپی اطلاعات"
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deletePerson(person.id)}
                        aria-label="حذف فرد"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Chart Buttons */}
          <div className="mt-6 flex flex-wrap gap-3">
            <Button
              disabled={selectedPeople.length !== 1}
              onClick={() => generateChart("natal")}
              variant="outline"
            >
              چارت تولد (Natal)
            </Button>
            <Button
              disabled={selectedPeople.length !== 1}
              onClick={() => generateChart("transit")}
              variant="outline"
            >
              چارت ترانزیت (Transit)
            </Button>
            <Button
              disabled={selectedPeople.length !== 1}
              onClick={() => generateChart("report")}
              variant="outline"
            >
              گزارش تحلیلی
            </Button>
            <Button
              disabled={selectedPeople.length !== 2}
              onClick={() => generateChart("synastry")}
              variant="outline"
            >
              سینستری (Synastry)
            </Button>
            <Button
              disabled={selectedPeople.length !== 2}
              onClick={() => generateChart("composite")}
              variant="outline"
            >
              کامپوزیت (Composite)
            </Button>
          </div>
        </div>

        {/* Modal Form */}
        {isModalOpen && (
          <Modal open={isModalOpen} onOpenChange={closeModal}>
            <ModalHeader>
              <ModalTitle>{editingPerson ? "ویرایش فرد" : "اضافه کردن فرد جدید"}</ModalTitle>
            </ModalHeader>

            <form onSubmit={handleSubmit} className="space-y-4 p-4 max-w-xl mx-auto">
              <div>
                <Label htmlFor="name">نام</Label>
                <Input
                  id="name"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="نام را وارد کنید"
                />
              </div>

              <div>
                <Label htmlFor="birthdate">تاریخ تولد</Label>
                <Input
                  type="date"
                  id="birthdate"
                  required
                  value={formData.birthdate}
                  onChange={(e) => setFormData({ ...formData, birthdate: e.target.value })}
                />
              </div>

              <div>
                <Label htmlFor="birthtime">زمان تولد</Label>
                <Input
                  type="time"
                  id="birthtime"
                  required
                  value={formData.birthtime}
                  onChange={(e) => setFormData({ ...formData, birthtime: e.target.value })}
                />
              </div>

              <div>
                <Label htmlFor="city">شهر</Label>
                <Input
                  id="city"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  placeholder="نام شهر"
                  onBlur={(e) => searchCity(e.target.value)}
                />
                <small className="text-xs text-gray-400">با خارج شدن از فیلد، شهر جستجو می‌شود</small>
              </div>

              <div
                id="map"
                ref={mapRef}
                className="w-full h-48 rounded-md border border-gray-300"
                style={{ minHeight: 200 }}
              ></div>

              <div className="flex justify-end gap-3 mt-4">
                <Button type="button" variant="outline" onClick={closeModal}>
                  انصراف
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {editingPerson ? "به‌روزرسانی" : "اضافه کردن"}
                </Button>
              </div>
            </form>
          </Modal>
        )}

        {/* Chart Modal */}
        {chartModalOpen && (
          <Modal open={chartModalOpen} onOpenChange={() => setChartModalOpen(false)}>
            <ModalHeader>
              <ModalTitle>نمایش چارت</ModalTitle>
            </ModalHeader>
            <CardContent>
              {chartType === "json" && (
                <pre className="overflow-auto max-h-[400px] bg-gray-900 text-green-300 p-4 rounded-md">
                  {chartContent}
                </pre>
              )}
              {chartType === "svg" && (
                <div
                  className="overflow-auto max-h-[400px]"
                  dangerouslySetInnerHTML={{ __html: chartContent }}
                />
              )}
            </CardContent>
          </Modal>
        )}
      </div>
    </div>
  )
}
