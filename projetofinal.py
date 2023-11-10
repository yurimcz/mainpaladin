import os.path
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from bs4 import BeautifulSoup
import time

while True:
    nomes = ["Ambra", "Antica", "Astera", "Axera", "Belobra", "Bombra", "Bona",
             "Calmera", "Castela", "Celebra", "Celesta", "Collabra", "Damora", "Descubra",
             "Dia", "Epoca", "Esmera", "Etebra", "Ferobra", "Firmera", "Flamera",
             "Gentebra", "Gladera", "Gravitera", "Guerribra", "Harmonia", "Havera", "Honbra",
             "Impulsa", "Inabra", "Issobra", "Jacabra", "Jadebra", "Jaguna", "Kalibra",
             "Kardera", "Kendria", "Lobera", "Luminera", "Lutabra", "Menera", "Monza",
             "Mykera", "Nadora", "Nefera", "Nevia", "Obscubra", "Ombra", "Ousabra",
             "Pacera", "Peloria", "Premia", "Pulsera", "Quelibra", "Quintera", "Rasteibra", "Refugia", "Retalia", "Runera",
             "Secura", "Serdebra", "Solidera", "Syrena", "Talera", "Thyria", "Tornabra", "Ustebra",
             "Utobra", "Venebra", "Vitera", "Vunira", "Wadira", "Wildera", "Wintera", "Yonabra", "Yovera", "Zuna", "Zunera"
             ]

    nome_boneco = "Main Paladin"
    url = "https://www.tibia.com/community/?name=" + nome_boneco

    requisicao = requests.get(url)

    if requisicao.status_code == 200:
        soup = BeautifulSoup(requisicao.text, "html.parser")
        elementos_de_texto = soup.find_all(string=True)
        primeiro_nome_encontrado = None

        for elemento in elementos_de_texto:
            for nome in nomes:
                if nome in elemento:
                    primeiro_nome_encontrado = nome
                    break

            if primeiro_nome_encontrado:
                break

        if primeiro_nome_encontrado:
            online_world = "https://www.tibia.com/community/?subtopic=worlds&world=" + primeiro_nome_encontrado

            requisicao2 = requests.get(online_world)

            if requisicao2.status_code == 200:
                soup = BeautifulSoup(requisicao2.text, 'html.parser')
                tags_a = soup.find_all("a", href=True)
                encontrado = False

                for tag in tags_a:
                    if nome_boneco in tag["href"]:
                        encontrado = True
                        break

                if not encontrado and " " in nome_boneco:
                    nome_com_espaco_substituido = nome_boneco.replace(" ", "+")
                    for tag in tags_a:
                        if nome_com_espaco_substituido in tag["href"]:
                            encontrado = True
                            break

                if encontrado:
                    status_boneco = "Online"
                else:
                    data_hora_atual = datetime.now()
                    formato_personalizado = data_hora_atual.strftime("%Y-%m-%d %H:%M")
                    status_boneco = "Offline"
            else:
                print(f'Erro ao fazer a solicitação. Código de status: {requisicao2.status_code}')

            SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
            SAMPLE_SPREADSHEET_ID = "14VFxTvSA2D9rjDob_0xj11eyqlFxiFuH-CWqKRiI0Aw"

            def find_next_empty_row(sheet):
                col_values = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                range="Página1!A:A").execute().get('values', [])
                return len(col_values) + 1

            def main():
                creds = None

                if os.path.exists("token.json"):
                    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            "credentials.json", SCOPES
                        )
                        creds = flow.run_local_server(port=0)

                        with open("token.json", "w") as token:
                            token.write(creds.to_json())

                try:
                    service = build("sheets", "v4", credentials=creds)
                    sheet = service.spreadsheets()

                    data_hora_atual = datetime.now()
                    formato_personalizado = data_hora_atual.strftime("%Y-%m-%d %H:%M")
                    next_row = find_next_empty_row(sheet)
                    valor_personagem = nome_boneco
                    valor_status = status_boneco
                    valor_dia = formato_personalizado
                    valores_adicionar = [[valor_personagem, valor_status, valor_dia]]

                    result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                    range=f"Página1!A{next_row}",
                                                    valueInputOption="USER_ENTERED",
                                                    body={'values': valores_adicionar}).execute()
                    print("feito")

                except HttpError as err:
                    print(err)

            if __name__ == "__main__":
                main()

    time.sleep(60)
