import requests
import json
import os

# GitHub Secrets'tan Refresh Token alınıyor
refresh_token = os.getenv('TESLA_REFRESH_TOKEN')
if not refresh_token:
    print("❌ HATA: TESLA_REFRESH_TOKEN bulunamadı! GitHub Secrets ayarlarını kontrol edin.")
    exit(1)

# Tesla OAuth Token Yenileme (Refresh) Adımı
print("🔄 Refresh Token kullanılarak yeni Access Token isteniyor...")
token_url = "https://auth.tesla.com/oauth2/v3/token"
token_payload = {
    "grant_type": "refresh_token",
    "client_id": "ownerapi",  # Resmi olmayan veya standart fleet client ID (gerekirse değiştirilebilir)
    "refresh_token": refresh_token,
    "scope": "openid email offline_access vehicle_device_data"
}

try:
    t_res = requests.post(token_url, json=token_payload, timeout=10)
    if t_res.status_code != 200:
        print(f"❌ Token yenilenemedi (Kod: {t_res.status_code}): {t_res.text}")
        exit(1)
        
    token_data = t_res.json()
    access_token = token_data.get('access_token')
    if not access_token:
        print("❌ Yanıttan access_token çıkarılamadı:", token_data)
        exit(1)
        
    print("✅ Yeni Access Token başarıyla alındı!")
except Exception as e:
    print("❌ Token yenileme sırasında bağlantı hatası:", str(e))
    exit(1)

# Yeni token ile API bağlantı ayarları
headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

# Çoklu bölge taraması (EU, NA, AP)
regions = [
    ("Avrupa (EU)", "https://fleet-api.prd.eu.vn.cloud.tesla.com"),
    ("Kuzey Amerika (NA)", "https://fleet-api.prd.na.cloud.tesla.com"),
    ("Asya-Pasifik (AP)", "https://fleet-api.prd.ap.cloud.tesla.com")
]

vehicles = []
selected_base_url = ""

for region_name, base_url in regions:
    url = f"{base_url}/api/1/vehicles"
    print(f"🔍 {region_name} sunucusu taranıyor...")
    try:
        v_res = requests.get(url, headers=headers, timeout=10)
        if v_res.status_code == 200:
            found = v_res.json().get('response', [])
            if found:
                vehicles = found
                selected_base_url = base_url
                print(f"✅ Araç {region_name} bölgesinde bulundu!")
                break
    except Exception as e:
        print(f"⚠️ {region_name} bağlantı hatası: {str(e)}")

if not vehicles:
    print("❌ Hiçbir bölgede araç bulunamadı. Lütfen Refresh Token'ın doğru hesaba ait olduğundan emin olun.")
    exit(1)

vid = vehicles[0].get('id')
print(f"🚗 Hedef Araç ID: {vid}")

# Araç verilerini çek
data_url = f"{selected_base_url}/api/1/vehicles/{vid}/vehicle_data"
d_res = requests.get(data_url, headers=headers)

if d_res.status_code == 200:
    v_data = d_res.json().get('response', {})
    charge = v_data.get('charge_state', {})
    drive = v_data.get('drive_state', {})
    v_state = v_data.get('vehicle_state', {})
    
    payload = {
        'battery_level': charge.get('battery_level', 0),
        'battery_range': round(charge.get('battery_range', 0) * 1.60934, 1),
        'odometer': round(v_state.get('odometer', 0) * 1.60934, 1),
        'speed': drive.get('speed') or 0,
        'state': v_data.get('state', 'unknown')
    }
    
    with open('vehicle_data.json', 'w') as f:
        json.dump(payload, f, indent=4)
    print('✅ BAŞARILI: vehicle_data.json güncellendi!')
else:
    print(f"❌ Araç verisi alınamadı (Kod: {d_res.status_code}): {d_res.text}")
    exit(1)
