import requests
import json
import os

token = os.getenv('TESLA_ACCESS_TOKEN')
if not token:
    print("❌ HATA: TESLA_ACCESS_TOKEN bulunamadı!")
    exit(1)

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Test edilecek olası tüm Tesla Fleet API bölgeleri
regions = [
    ("Avrupa (EU)", "https://fleet-api.prd.eu.vn.cloud.tesla.com"),
    ("Kuzey Amerika (NA)", "https://fleet-api.prd.na.cloud.tesla.com"),
    ("Asya-Pasifik (AP)", "https://fleet-api.prd.ap.cloud.tesla.com")
]

vehicles = []
selected_base_url = ""

for region_name, base_url in regions:
    url = f"{base_url}/api/1/vehicles"
    print(f"🔍 {region_name} sunucusu deneniyor: {url}")
    try:
        v_res = requests.get(url, headers=headers, timeout=10)
        print(f"Yanıt Kodu: {v_res.status_code}")
        if v_res.status_code == 200:
            data = v_res.json()
            found = data.get('response', [])
            if found:
                vehicles = found
                selected_base_url = base_url
                print(f"✅ BAŞARILI! Araçlar {region_name} bölgesinde bulundu.")
                break
            else:
                print(f"ℹ️ {region_name} yanıt verdi ancak hesapta araç listesi boş.")
        else:
            print(f"⚠️ {region_name} hata döndürdü: {v_res.text}")
    except Exception as e:
        print(f"⚠️ Bağlantı hatası ({region_name}): {str(e)}")

if not vehicles:
    print("\n❌ Hiçbir bölgede araç bulunamadı. Token'ın süresi dolmuş veya araç listesi izni (vehicle_device_data vb.) eksik olabilir.")
    exit(1)

vid = vehicles[0].get('id')
print(f"🚗 Hedef Araç ID: {vid}")

# Araç verilerini çek
data_url = f"{selected_base_url}/api/1/vehicles/{vid}/vehicle_data"
print(f"Veriler isteniyor: {data_url}")
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
    print('✅ BAŞARILI: vehicle_data.json dosyası oluşturuldu!')
else:
    print(f"❌ Araç verisi alınamadı (Kod: {d_res.status_code}): {d_res.text}")
    exit(1)

