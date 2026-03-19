import { useState, useEffect } from 'react'
import axios from 'axios'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// ==========================================================
// 1. YARDIMCI BİLEŞENLER
// ==========================================================

const StatsCards = ({ stats, setShowBirthdayModal }) => {
  if (!stats) return <div className="text-center my-3">Veriler Yükleniyor...</div>
  return (
    <div className="row mb-4">
      <div className="col-md-4"><div className="card text-white bg-primary shadow h-100"><div className="card-body text-center p-2"><h6 className="card-title">Toplam Personel</h6><h2 className="fw-bold m-0">{stats.total}</h2></div></div></div>
      <div className="col-md-4"><div className="card text-white bg-success shadow h-100"><div className="card-body text-center p-2"><h6 className="card-title">Cinsiyet</h6><div><span className="fs-5 fw-bold">👨 {stats.genders['Erkek'] || 0}</span><span className="mx-2">|</span><span className="fs-5 fw-bold">👩 {stats.genders['Kadın'] || 0}</span></div></div></div></div>
      <div className="col-md-4"><div className="card text-white bg-danger shadow h-100" style={{cursor: 'pointer'}} onClick={() => setShowBirthdayModal(true)}><div className="card-body text-center p-2"><h6 className="card-title">🎂 Doğum Günleri</h6><h2 className="fw-bold m-0">{stats.upcoming_birthdays.length} <small className="fs-6 fw-normal">Yaklaşan</small></h2></div></div></div>
    </div>
  )
}

const LeaveBalanceCards = ({ user }) => {
    return (
        <div className="row mb-4">
            <div className="col-md-4"><div className="card border-primary shadow h-100"><div className="card-header bg-primary text-white text-center fw-bold">🏖️ Yıllık İzin</div><div className="card-body text-center"><h3 className="text-primary fw-bold">{user?.annual_leave_entitlement || 0} <small className="fs-6 text-muted">Gün</small></h3></div></div></div>
            <div className="col-md-4"><div className="card border-warning shadow h-100"><div className="card-header bg-warning text-dark text-center fw-bold">🤧 Mazeret İzni</div><div className="card-body text-center"><h3 className="text-warning fw-bold">{user?.excuse_leave_entitlement || 0} <small className="fs-6 text-muted">Gün</small></h3></div></div></div>
            <div className="col-md-4"><div className="card border-danger shadow h-100"><div className="card-header bg-danger text-white text-center fw-bold">🏥 Rapor Hakkı</div><div className="card-body text-center"><h3 className="text-danger fw-bold">{user?.sick_leave_entitlement || 0} <small className="fs-6 text-muted">Gün</small></h3></div></div></div>
        </div>
    )
}

const LeaveCalendarList = ({ activeLeaves }) => {
  return (
    <div className="card bg-warning text-dark shadow border-0 mb-3 animate-fade-in">
      <div className="card-body">
        <h5 className="border-bottom border-dark pb-2">📅 İzin Takvimi</h5>
        {activeLeaves.length === 0 ? (<p className="text-center fw-bold mt-3">Herkes ofiste! 👍</p>) : (<div className="accordion accordion-flush" id="accordionLeaves">{activeLeaves.map((l, i) => (<div className="accordion-item bg-transparent border-bottom border-dark" key={i}><h2 className="accordion-header"><button className="accordion-button collapsed bg-transparent text-dark p-2 shadow-none" type="button" data-bs-toggle="collapse" data-bs-target={`#leave${i}`}><div className="d-flex w-100 justify-content-between align-items-center me-2"><span className="fw-bold">{l.name}</span>{l.is_active ? <span className="badge bg-success">ŞU AN</span> : <span className="badge bg-primary">PLANLI</span>}</div></button></h2><div id={`leave${i}`} className="accordion-collapse collapse" data-bs-parent="#accordionLeaves"><div className="accordion-body p-2 bg-light bg-opacity-75 rounded mb-2"><div>💼 <strong>{l.role}</strong> - {l.type_name}</div><div className="d-flex justify-content-between mt-1"><span>Gidiş: <strong>{l.start_date}</strong></span><span>Dönüş: <strong>{l.end_date}</strong></span></div></div></div></div>))}</div>)}
      </div>
    </div>
  )
}

// ==========================================================
// 2. MODÜLLER
// ==========================================================

