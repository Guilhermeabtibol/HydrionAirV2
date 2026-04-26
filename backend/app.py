import serial
import serial.tools.list_ports
import json
import threading
import time
import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite requisições do React

# ------------------ CONFIGURAÇÃO DA SERIAL ------------------
def find_arduino_port():
    """Tenta encontrar automaticamente a porta do Arduino."""
    # Primeiro, verifica se foi passada por variável de ambiente
    env_port = os.environ.get('ARDUINO_PORT')
    if env_port:
        print(f"📌 Usando porta da variável de ambiente: {env_port}")
        return env_port
    
    # Tenta detectar automaticamente
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"🔍 Porta encontrada: {port.device} - {port.description}")
        if 'Arduino' in port.description or 'USB' in port.description or 'ttyUSB' in port.device:
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

# Verifica se estamos rodando no Docker (arquivo .dockerenv existe)
is_docker = os.path.exists('/.dockerenv')
if is_docker:
    print("🐳 Rodando dentro do container Docker")
    # No Docker, geralmente a porta é /dev/ttyUSB0 (montada)
    PORTA = '/dev/ttyUSB0'
    # Aguarda o dispositivo aparecer (pode demorar alguns segundos)
    for _ in range(10):
        if os.path.exists(PORTA):
            break
        time.sleep(1)
else:
    PORTA = find_arduino_port()

if PORTA is None:
    print("⚠️ Arduino não encontrado! Verifique a conexão e as permissões.")
    print("   Execute: sudo usermod -a -G dialout $USER e reinicie.")
    print("   Ou no Docker: certifique-se de que o dispositivo está montado.")
    PORTA = '/dev/ttyUSB0'  # fallback

print(f"📡 Conectando ao Arduino na porta {PORTA}")

try:
    ser = serial.Serial(PORTA, 9600, timeout=1)
    time.sleep(2)  # Aguarda estabilização
    print("✅ Serial aberta com sucesso!")
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
        print("⚠️ Thread serial não iniciada: ser é None")
        return
    print("🔄 Thread de leitura serial iniciada")
    while True:
        try:
            linha = ser.readline().decode('utf-8').strip()
            if linha:
                # Tenta interpretar como JSON
                dado = json.loads(linha)
                if "erro" not in dado:
                    dado["timestamp"] = time.time()
                    ultimo_dado = dado
                    print(f"✅ Dado recebido: {dado}")
                else:
                    print(f"⚠️ Erro do sensor: {dado}")
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

@app.route('/api/health')
def health():
    """Endpoint para verificar se o backend está vivo."""
    return jsonify({"status": "ok", "serial_connected": ser is not None})

if __name__ == '__main__':
    # Usa a porta definida por ambiente ou 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)