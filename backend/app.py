import serial
import serial.tools.list_ports
import json
import threading
import time
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app)  # Permite requisições do React em desenvolvimento

# ------------------ CONFIGURAÇÃO DA SERIAL ------------------
def find_arduino_port():
    """Tenta encontrar automaticamente a porta do Arduino."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'Arduino' in port.description or 'USB' in port.description:
            return port.device
    # Se não encontrar, tenta portas comuns
    for p in ['/dev/ttyUSB0', '/dev/ttyACM0']:
        try:
            s = serial.Serial(p, timeout=0.5)
            s.close()
            return p
        except:
            pass
    return None

PORTA = find_arduino_port()
if PORTA is None:
    print("⚠️ Arduino não encontrado! Verifique a conexão e as permissões.")
    print("   Execute: sudo usermod -a -G dialout $USER e reinicie.")
    PORTA = '/dev/ttyUSB0'  # fallback, pode dar erro

print(f"📡 Conectando ao Arduino na porta {PORTA}")

try:
    ser = serial.Serial(PORTA, 9600, timeout=1)
    time.sleep(2)  # Aguarda estabilização
except Exception as e:
    print(f"❌ Erro ao abrir a porta {PORTA}: {e}")
    ser = None

# ------------------ DADOS EM MEMÓRIA ------------------
ultimo_dado = {
    "temperatura": None,
    "umidade": None,
    "co_ppm": None,
    "timestamp": None
}

def ler_serial():
    """Thread que lê a serial continuamente e atualiza ultimo_dado."""
    global ultimo_dado
    if ser is None:
        return
    while True:
        try:
            linha = ser.readline().decode('utf-8').strip()
            if linha:
                # Tenta interpretar como JSON
                dado = json.loads(linha)
                if "erro" not in dado:
                    dado["timestamp"] = time.time()
                    ultimo_dado = dado
                    print(f"✅ Dado recebido: {dado}")  # opcional
        except json.JSONDecodeError:
            print(f"⚠️ Linha não-JSON: {linha}")
        except Exception as e:
            print(f"Erro na leitura serial: {e}")
        time.sleep(0.1)

# Inicia a thread de leitura
if ser:
    thread_serial = threading.Thread(target=ler_serial, daemon=True)
    thread_serial.start()
else:
    print("⚠️ Thread serial não iniciada porque não foi possível abrir a porta.")

# ------------------ ROTAS DA API ------------------
@app.route('/api/dados')
def api_dados():
    """Retorna o último dado lido do Arduino."""
    return jsonify(ultimo_dado)

@app.route('/')
def serve_react():
    """Serve o frontend React (após build)."""
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)