const AnnouncementsModule = ({ token, user }) => {
    const [announcements, setAnnouncements] = useState([])
    const [teams, setTeams] = useState([])
    const [newAnn, setNewAnn] = useState({ title: "", content: "", is_public: false, target_team_id: "" })

    useEffect(() => { fetchData() }, [token])

    const fetchData = async () => {
        // 1. DUYURULARI ÇEK (Hata olursa sadece duyuru gelmez)
        try {
            const annRes = await axios.get("http://127.0.0.1:8000/announcements/", { headers: { Authorization: `Bearer ${token}` } })
            setAnnouncements(annRes.data)
        } catch (error) { 
            console.error("Duyurular yüklenemedi:", error) 
        }

        // 2. TAKIMLARI ÇEK 
        try {
            const teamRes = await axios.get("http://127.0.0.1:8000/teams/", { headers: { Authorization: `Bearer ${token}` } })
            setTeams(teamRes.data)
        } catch (error) {
            console.error("Takımlar yüklenemedi:", error)
        }
    }

    const handlePost = async (e) => {
        e.preventDefault()
        const payload = { ...newAnn }
        if (payload.target_team_id === "") payload.target_team_id = null;
        else payload.target_team_id = parseInt(payload.target_team_id);

        try {
            await axios.post("http://127.0.0.1:8000/announcements/", payload, { headers: { Authorization: `Bearer ${token}` } })
            alert("📢 Duyuru Yayınlandı!")
            setNewAnn({ title: "", content: "", is_public: false, target_team_id: "" })
            fetchData()
        } catch (err) { 
            console.error(err);
            alert(err.response?.data?.detail || "Yetkiniz yok veya hata oluştu.") 
        }
    }

    const handleDelete = async (id) => {
        if(!confirm("Silmek istediğine emin misin?")) return;
        try { await axios.delete(`http://127.0.0.1:8000/announcements/${id}`, { headers: { Authorization: `Bearer ${token}` } }); fetchData() } 
        catch (err) { alert("Silemezsiniz.") }
    }

    const userRole = user?.role || "";
    // DİKKAT: Backend'den employee_id geliyor, number olduğundan emin olalım
    const currentEmpId = user?.employee_id ? parseInt(user.employee_id) : 0;

    // YETKİ KONTROLÜ: Admin, İK veya HERHANGİ BİR TAKIMIN LİDERİ Mİ?
    const isLeader = teams.some(t => t.leader_id === currentEmpId);
    const canPost = ["admin", "hr", "İnsan Kaynakları"].includes(userRole) || isLeader;
    
    // Hangi takımlara duyuru atabilir? (Admin hepsi, Lider sadece kendi takımı)
    const visibleTeams = ["admin", "hr", "İnsan Kaynakları"].includes(userRole) 
        ? teams 
        : teams.filter(t => t.leader_id === currentEmpId)

    return (
        <div className="row animate-fade-in">
            {canPost && (
            <div className="col-md-4 mb-3">
                <div className="card shadow border-0">
                    <div className="card-header bg-info text-white fw-bold">✍️ Duyuru Paneli {isLeader && "(Lider Yetkisi)"}</div>
                    <div className="card-body">
                        <form onSubmit={handlePost}>
                            <input className="form-control mb-2" placeholder="Başlık" required value={newAnn.title} onChange={e=>setNewAnn({...newAnn, title: e.target.value})} />
                            <textarea className="form-control mb-2" rows="3" placeholder="Mesajınız..." required value={newAnn.content} onChange={e=>setNewAnn({...newAnn, content: e.target.value})}></textarea>
                            <div className="mb-2">
                                <label className="small fw-bold">Hedef Kitle:</label>
                                <select className="form-select mb-2" required value={newAnn.is_public ? "public" : (newAnn.target_team_id || "")} 
                                    onChange={e => { 
                                        if(e.target.value === "public") setNewAnn({...newAnn, is_public: true, target_team_id: ""}); 
                                        else setNewAnn({...newAnn, is_public: false, target_team_id: e.target.value}) 
                                    }}>
                                    <option value="" disabled>Seçiniz...</option>
                                    {/* Sadece Admin/İK herkese açık atabilir */}
                                    {["admin", "hr", "İnsan Kaynakları"].includes(userRole) && <option value="public">🌍 Herkese Açık</option>}
                                    
                                    {/* Lider sadece kendi takımını görür */}
                                    {visibleTeams.map(t => <option key={t.id} value={t.id}>👥 {t.name} Ekibi</option>)}
                                </select>
                            </div>
                            <button className="btn btn-info text-white fw-bold w-100">YAYINLA</button>
                        </form>
                    </div>
                </div>
            </div>
            )}
            
            {/* Duyuru Listesi - KODUN GERİSİ AYNI */}
            <div className={canPost ? "col-md-8" : "col-md-12"}>
                {announcements.map(a => (
                    <div className="card shadow-sm mb-3 border-start border-5 border-info" key={a.id}>
                        <div className="card-body">
                            <div className="d-flex justify-content-between"><h5 className="card-title text-primary">{a.title}</h5><small className="text-muted">{new Date(a.created_at).toLocaleDateString()}</small></div>
                            <p className="card-text">{a.content}</p>
                            <div className="d-flex justify-content-between align-items-center">
                                <span className="badge bg-secondary">{a.is_public ? "🌍 Herkese Açık" : `👥 ${a.target_team_name || 'Ekip'} Özel`}</span>
                                <div><small className="me-2 text-muted">Yazan: {a.author_name}</small>
                                {["admin", "hr"].includes(userRole) && <button className="btn btn-sm btn-danger" onClick={()=>handleDelete(a.id)}>Sil</button>}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
                {announcements.length === 0 && <p className="text-center text-muted">Henüz duyuru yok.</p>}
            </div>
        </div>
    )
}

const TeamManagement = ({ token }) => {
    const [teams, setTeams] = useState([])
    const [employees, setEmployees] = useState([])
    const [newTeam, setNewTeam] = useState({ name: "", leader_id: "" })

    useEffect(() => { fetchTeams(); fetchEmployees(); }, [token])

    const fetchTeams = async () => { const res = await axios.get("http://127.0.0.1:8000/teams/", { headers: { Authorization: `Bearer ${token}` } }); setTeams(res.data) }
    const fetchEmployees = async () => { const res = await axios.get("http://127.0.0.1:8000/employees/", { headers: { Authorization: `Bearer ${token}` } }); setEmployees(res.data) }

    const createTeam = async () => {
        try { 
            const payload = { name: newTeam.name, leader_id: newTeam.leader_id ? parseInt(newTeam.leader_id) : null }
            await axios.post("http://127.0.0.1:8000/teams/", payload, { headers: { Authorization: `Bearer ${token}` } }); 
            alert("Takım Kuruldu!"); setNewTeam({ name: "", leader_id: "" }); fetchTeams() 
        } catch (e) { alert("Hata oluştu.") }
    }

    const updateLeader = async (teamId, leaderId) => {
        try { await axios.put(`http://127.0.0.1:8000/teams/${teamId}/leader`, { leader_id: parseInt(leaderId) }, { headers: { Authorization: `Bearer ${token}` } }); alert("Lider Güncellendi!"); fetchTeams(); } catch (e) { alert("Güncellenemedi.") }
    }

    return (
        <div className="card shadow border-0 mb-3 animate-fade-in">
            <div className="card-header bg-dark text-white">👥 Ekip / Takım Yönetimi</div>
            <div className="card-body">
                <div className="row mb-4 p-3 bg-light rounded border mx-1">
                    <h6 className="fw-bold text-primary">➕ Yeni Takım Kur</h6>
                    <div className="col-md-5"><input className="form-control" placeholder="Ekip Adı" value={newTeam.name} onChange={e=>setNewTeam({...newTeam, name: e.target.value})} /></div>
                    <div className="col-md-5"><select className="form-select" value={newTeam.leader_id} onChange={e=>setNewTeam({...newTeam, leader_id: e.target.value})}><option value="">Lider Seçiniz...</option>{employees.map(emp => (<option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name}</option>))}</select></div>
                    <div className="col-md-2"><button className="btn btn-dark w-100" onClick={createTeam}>Kur</button></div>
                </div>

                <h6 className="fw-bold border-bottom pb-2">📋 Mevcut Takımlar ve Üyeleri</h6>
                <div className="table-responsive">
                <table className="table table-hover align-middle">
                    <thead className="table-secondary"><tr><th>Ekip Adı</th><th>Lider</th><th>Üyeler (İsimler)</th><th>Sayı</th></tr></thead>
                    <tbody>
                        {teams.map(t => (
                            <tr key={t.id}>
                                <td className="fw-bold">{t.name}</td>
                                <td>
                                    <select className="form-select form-select-sm" style={{maxWidth: '160px'}} onChange={(e) => updateLeader(t.id, e.target.value)} value={t.leader_id || ""}>
                                        <option value="" disabled>{t.leader_name || "Lider Ata"}</option>
                                        {employees.map(emp => (<option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name}</option>))}
                                    </select>
                                </td>
                                <td>
                                    {t.members && t.members.length > 0 ? (
                                        <small className="text-muted">{t.members.join(", ")}</small>
                                    ) : <span className="text-muted small">Henüz üye yok</span>}
                                </td>
                                <td><span className="badge bg-secondary">{t.member_count}</span></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                </div>
            </div>
        </div>
    )
}

const NewEmployeeForm = ({ token, onSuccess }) => { 
    const [newEmp, setNewEmp] = useState({ first_name: "", last_name: "", email: "", password: "", department_id: 1, employment_type_id: 1, gender: "Erkek", birth_date: "", role: "İşçi" }); 
    
    const handleSubmit = async (e) => { 
        e.preventDefault(); 
        try { 
            await axios.post("http://127.0.0.1:8000/employees/", newEmp, { headers: { Authorization: `Bearer ${token}` } }); 
            alert("✅ Personel Başarıyla Eklendi!"); 
            setNewEmp({ ...newEmp, first_name: "", last_name: "", email: "", password: "" }); 
            if(onSuccess) onSuccess() 
        } catch (error) { 
            // 👇 GÜNCELLEME BURADA: Gerçek hatayı ekrana basıyoruz
            console.error(error);
            if (error.response && error.response.data && error.response.data.detail) {
                alert(`❌ Hata: ${error.response.data.detail}`); // Örn: "Bu email zaten kayıtlı"
            } else {
                alert("❌ Bir hata oluştu! Lütfen tüm alanları kontrol edin."); 
            }
        } 
    }; 
    
    return (<div className="card shadow border-0 mb-3 animate-fade-in"><div className="card-header bg-primary text-white"><h5>➕ Yeni Personel İşe Alım Formu</h5></div><div className="card-body bg-light"><form onSubmit={handleSubmit}><div className="row"><div className="col"><input className="form-control mb-2" placeholder="Ad" required value={newEmp.first_name} onChange={e => setNewEmp({...newEmp, first_name: e.target.value})} /></div><div className="col"><input className="form-control mb-2" placeholder="Soyad" required value={newEmp.last_name} onChange={e => setNewEmp({...newEmp, last_name: e.target.value})} /></div></div><div className="mb-2"><label className="small fw-bold">Rol (Maaşı Belirler)</label><select className="form-select" value={newEmp.role} onChange={e => setNewEmp({...newEmp, role: e.target.value})}><option value="İşçi">İşçi</option><option value="Memur">Memur</option><option value="Satış Müdürü">Satış Müdürü</option><option value="İnsan Kaynakları">İnsan Kaynakları</option><option value="Yazılımcı">Yazılımcı</option></select></div><div className="row mb-2"><div className="col"><input type="date" className="form-control" required value={newEmp.birth_date} onChange={e => setNewEmp({...newEmp, birth_date: e.target.value})} /></div><div className="col"><select className="form-select" value={newEmp.gender} onChange={e => setNewEmp({...newEmp, gender: e.target.value})}><option value="Erkek">Erkek</option><option value="Kadın">Kadın</option></select></div></div><hr/><input className="form-control mb-2" type="email" placeholder="Email" required value={newEmp.email} onChange={e => setNewEmp({...newEmp, email: e.target.value})} /><input className="form-control mb-3" type="password" placeholder="Şifre" required value={newEmp.password} onChange={e => setNewEmp({...newEmp, password: e.target.value})} /><button type="submit" className="btn btn-success w-100 fw-bold">KAYDET</button></form></div></div>) 
}

const EditEmployeeModal = ({ employee, token, onClose, onUpdate }) => { 
    const [data, setData] = useState({ ...employee }); 
    const [teams, setTeams] = useState([]); 
    useEffect(()=>{axios.get("http://127.0.0.1:8000/teams/", {headers:{Authorization:`Bearer ${token}`}}).then(res=>setTeams(res.data))},[]); 
    const handleSave = async () => { try { await axios.put(`http://127.0.0.1:8000/employees/${employee.id}`, data, { headers: { Authorization: `Bearer ${token}` } }); if(data.team_id) await axios.put(`http://127.0.0.1:8000/teams/assign/${employee.id}?team_id=${data.team_id}`, {}, { headers: { Authorization: `Bearer ${token}` } }); alert("Bilgiler Güncellendi!"); onUpdate(); onClose() } catch (e) { alert("Hata oluştu") } }; 
    return (<div className="modal show d-block" style={{background: 'rgba(0,0,0,0.5)'}}><div className="modal-dialog"><div className="modal-content"><div className="modal-header bg-warning"><h5 className="modal-title">✏️ Personel Düzenle</h5><button className="btn-close" onClick={onClose}></button></div><div className="modal-body"><label>Ad</label><input className="form-control mb-2" value={data.first_name} onChange={e => setData({...data, first_name: e.target.value})} /><label>Soyad</label><input className="form-control mb-2" value={data.last_name} onChange={e => setData({...data, last_name: e.target.value})} /><label>Takım Ata</label><select className="form-select mb-2" value={data.team_id || ""} onChange={e=>setData({...data, team_id: e.target.value})}><option value="">Takımsız</option>{teams.map(t=><option key={t.id} value={t.id}>{t.name}</option>)}</select></div><div className="modal-footer"><button className="btn btn-secondary" onClick={onClose}>İptal</button><button className="btn btn-primary" onClick={handleSave}>Kaydet</button></div></div></div></div>) 
}

// ==========================================================
// 3. ANA PANELLER
// ==========================================================

const AdminPanel = ({ token, onLogout, user }) => {
  const [stats, setStats] = useState(null); const [employees, setEmployees] = useState([]); const [activeTab, setActiveTab] = useState(null); const [showBirthdayModal, setShowBirthdayModal] = useState(false); const [editingEmp, setEditingEmp] = useState(null)
  useEffect(() => { axios.get("http://127.0.0.1:8000/dashboard/stats", { headers: { Authorization: `Bearer ${token}` } }).then(res => setStats(res.data)); fetchEmployees() }, [token])
  const fetchEmployees = async () => { try { const response = await axios.get("http://127.0.0.1:8000/employees/", { headers: { Authorization: `Bearer ${token}` } }); setEmployees(response.data) } catch (error) { } }
  const handleUpdateSalary = async (id, currentSalary, name) => { const newSalary = parseInt(prompt(`"${name}" için yeni maaş:`, currentSalary)); if (newSalary) { await axios.put(`http://127.0.0.1:8000/employees/${id}/salary`, { amount: newSalary }, { headers: { Authorization: `Bearer ${token}` } }); fetchEmployees(); } }
  const handleFire = async (id) => { if(confirm("SİLMEK istiyor musunuz?")) { await axios.delete(`http://127.0.0.1:8000/employees/${id}`, { headers: { Authorization: `Bearer ${token}` } }); fetchEmployees(); } }

  return (
    <div className="container mt-4">
      {/* BAŞLIK VE PROFİL BİLGİSİ (ÇÖKMEZ MOD: Soru işaretleri eklendi) */}
      <div className="d-flex justify-content-between align-items-center mb-4 p-3 bg-dark text-white rounded shadow">
        <h3>🚀 Yönetim Paneli</h3>
        <div className="d-flex align-items-center">
            <div className="me-3 text-end">
                {/* user? kullanarak veri yoksa hata verme, boş geç dedik */}
                <div className="fw-bold">{user?.first_name} {user?.last_name}</div>
                <span className="badge bg-warning text-dark">{user?.job_title || "Yönetici"}</span>
            </div>
            <button className="btn btn-danger" onClick={onLogout}>Çıkış</button>
        </div>
      </div>
      
      <StatsCards stats={stats} setShowBirthdayModal={setShowBirthdayModal} />
      
      <div className="row g-3 mb-4">
        <div className="col-md-4"><button className={`btn w-100 py-3 fw-bold shadow ${activeTab==='announcements'?'btn-primary':'btn-secondary'}`} onClick={()=>setActiveTab(activeTab==='announcements'?null:'announcements')}>📢 DUYURULAR</button></div>
        <div className="col-md-4"><button className={`btn w-100 py-3 fw-bold shadow ${activeTab==='teams'?'btn-primary':'btn-secondary'}`} onClick={()=>setActiveTab(activeTab==='teams'?null:'teams')}>👥 TAKIMLAR</button></div>
        <div className="col-md-4"><button className={`btn w-100 py-3 fw-bold shadow ${activeTab==='calendar'?'btn-primary':'btn-secondary'}`} onClick={()=>setActiveTab(activeTab==='calendar'?null:'calendar')}>📅 İZİNLER</button></div>
        <div className="col-md-6"><button className={`btn w-100 py-3 fw-bold shadow ${activeTab==='list'?'btn-primary':'btn-secondary'}`} onClick={()=>setActiveTab(activeTab==='list'?null:'list')}>📋 PERSONEL LİSTESİ</button></div>
        <div className="col-md-6"><button className={`btn w-100 py-3 fw-bold shadow ${activeTab==='hiring'?'btn-success':'btn-secondary'}`} onClick={()=>setActiveTab(activeTab==='hiring'?null:'hiring')}>➕ YENİ PERSONEL EKLE</button></div>
      </div>

      {activeTab === 'announcements' && <AnnouncementsModule token={token} user={user} />}
      {activeTab === 'teams' && <TeamManagement token={token} />}
      {activeTab === 'calendar' && stats && <LeaveCalendarList activeLeaves={stats.active_leaves} />}
      {activeTab === 'list' && (<div className="card shadow-sm border-0 mb-3 animate-fade-in"><div className="card-header bg-secondary text-white"><h5>📋 Personel Listesi</h5></div><div className="card-body p-0"><table className="table table-hover mb-0 align-middle"><thead className="table-dark"><tr><th>Ad Soyad</th><th>Rol</th><th>Maaş</th><th>İşlem</th></tr></thead><tbody>{employees.map((emp) => (<tr key={emp.id}><td className="fw-bold">{emp.first_name} {emp.last_name}</td><td><span className="badge bg-primary">{emp.role}</span></td><td className="text-success fw-bold">{emp.salary.toLocaleString()} ₺</td><td><div className="btn-group"><button className="btn btn-warning btn-sm" onClick={() => handleUpdateSalary(emp.id, emp.salary, emp.first_name)}>💰</button><button className="btn btn-info btn-sm" onClick={() => setEditingEmp(emp)}>✏️</button><button className="btn btn-danger btn-sm" onClick={() => handleFire(emp.id)}>🗑️</button></div></td></tr>))}</tbody></table></div></div>)}
      {activeTab === 'hiring' && <NewEmployeeForm token={token} onSuccess={fetchEmployees} />}
      {editingEmp && <EditEmployeeModal employee={editingEmp} token={token} onClose={() => setEditingEmp(null)} onUpdate={fetchEmployees} />}
      {showBirthdayModal && stats && (<div className="modal show d-block" style={{background: 'rgba(0,0,0,0.5)'}}><div className="modal-dialog"><div className="modal-content"><div className="modal-header bg-danger text-white"><h5>🎂 Doğum Günleri</h5><button className="btn-close" onClick={()=>setShowBirthdayModal(false)}></button></div><div className="modal-body"><ul className="list-group">{stats.upcoming_birthdays.map((u, i) => <li key={i} className="list-group-item">{u.name} - {u.days_left} gün kaldı</li>)}</ul></div></div></div></div>)}
    </div>
  )
}

// HRPanel bileşenini bul ve bununla değiştir:

const HRPanel = ({ token, user, onLogout }) => {
    const [stats, setStats] = useState(null); 
    const [requests, setRequests] = useState([]); 
    const [activeTab, setActiveTab] = useState(null); 
    const [showBirthdayModal, setShowBirthdayModal] = useState(false)

    useEffect(() => { 
        axios.get("http://127.0.0.1:8000/dashboard/stats", { headers: { Authorization: `Bearer ${token}` } }).then(res => setStats(res.data)) 
        fetchRequests(); 
    }, [token])

    const fetchRequests = () => { axios.get("http://127.0.0.1:8000/leaves/all", { headers: { Authorization: `Bearer ${token}` } }).then(res => setRequests(res.data)).catch(err => {}) }
    const updateStatus = async (id, status) => { try { await axios.put(`http://127.0.0.1:8000/leaves/${id}/status`, { status }, { headers: { Authorization: `Bearer ${token}` } }); alert(`İşlem: ${status}`); setRequests(requests.map(req => req.id === id ? { ...req, status: status } : req)) } catch (err) { alert("Hata!") } }
    const deleteLeave = async (id) => { if(!confirm("Bu kaydı silmek istediğinize emin misiniz?")) return; try { await axios.delete(`http://127.0.0.1:8000/leaves/${id}`, { headers: { Authorization: `Bearer ${token}` } }); setRequests(requests.filter(req => req.id !== id)) } catch(err) { alert("Silinemedi!") } }

    return (
        <div className="container mt-4">
            <div className="d-flex justify-content-between align-items-center mb-4 p-3 bg-warning text-dark rounded shadow">
                <h3>👔 İK Yönetim Paneli</h3>
                <div className="d-flex align-items-center">
                    <div className="me-3 text-end">
                        <div className="fw-bold">{user?.first_name} {user?.last_name}</div>
                        <span className="badge bg-dark text-white">{user?.job_title || "İK Uzmanı"}</span>
                    </div>
                    <button className="btn btn-danger" onClick={onLogout}>Çıkış</button>
                </div>
            </div>
            
            <StatsCards stats={stats} setShowBirthdayModal={setShowBirthdayModal} />
            
            {/* 👇 BUTONLAR ARTIK GRİ (btn-secondary) GÖRÜNECEK */}
            <div className="row g-3 mb-4">
                <div className="col-md"><button className={`btn w-100 py-3 fw-bold shadow ${activeTab==='approvals'?'btn-dark':'btn-secondary'}`} onClick={()=>setActiveTab(activeTab==='approvals'?null:'approvals')}>⏳ İZİN ONAYLARI</button></div>
                <div className="col-md"><button className={`btn w-100 py-3 fw-bold shadow ${activeTab==='calendar'?'btn-dark':'btn-secondary'}`} onClick={()=>setActiveTab(activeTab==='calendar'?null:'calendar')}>📅 İZİNDEKİLER</button></div>
                <div className="col-md"><button className={`btn w-100 py-3 fw-bold shadow ${activeTab==='announcements'?'btn-dark':'btn-secondary'}`} onClick={()=>setActiveTab(activeTab==='announcements'?null:'announcements')}>📢 DUYURULAR</button></div>
                <div className="col-md"><button className={`btn w-100 py-3 fw-bold shadow ${activeTab==='teams'?'btn-dark':'btn-secondary'}`} onClick={()=>setActiveTab(activeTab==='teams'?null:'teams')}>👥 TAKIMLAR</button></div>
                <div className="col-md"><button className={`btn w-100 py-3 fw-bold shadow ${activeTab==='hiring'?'btn-dark':'btn-secondary'}`} onClick={()=>setActiveTab(activeTab==='hiring'?null:'hiring')}>➕ İŞE ALIM</button></div>
            </div>

            {activeTab === 'announcements' && <AnnouncementsModule token={token} user={user} />}
            {activeTab === 'teams' && <TeamManagement token={token} />}
            {activeTab === 'hiring' && <NewEmployeeForm token={token} />}
            {activeTab === 'calendar' && stats && <LeaveCalendarList activeLeaves={stats.active_leaves} />}

            {activeTab === 'approvals' && (
                <div className="card shadow border-0 mb-3 animate-fade-in">
                    <div className="card-header bg-dark text-white">⏳ İzin Talep Yönetimi</div>
                    <div className="card-body p-0">
                    <table className="table table-hover mb-0 align-middle">
                        <thead className="table-light"><tr><th>Personel</th><th>Tarihler</th><th>Sebep</th><th>Durum</th><th>İşlem</th></tr></thead>
                        <tbody>
                            {requests.length === 0 ? <tr><td colSpan="5" className="text-center p-3">Bekleyen talep yok.</td></tr> : null}
                            {requests.map(r => (
                            <tr key={r.id}>
                                <td className="fw-bold">{r.employee_name}</td>
                               <td>
    {/* Başlangıç Tarihi: SARI KUTU (bg-warning) */}
    <span className="badge bg-warning text-dark border border-dark text-wrap py-2 px-3 shadow-sm">
        <i className="bi bi-calendar-event me-1"></i>
        {r.start_date.split('-').reverse().join('.')}
    </span>

    {/* Araya Ok İşareti */}
    <span className="mx-2 text-muted fw-bold">➜</span>

    {/* Bitiş Tarihi: SARI KUTU (bg-warning) */}
    <span className="badge bg-warning text-dark border border-dark text-wrap py-2 px-3 shadow-sm">
        <i className="bi bi-calendar-check me-1"></i>
        {r.end_date.split('-').reverse().join('.')}
    </span>
</td>
                                <td>{r.reason}</td>
                                <td>{r.status === "Onaylandı" ? <span className="badge bg-success">Onaylandı</span> : r.status === "Reddedildi" ? <span className="badge bg-danger">Reddedildi</span> : <span className="badge bg-warning text-dark">Beklemede</span>}</td>
                                <td>{r.status === "Beklemede" ? (<><button className="btn btn-success btn-sm me-1" onClick={() => updateStatus(r.id, "Onaylandı")}>✅</button><button className="btn btn-danger btn-sm" onClick={() => updateStatus(r.id, "Reddedildi")}>❌</button></>) : (<button className="btn btn-outline-danger btn-sm" onClick={() => deleteLeave(r.id)}>🗑️ Sil</button>)}</td>
                            </tr>
                            ))}
                        </tbody>
                    </table>
                    </div>
                </div>
            )}
        </div>
    )
}

const EmployeePanel = ({ token, user, onLogout }) => {
    const [activeTab, setActiveTab] = useState(null); 
    const [leaves, setLeaves] = useState([]); const [newLeave, setNewLeave] = useState({ leave_type_id: 1, start_date: "", end_date: "", reason: "" }); 
    const fetchMyLeaves = async () => { try { const res = await axios.get("http://127.0.0.1:8000/leaves/my", { headers: { Authorization: `Bearer ${token}` } }); setLeaves(res.data) } catch (err) { } }
    useEffect(() => { fetchMyLeaves() }, [token])
    const handleRequest = async (e) => { e.preventDefault(); try { await axios.post("http://127.0.0.1:8000/leaves/", newLeave, { headers: { Authorization: `Bearer ${token}` } }); alert("✅ İzin talebiniz gönderildi!"); fetchMyLeaves(); setNewLeave({...newLeave, start_date: "", end_date: "", reason: ""}) } catch (err) { alert("❌ Hata.") } }
    
    return (
        <div className="container mt-4">
            <div className="d-flex justify-content-between align-items-center mb-4 p-3 bg-primary text-white rounded shadow">
                <h3>👋 Merhaba, {user?.first_name}</h3>
                <div className="d-flex align-items-center">
                    <span className="badge bg-light text-primary me-3 fs-6">{user?.job_title}</span>
                    <button className="btn btn-danger btn-sm" onClick={onLogout}>Çıkış</button>
                </div>
            </div>
            
            {!activeTab && <LeaveBalanceCards user={user} />}

            <button className={`btn w-100 py-3 mb-3 fw-bold shadow ${activeTab==='announcements'?'btn-info':'btn-outline-info'}`} onClick={()=>setActiveTab(activeTab==='announcements'?null:'announcements')}>📢 DUYURULAR PANOSU</button>
            
            {activeTab === 'announcements' && <AnnouncementsModule token={token} user={user} />}
            
            {!activeTab && (
                <div className="row">
                    <div className="col-md-4"><div className="card shadow border-0"><div className="card-header bg-success text-white">🏖️ İzin İste</div><div className="card-body bg-light"><form onSubmit={handleRequest}><div className="mb-2"><label className="small fw-bold">İzin Türü</label><select className="form-select" onChange={e=>setNewLeave({...newLeave, leave_type_id: parseInt(e.target.value)})} value={newLeave.leave_type_id}><option value="1">Yıllık İzin</option><option value="2">Mazeret İzni</option><option value="3">Rapor</option></select></div><div className="mb-2"><label className="small">Başlangıç</label><input type="date" className="form-control" required value={newLeave.start_date} onChange={e => setNewLeave({...newLeave, start_date: e.target.value})} /></div><div className="mb-2"><label className="small">Bitiş</label><input type="date" className="form-control" required value={newLeave.end_date} onChange={e => setNewLeave({...newLeave, end_date: e.target.value})} /></div><div className="mb-3"><label className="small">Sebep</label><textarea className="form-control" rows="2" required value={newLeave.reason} onChange={e => setNewLeave({...newLeave, reason: e.target.value})}></textarea></div><button className="btn btn-success w-100 fw-bold">Talep Oluştur</button></form></div></div></div>
                    <div className="col-md-8"><div className="card shadow border-0"><div className="card-header bg-secondary text-white">📋 Geçmiş İzinlerim</div><div className="card-body p-0"><table className="table table-hover mb-0"><thead className="table-light"><tr><th>Tür</th><th>Tarih</th><th>Durum</th></tr></thead><tbody>{leaves.map(l => (<tr key={l.id}><td>{l.leave_type_id === 1 ? <span className="badge bg-primary">Yıllık</span> : l.leave_type_id === 2 ? <span className="badge bg-warning text-dark">Mazeret</span> : <span className="badge bg-danger">Rapor</span>}</td><td><small>{l.start_date} / {l.end_date}</small></td><td>{l.status === "Onaylandı" ? <span className="badge bg-success">Onaylandı</span> : l.status === "Reddedildi" ? <span className="badge bg-danger">Reddedildi</span> : <span className="badge bg-secondary">Beklemede</span>}</td></tr>))}</tbody></table></div></div></div>
                </div>
            )}
        </div>
    )
}

function App() {
  const [token, setToken] = useState(null); const [user, setUser] = useState(null); const [email, setEmail] = useState(""); const [password, setPassword] = useState("");
  
  const handleLogin = async (e) => { 
      e.preventDefault(); 
      const formData = new FormData(); 
      formData.append('username', email); 
      formData.append('password', password); 
      try { 
          const res = await axios.post("http://127.0.0.1:8000/auth/login", formData); 
          const accessToken = res.data.access_token;
          setToken(accessToken);
          // Token ile kullanıcı bilgilerini çek
          const meRes = await axios.get("http://127.0.0.1:8000/auth/me", { headers: { Authorization: `Bearer ${accessToken}` } }); 
          setUser(meRes.data) 
      } catch (err) { 
          console.error("Giriş Hatası Detayı:", err);
          if (err.response) {
            alert(`Giriş Başarısız! Sunucu Mesajı: ${err.response.data.detail || err.message}`);
          } else {
            alert("Sunucuya ulaşılamıyor! (CORS veya Ağ Hatası)");
          }
      } 
  }

  const logout = () => { setToken(null); setUser(null); }

  if (!token) { 
      return (
        <div className="d-flex justify-content-center align-items-center vh-100 bg-dark">
            <div className="card p-4 shadow" style={{width: '350px'}}>
                <h3 className="text-center mb-3">İK SİSTEMİ</h3>
                <form onSubmit={handleLogin}>
                    <input className="form-control mb-2" placeholder="Email" onChange={e => setEmail(e.target.value)} />
                    <input className="form-control mb-3" type="password" placeholder="Şifre" onChange={e => setPassword(e.target.value)} />
                    <button className="btn btn-primary w-100">Giriş Yap</button>
                </form>
            </div>
        </div>
      ) 
  }

  // 2. YÜKLENİYOR EKRANI (Token var ama User yoksa)
  if (!user) {
      return (
          <div className="d-flex justify-content-center align-items-center vh-100">
              <div className="spinner-border text-primary" role="status"><span className="visually-hidden">Yükleniyor...</span></div>
              <h4 className="ms-3">Kullanıcı Bilgileri Alınıyor...</h4>
          </div>
      )
  }

  // 3. PANELLER
  if (user.role === "admin" || user.first_name === "Süper") return <AdminPanel token={token} onLogout={logout} user={user} />
  else if (user.role === "hr" || user.role === "İnsan Kaynakları") return <HRPanel token={token} user={user} onLogout={logout} />
  else return <EmployeePanel token={token} user={user} onLogout={logout} />
}

export default App