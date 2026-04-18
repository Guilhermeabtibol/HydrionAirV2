
# Hydrion Air




---

## 📁 Estrutura final do projeto (exemplo)

```
hydrion_air/
├── arduino/
│   └── sensor_reader/
│       └── sensor_reader.ino
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ...
└── README.md
```

---

## 🐍 1. Arquivo `backend/requirements.txt`

Crie este arquivo dentro da pasta `backend` com o seguinte conteúdo:

```
flask==3.1.0
flask-cors==5.0.0
pyserial==3.5
```

> Use essas versões exatas ou apenas os nomes dos pacotes. O `pyserial` é essencial para comunicação com o Arduino.

---

## 📄 2. Documentação `README.md` (para o repositório/usuário)

Coloque o arquivo `README.md` na raiz do projeto (mesmo nível das pastas `backend`, `frontend`, `arduino`). Copie e cole o conteúdo abaixo:

```markdown
# 🌍 Hydrion Air - Estação Ambiental com Arduino + Flask + React

Monitoramento em tempo real de temperatura, umidade e monóxido de carbono (CO) usando Arduino Uno, sensores DHT11 e MQ-7, com visualização em dashboard com gráficos dinâmicos.

## 📋 Pré‑requisitos

- **Linux Mint / Ubuntu** (outros Linux podem funcionar, mas os comandos são para Debian‑based)
- **Python 3.10+** e `pip`
- **Node.js 18+** e `npm`
- **Arduino Uno R3** com cabo USB
- **Sensores**: DHT11 (módulo 3 pinos) e MQ-7
- **Acesso `sudo`** para configurar permissões de porta serial

## 🔧 1. Clonar / obter o projeto

```bash
git clone https://github.com/seu-usuario/hydrion_air.git
cd hydrion_air
```

## 🔌 2. Configurar o Arduino

### 2.1. Instalar bibliotecas necessárias (via Arduino CLI ou Arduino IDE)

- **DHT sensor library** (Adafruit)
- **MQUnifiedsensor** (miguel5612)

Se você usa Arduino CLI (recomendado para Linux):

```bash
arduino-cli lib install "DHT sensor library"
arduino-cli lib install "MQUnifiedsensor"
```

> Caso não tenha o Arduino CLI: siga [arduino.github.io/arduino-cli](https://arduino.github.io/arduino-cli)

### 2.2. Carregar o sketch

Abra o arquivo `arduino/sensor_reader/sensor_reader.ino` na Arduino IDE ou no VS Code com extensão Arduino. Selecione a placa **Arduino Uno** e a porta serial (ex: `/dev/ttyUSB0`). Faça o upload.

> ⚠️ **Linux – permissão de porta**: se ocorrer erro `Permission denied`, execute:
> ```bash
> sudo usermod -a -G dialout $USER
> ```
> **Reinicie o computador** para a mudança fazer efeito.

### 2.3. Verificar se o Arduino está enviando dados

Abra o monitor serial (9600 baud). Você deve ver linhas JSON como:

```json
{"temperatura":22.5,"umidade":55.0,"co_ppm":8.2}
```

## 🐍 3. Backend Flask (API e leitor serial)

### 3.1. Criar ambiente virtual e instalar dependências

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3.2. Executar o servidor

```bash
python app.py
```

O servidor iniciará em `http://localhost:5000`. Ele:
- Lê a porta serial do Arduino (automática ou `/dev/ttyUSB0`)
- Expõe um endpoint `GET /api/dados` com o último dado em JSON
- Serve o frontend React (após build)

> **Problema comum**: porta 5000 já em uso. Use `sudo lsof -i :5000` para identificar o processo e matá-lo (`kill -9 PID`).

## ⚛️ 4. Frontend React (Dashboard com gráficos)

### 4.1. Instalar dependências do Node

```bash
cd ../frontend   # ou cd frontend se já estiver na raiz
npm install
```

> A biblioteca `recharts` (gráficos) já está incluída no `package.json`. Se não estiver, instale com:
> ```bash
> npm install recharts
> ```

### 4.2. Configurar proxy para o backend (em desenvolvimento)

Edite `frontend/package.json` e adicione a linha:

```json
"proxy": "http://localhost:5000"
```

Exemplo:

```json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "proxy": "http://localhost:5000",
  "dependencies": {
    ...
  }
}
```

### 4.3. Executar o servidor de desenvolvimento

```bash
npm start
```

O dashboard abrirá em `http://localhost:3000` e começará a buscar os dados do backend a cada 2 segundos.

## 🚀 5. Execução completa (dois terminais)

**Terminal 1 – Backend**:
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 – Frontend**:
```bash
cd frontend
npm start
```

> O Arduino já deve estar conectado e com o sketch carregado.

## 📊 Funcionalidades do Dashboard

- Cards com valores atuais (temperatura, umidade, CO)
- Indicador de qualidade do ar (Boa, Moderada, Ruim, Perigosa)
- Gráficos de linha para histórico das últimas 20 leituras
- Gráfico de pizza com distribuição da qualidade do ar
- Alerta visual quando CO > 50 ppm
- Atualização automática a cada 2 segundos

## 🐛 Solução de problemas comuns

| Problema | Possível solução |
|----------|------------------|
| `Permission denied` ao acessar `/dev/ttyUSB0` | Adicione usuário ao grupo `dialout` e reinicie. |
| Backend não encontra o Arduino | Verifique a porta em `app.py` ou defina manualmente. |
| Porta 5000 ocupada | Mate o processo ou altere a porta no `app.py` e no proxy do React. |
| React não exibe dados | Confira se o Flask está rodando e se o proxy está correto. |
| Leituras do MQ-7 negativas ou muito altas | Aguarde 15‑30 minutos para aquecimento do sensor. |

## 📚 Tecnologias utilizadas

- **Arduino C++** – leitura dos sensores e envio via Serial
- **Flask** – API REST e leitor serial
- **React** – interface com usuário
- **Recharts** – gráficos interativos
- **Axios** – requisições HTTP

## 📝 Licença

Este projeto é de uso livre para fins educacionais.

---

Desenvolvido por Guilherme Abtibol

