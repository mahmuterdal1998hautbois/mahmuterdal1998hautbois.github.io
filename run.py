import requests
import json
import os

token = os.getenv('TESLA_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print("Tesla API'ye bağlanılıyor...")
v_res = requests.get('https://fleet-api.prd.eu.vn.cloud.tesla.com/api/1/vehicles', headers=headers)
print("Araç listesi yanıt kodu:", v_res.status_code)

if v_res.status_code == 200:
    vehicles = v_res.json().get('response', [])
    print(f"Bulunan araç sayısı: {len(vehicles)}")
    if vehicles:
        vid = vehicles[0].get('id')
        print(f"Araç ID: {vid}")
        d_res = requests.get(f'https://fleet-api.prd.eu.vn.cloud.tesla.com/api/1/vehicles/{vid}/vehicle_data', headers=headers)
        print("Araç veri yanıt kodu:", d_res.status_code)
        
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
            print('✅ Başarılı: vehicle_data.json dosyası oluşturuldu!')
        else:
            print("Araç verisi alınamadı:", d_res.text)
    else:
        print("Hesapta kayıtlı araç bulunamadı.")
else:
    print("Token geçersiz veya yetkisiz:", v_res.text)
