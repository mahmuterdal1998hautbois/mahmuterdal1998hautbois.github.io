import requests
import json
import os

token = os.getenv('TESLA_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Önce Avrupa (EU) adresini deniyoruz
url = 'https://fleet-api.prd.eu.vn.cloud.tesla.com/api/1/vehicles'
print("Tesla API'ye bağlanılıyor (EU)...")
v_res = requests.get(url, headers=headers)
print("Yanıt Kodu:", v_res.status_code)
print("Ham Yanıt:", v_res.text)

# Eğer EU'dan araç dönmezse, Kuzey Amerika (NA) adresini deneyelim
data = v_res.json()
vehicles = data.get('response', [])

if not vehicles:
    print("\nEU bölgesinde araç bulunamadı, Kuzey Amerika (NA) deneniyor...")
    url = 'https://fleet-api.prd.na.cloud.tesla.com/api/1/vehicles'
    v_res = requests.get(url, headers=headers)
    print("NA Yanıt Kodu:", v_res.status_code)
    print("NA Ham Yanıt:", v_res.text)
    vehicles = v_res.json().get('response', [])

if vehicles:
    vid = vehicles[0].get('id')
    print(f"\n✅ Araç Bulundu! ID: {vid}")
    
    # Doğru URL ile veri çekme
    base_url = url.replace('/vehicles', '')
    d_res = requests.get(f'{base_url}/vehicles/{vid}/vehicle_data', headers=headers)
    
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
        print('✅ vehicle_data.json başarıyla oluşturuldu!')
    else:
        print("Araç verisi alınamadı:", d_res.text)
else:
    print("\n❌ Hiçbir bölgede araç bulunamadı. Token'ın izinlerini kontrol etmek gerekebilir.")
