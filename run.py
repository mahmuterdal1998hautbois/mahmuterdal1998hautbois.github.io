import requests
import json
import os

token = os.getenv('TESLA_ACCESS_TOKEN')
if not token:
    print("❌ HATA: TESLA_ACCESS_TOKEN bulunamadı! GitHub Secrets ayarını kontrol edin.")
    exit(1)

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

try:
    print("Tesla API'ye bağlanılıyor...")
    v_res = requests.get('https://fleet-api.prd.eu.vn.cloud.tesla.com/api/1/vehicles', headers=headers)
    print("Yanıt Kodu:", v_res.status_code)
    
    data = v_res.json()
    vehicles = data.get('response', [])
    print(f"Bulunan araç sayısı: {len(vehicles)}")
    
    if not vehicles:
        print("❌ Araç bulunamadı. Yanıt içeriği:", data)
        exit(1)
        
    vid = vehicles[0].get('id')
    print(f"✅ Araç ID bulundu: {vid}")
    
    d_res = requests.get(f'https://fleet-api.prd.eu.vn.cloud.tesla.com/api/1/vehicles/{vid}/vehicle_data', headers=headers)
    print("Araç Veri Yanıt Kodu:", d_res.status_code)
    
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
        print("❌ Araç verisi alınamadı. Yanıt:", d_res.text)
        exit(1)

except Exception as e:
    print("❌ Beklenmeyen bir hata oluştu:", str(e))
    exit(1)
