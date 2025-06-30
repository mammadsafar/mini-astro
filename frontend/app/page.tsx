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
  birthdate: string
  birthtime: string
  city: string
  lat: number
  lng: number
  tz_str: string
}

const API_URL = process.env.NEXT_PUBLIC_API_URL;


interface ChartData {
  type: "natal" | "transit" | "synastry" | "composite" | "report"
  people: Person[]
}

export default function AstrologyChartApp() {
  const [people, setPeople] = useState<Person[]>([])
  const [selectedPeople, setSelectedPeople] = useState<string[]>([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingPerson, setEditingPerson] = useState<Person | null>(null)
  const [isDarkMode, setIsDarkMode] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    year: 0,
    month: 0,
    day: 0,
    hour: 0,
    minute: 0,
    city: "",
    lat: 0,
    lng: 0,
    tz_str: "Asia/Tehran"
  })

  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const markerRef = useRef<any>(null)

  const [chartModalOpen, setChartModalOpen] = useState(false)
  const [chartContent, setChartContent] = useState("")
  const [chartType, setChartType] = useState<"json" | "svg" | null>(null)

  // Initialize map
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
    setIsLoading(true);

    const response = await fetch(`${API_URL}/users/`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    const safePeople: Person[] = data.map((person: any, index: number) => {
      const year = typeof person.year === "number" ? person.year : 0;
      const month = typeof person.month === "number" ? person.month : 0;
      const day = typeof person.day === "number" ? person.day : 0;
      const hour = typeof person.hour === "number" ? person.hour : 0;
      const minute = typeof person.minute === "number" ? person.minute : 0;

      const birthdate = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
      const birthtime = `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;

      return {
        id: person.id?.toString() || index.toString(),
        name: person.name || "",
        birthdate,
        birthtime,
        city: person.city || "",
        lat: typeof person.lat === "number" ? person.lat : 0,
        lng: typeof person.lng === "number" ? person.lng : 0,
        tz_str: person.tz_str || "Asia/Tehran"
      };
    });

    setPeople(safePeople);
  } catch (error) {
    console.error("خطا در دریافت اطلاعات:", error);
    alert(`❌ خطا در اتصال به سرور. لطفاً مطمئن شوید که سرور روی ${API_URL}L در حال اجرا است.`);
    setPeople([]);
  } finally {
    setIsLoading(false);
  }
};

  // const loadPeople = async () => {
  //   try {
  //     setIsLoading(true)
  //     const response = await fetch(`${API_URL}/users/`)
  //     if (response.ok) {
  //       const data = await response.json()
  //       console.log(data)
  //       const birthdate = `${person.year}-${String(person.month).padStart(2, "0")}-${String(person.day).padStart(2, "0")}`
  //       const birthtime = `${String(person.hour).padStart(2, "0")}:${String(person.minute).padStart(2, "0")}`

  //       setPeople(
  //         data.map((person: any, index: number) => ({
  //           ...person,
            
  //           id: person.id || index.toString(),
  //         })),
  //       )
  //     } else {
  //       throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  //     }
  //   } catch (error) {
  //     console.error("خطا در دریافت اطلاعات:", error)
  //     alert("خطا در اتصال به سرور. لطفاً مطمئن شوید که سرور روی localhost:3330 در حال اجرا است.")
  //     // Set empty array to prevent crashes
  //     setPeople([])
  //   } finally {
  //     setIsLoading(false)
  //   }
  // }

  const searchCity = async (query: string) => {
    if (!query.trim()) return

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`,
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

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
      } else {
        console.log("شهر پیدا نشد")
      }
    } catch (error) {
      console.error("خطا در جستجوی شهر:", error)
      // Don't show alert for city search errors as it's not critical
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.lat || !formData.lng) {
      alert("لطفاً محل تولد را روی نقشه مشخص کنید")
      return
    }

    const personData = {
      ...formData,
      tz_str: Intl.DateTimeFormat().resolvedOptions().timeZone,
      id: editingPerson?.id || Date.now().toString(),
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

          if (response.ok) {
            setPeople((prev) => prev.map((p) => (p.id === editingPerson.id ? personData : p)))
            alert("اطلاعات با موفقیت به‌روزرسانی شد")
          } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
          }
        } catch (fetchError) {
          // Update locally if server is not available
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

          if (response.ok) {
            setPeople((prev) => [...prev, personData])
            alert("فرد جدید با موفقیت اضافه شد")
          } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
          }
        } catch (fetchError) {
          // Add locally if server is not available
          setPeople((prev) => [...prev, personData])
          alert("سرور در دسترس نیست. فرد به صورت محلی اضافه شد.")
        }
      }
    } catch (error) {
      console.error("خطا در ذخیره اطلاعات:", error)
      alert("خطا در ذخیره اطلاعات: " + error.message)
    } finally {
      setIsLoading(false)
      closeModal()
    }
  }

  const deletePerson = async (id: string) => {
    if (!confirm("آیا از حذف این فرد مطمئن هستید؟")) return

    try {
      setIsLoading(true)

      try {
        const response = await fetch(`${API_URL}/users/${id}`, {
          method: "DELETE",
        })

        if (response.ok) {
          setPeople((prev) => prev.filter((p) => p.id !== id))
          setSelectedPeople((prev) => prev.filter((pid) => pid !== id))
          alert("فرد با موفقیت حذف شد")
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
      } catch (fetchError) {
        // Delete locally if server is not available
        setPeople((prev) => prev.filter((p) => p.id !== id))
        setSelectedPeople((prev) => prev.filter((pid) => pid !== id))
        alert("سرور در دسترس نیست. فرد به صورت محلی حذف شد.")
      }
    } catch (error) {
      console.error("خطا در حذف:", error)
      alert("خطا در حذف فرد: " + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const copyPersonJson = (person: Person) => {
    navigator.clipboard.writeText(JSON.stringify(person, null, 2))
    toast({
      title: "کپی شد",
      description: "اطلاعات در کلیپ‌بورد کپی شد",
    })
  }

  const openModal = (person?: Person) => {
    if (person) {
      setEditingPerson(person)
      console.log(person);
      const [year, month, day] = person.birthdate.split("-").map(Number);
      const [hour, minute] = person.birthtime.split(":").map(Number);
      console.log(person.birthdate);
      console.log(year);

      setFormData({
        name: person.name,
        year: year, 
        month: month, 
        day: day, 
        hour: hour, 
        minute: minute, 
        city: person.city,
        lat: person.lat,
        lng: person.lng,
        tz_str: person.tz_str,
      })
    } else {
      setEditingPerson(null)
      setFormData({
        name: "",
        year: 0, 
        month: 0, 
        day: 0, 
        hour: 0, 
        minute: 0, 
        city: "",
        lat: 0,
        lng: 0,
        tz_str: "Asia/Tehran"
      })
    }
    setIsModalOpen(true)
  }
    // name: str
    // year: int
    // month: int
    // day: int
    // hour: int
    // minute: int
    // lat: float
    // lng: float
    // city: str
    // tz_str: str
  const closeModal = () => {
    setIsModalOpen(false)
    setEditingPerson(null)
    if (markerRef.current && mapInstanceRef.current) {
      mapInstanceRef.current.removeLayer(markerRef.current)
      markerRef.current = null
    }
  }

  const generateChart = async (type: string) => {
    const selectedPeopleData = people.filter((p) => selectedPeople.includes(p.id))

    // Validation
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

    let url = "",
      payload: any = {}

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

      if (response.ok) {
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


      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    } catch (error) {
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

  const togglePersonSelection = (personId: string) => {
    setSelectedPeople((prev) => (prev.includes(personId) ? prev.filter((id) => id !== personId) : [...prev, personId]))
  }

  return (
    <div
      className={`min-h-screen transition-all duration-300 ${
        isDarkMode
          ? "bg-gradient-to-br from-slate-900 via-blue-900 to-emerald-900"
          : "bg-gradient-to-br from-blue-50 via-emerald-50 to-teal-50"
      }`}
    >
      {/* Load Leaflet CSS */}
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
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
              <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-blue-400 bg-clip-text text-transparent">
                چارت آسترولوژی
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsDarkMode(!isDarkMode)}
                className={`rounded-full ${isDarkMode ? "hover:bg-white/20" : "hover:bg-black/10"}`}
              >
                {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </Button>
              <Button
                onClick={() => openModal()}
                className="bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600 text-white rounded-full"
              >
                <Plus className="w-4 h-4 mr-2" />
                افزودن فرد جدید
              </Button>
            </div>
          </div>
        </div>

        {/* People List */}
        <Card
          className={`backdrop-blur-md border ${
            isDarkMode ? "bg-white/10 border-white/20 text-white" : "bg-white/40 border-white/60 text-gray-800"
          }`}
        >
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              لیست افراد ({people.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-400"></div>
              </div>
            ) : people.length === 0 ? (
              <div className="text-center py-8 text-gray-500">هیچ فردی اضافه نشده است</div>
            ) : (
              <div className="space-y-3">
                {people.map((person) => (
                  <div
                    key={person.id}
                    className={`p-4 rounded-xl border transition-all ${
                      selectedPeople.includes(person.id)
                        ? isDarkMode
                          ? "bg-emerald-500/20 border-emerald-400/50"
                          : "bg-emerald-100/50 border-emerald-300/50"
                        : isDarkMode
                          ? "bg-white/5 border-white/10 hover:bg-white/10"
                          : "bg-white/30 border-white/30 hover:bg-white/50"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <Checkbox
                          checked={selectedPeople.includes(person.id)}
                          onCheckedChange={() => togglePersonSelection(person.id)}
                        />
                        <div className="space-y-1">
                          <h3 className="font-semibold text-lg">{person.name}</h3>
                          <div className="flex items-center gap-4 text-sm opacity-75">
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {person.birthdate}
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              {person.birthtime}
                            </div>
                            <div className="flex items-center gap-1">
                              <MapPin className="w-4 h-4" />
                              {person.city}
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => copyPersonJson(person)}
                          className="rounded-full"
                        >
                          <Copy className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => openModal(person)} className="rounded-full">
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => deletePerson(person.id)}
                          className="rounded-full text-red-400 hover:text-red-300"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Chart Generation */}
        <Card
          className={`backdrop-blur-md border ${
            isDarkMode ? "bg-white/10 border-white/20 text-white" : "bg-white/40 border-white/60 text-gray-800"
          }`}
        >
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5" />
              تولید چارت
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <Button
                onClick={() => generateChart("natal")}
                disabled={selectedPeople.length !== 1 || isLoading}
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-xl h-12"
              >
                <Star className="w-4 h-4 mr-2" />
                چارت تولد
              </Button>
              <Button
                onClick={() => generateChart("transit")}
                disabled={selectedPeople.length !== 1 || isLoading}
                className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white rounded-xl h-12"
              >
                <Zap className="w-4 h-4 mr-2" />
                چارت ترانزیت
              </Button>
              <Button
                onClick={() => generateChart("synastry")}
                disabled={selectedPeople.length !== 2 || isLoading}
                className="bg-gradient-to-r from-rose-500 to-orange-500 hover:from-rose-600 hover:to-orange-600 text-white rounded-xl h-12"
              >
                <Heart className="w-4 h-4 mr-2" />
                چارت رابطه
              </Button>
              <Button
                onClick={() => generateChart("composite")}
                disabled={selectedPeople.length !== 2 || isLoading}
                className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white rounded-xl h-12"
              >
                <Users className="w-4 h-4 mr-2" />
                چارت ترکیبی
              </Button>
              <Button
                onClick={() => generateChart("report")}
                disabled={selectedPeople.length !== 1 || isLoading}
                className="bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white rounded-xl h-12"
              >
                <FileText className="w-4 h-4 mr-2" />
                گزارش کامل
              </Button>
            </div>

            {selectedPeople.length > 0 && (
              <div className="mt-4 p-3 rounded-lg bg-emerald-500/20 border border-emerald-400/30">
                <p className="text-sm">
                  {selectedPeople.length} فرد انتخاب شده:{" "}
                  {people
                    .filter((p) => selectedPeople.includes(p.id))
                    .map((p) => p.name)
                    .join("، ")}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={closeModal}
          className={`backdrop-blur-md border ${
            isDarkMode ? "bg-slate-900/90 border-white/20 text-white" : "bg-white/90 border-white/60 text-gray-800"
          }`}
        >
          <ModalHeader>
            <ModalTitle>{editingPerson ? "ویرایش اطلاعات" : "افزودن فرد جدید"}</ModalTitle>
          </ModalHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">نام</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                  required
                  className={`${isDarkMode ? "bg-white/10 border-white/20 text-white" : "bg-white/50 border-white/50"}`}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="city">شهر تولد</Label>
                <Input
                  id="city"
                  value={formData.city}
                  onChange={(e) => {
                    setFormData((prev) => ({ ...prev, city: e.target.value }))
                    searchCity(e.target.value)
                  }}
                  required
                  className={`${isDarkMode ? "bg-white/10 border-white/20 text-white" : "bg-white/50 border-white/50"}`}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="birthdate">تاریخ تولد</Label>
                <Input
                  id="birthdate"
                  type="date"
                  value={formData.birthdate}
                  onChange={(e) => setFormData((prev) => ({ ...prev, birthdate: e.target.value }))}
                  required
                  className={`${isDarkMode ? "bg-white/10 border-white/20 text-white" : "bg-white/50 border-white/50"}`}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="birthtime">ساعت تولد</Label>
                <Input
                  id="birthtime"
                  type="time"
                  value={formData.birthtime}
                  onChange={(e) => setFormData((prev) => ({ ...prev, birthtime: e.target.value }))}
                  required
                  className={`${isDarkMode ? "bg-white/10 border-white/20 text-white" : "bg-white/50 border-white/50"}`}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>محل تولد (روی نقشه کلیک کنید)</Label>
              <div ref={mapRef} className="h-64 rounded-lg border border-white/20" style={{ minHeight: "250px" }} />
              <p className="text-sm opacity-75">
                مختصات: {formData.lat.toFixed(6)}, {formData.lng.toFixed(6)}
              </p>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button type="button" variant="ghost" onClick={closeModal} disabled={isLoading}>
                انصراف
              </Button>
              <Button
                type="submit"
                disabled={isLoading || !formData.lat || !formData.lng}
                className="bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600 text-white"
              >
                {isLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : null}
                {editingPerson ? "به‌روزرسانی" : "افزودن"}
              </Button>
            </div>
          </form>
        </Modal>

        <Modal
          isOpen={chartModalOpen}
          onClose={() => setChartModalOpen(false)}
          className={`backdrop-blur-md border max-w-4xl overflow-auto ${
            isDarkMode ? "bg-slate-900/90 border-white/20 text-white" : "bg-white/90 border-white/60 text-gray-800"
          }`}
        >
          <ModalHeader>
            <ModalTitle>نمایش چارت</ModalTitle>
          </ModalHeader>
          <div className="p-4 space-y-4">
            {chartType === "json" && (
              <>
                <pre className="whitespace-pre-wrap break-words rounded-md p-4 bg-black/20 border border-white/10 max-h-[400px] overflow-auto">
                  {chartContent}
                </pre>
                <Button
                  onClick={() => {
                    navigator.clipboard.writeText(chartContent)
                    toast({ title: "کپی شد", description: "متن JSON در کلیپ‌بورد کپی شد" })
                  }}
                  className="bg-gradient-to-r from-emerald-500 to-blue-500 text-white"
                >
                  کپی JSON
                </Button>
              </>
            )}
            {chartType === "svg" && (
              <>
                <div
                  className="bg-white p-4 rounded-md border max-h-[500px] overflow-auto"
                  dangerouslySetInnerHTML={{ __html: chartContent }}
                />
                <a
                  href={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(chartContent)}`}
                  download="chart.svg"
                  className="inline-block mt-2"
                >
                  <Button className="bg-gradient-to-r from-emerald-500 to-blue-500 text-white">
                    دانلود SVG
                  </Button>
                </a>
              </>
            )}
          </div>
        </Modal>

      </div>
    </div>
    
  )
}
