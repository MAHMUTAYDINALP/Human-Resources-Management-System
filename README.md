👥 Human Resources Management System (HRMS) - Full Stack
Bu proje; personel yönetimi, izin takibi, ekip koordinasyonu ve duyuru süreçlerini kapsayan profesyonel bir İnsan Kaynakları Yönetim Sistemidir. FastAPI (Backend) ve React (Frontend) mimarisi ile geliştirilmiş olup, veritabanı bütünlüğü ve güvenli kullanıcı yetkilendirmesi süreçlerini temel alır.

🛠️ Uygulanan Teknik Çözümler ve Özellikler
1. Veri Güvenliği ve Doğrulama
Password Hashing: Kullanıcı şifreleri veritabanında düz metin olarak değil, bcrypt algoritması ile hashlenerek saklanır.

Regex (Düzenli İfadeler): Kullanıcı kayıt ve giriş süreçlerinde e-posta formatı ve şifre kriterleri Regular Expressions kullanılarak sunucu tarafında doğrulanır.

JWT Auth: Sistem erişimi JSON Web Token tabanlı yetkilendirme ile korunmaktadır.

2. Gelişmiş CRUD ve İş Mantığı
Otomatik İzin & Maaş: Personel eklenirken seçilen role göre (Yazılımcı, Yönetici vb.) yıllık izin hakları ve başlangıç maaşları sistem tarafından otomatik atanır.

Ekiplere Özel Duyuru: Duyurular genel veya sadece belirli bir Team ID'ye bağlı ekibin göreceği şekilde yayınlanabilir.

İlişkisel Bütünlük (Cascade): Bir kullanıcı silindiğinde, ona bağlı personel kartı ve izin kayıtları veritabanı seviyesinde otomatik olarak temizlenir.

3. Dinamik Dashboard ve Raporlama
İstatistik Paneli: Toplam personel, cinsiyet dağılımı ve aktif ekip sayıları anlık olarak dashboard üzerinden izlenebilir.

Doğum Günü Takibi: Yaklaşan personel doğum günlerini listeleyen özel bir bildirim sistemi mevcuttur.

📸 Uygulama Görselleri
Sistem dökümantasyonu ve veritabanı yapısına ait görseller dokumanlar/ klasöründe yer almaktadır:

<img width="1918" height="957" alt="giriş ekranı" src="https://github.com/user-attachments/assets/3f08e964-f5f3-49a1-9b32-b5b0c72b650f" />
<img width="1912" height="959" alt="çalışan ekibe özel ve herkese açık gelen duyuruları görmesi" src="https://github.com/user-attachments/assets/e7e63722-96b0-47f1-8e24-9faf4114531a" />
<img width="1914" height="961" alt="insan kaynakları izin isteklerini gördügü panel" src="https://github.com/user-attachments/assets/2852f7d3-eb38-4c35-9c42-6a0f6b2a3e78" />
<img width="1912" height="998" alt="personel ekleme" src="https://github.com/user-attachments/assets/a9b6c74a-e581-4522-b7ca-96b1ac0bb7df" />
<img width="1915" height="954" alt="çalışan ekranı(duyuru paneli,izin hakları ,izin alma paneli)" src="https://github.com/user-attachments/assets/6c4b160b-080a-4f27-ad53-fcf257558158" />
<img width="1916" height="957" alt="çalışan onaylanan ve beklenen izinleri göçrüyor ve onaylanan izin talebi izin hakkından düşüyor" src="https://github.com/user-attachments/assets/648ec9d0-24fe-4011-8246-b7e803a9640f" />
<img width="1912" height="959" alt="çalışan ekibe özel ve herkese açık gelen duyuruları görmesi" src="https://github.com/user-attachments/assets/2382d823-be73-4b03-b90d-a9d445beb027" />
<img width="1915" height="955" alt="insan kaynakları izindekilerin listesini görme ekranı" src="https://github.com/user-attachments/assets/4775be32-2683-4fc0-8081-2eb32839ceca" />




Sistem Mimarisi (Loglar): 

🚀 Kurulum ve Çalıştırma
1. Backend (FastAPI)
cd backend

python -m venv venv

.\venv\Scripts\activate (Windows)

pip install -r requirements.txt

uvicorn app.main:app --reload

2. Frontend (React + Vite)
cd frontend

npm install

npm run dev

3. Veritabanı (PostgreSQL)
PostgreSQL üzerinde bir veritabanı oluşturun.

DATABASE/ klasöründeki şemayı içe aktarın.

leave_types ve employment_types tablolarına gerekli tanımlamaları ekleyin.


Geliştiren: Mahmut AydınAlp
https://www.linkedin.com/in/mahmut-ayd%C4%B1nalp-659875282/      
https://github.com/MAHMUTAYDINALP
