import os.path
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

def verifica_arquivo_anterior_existe(absCaminho_arquivo):
    return os.path.isfile(absCaminho_arquivo)


def get_qtd_editais_anteriores(nome_arquivo):
    arquivo = open(nome_arquivo, "r")
    qtdEditais = arquivo.read()
    return qtdEditais


def update_local(absfile_path, updated_number):
    # Update number saved locally
    file = open(absfile_path, "w")
    file.write(updated_number)
    file.close()


def get_qtd_editais_att():
    url = 'https://fundacaobutantan.org.br/licitacoes/ato-convocatorio'
    response = requests.get(url)
    html = BeautifulSoup(response.text, 'html.parser')

    for num, noticias in enumerate(html.select('.noticias_margin'), 1):
        if num == 1:
            tit = noticias.find('h5').get_text()
            data = noticias.find('small').get_text()
            x = [tit, data]
    x.append(str(num))
    return x


def enviar_email(get_qtd_editais_att):
    print("HÁ UM NOVO EDITAL")
    # import necessary packages

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib

    # create message object instance
    msg = MIMEMultipart()

    text = """ Olá, Como vai? :D

Um novo edital foi publicado!
Entre em https://fundacaobutantan.org.br/licitacoes/ato-convocatorio para conferir.
Att.
"""
    # "caio.cardim@integradora.com.br"
    # "henrique.pereira@integradora.com.br"
    emails = os.environ.get('emails').split(',')
    password = os.getenv('senha')
    msg['From'] = os.getenv('email')
    msg['Subject'] = f"NOVO {get_qtd_editais_att()[0]}"

    # add in the message body
    msg.attach(MIMEText(text, 'plain'))

    # create server
    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)
    for i in range(len(emails)):
        # send the message via the server.
        # print(emails[i])
        print("Email enviado com sucesso %s:" % (emails[i]))
        server.sendmail(msg['From'], [emails[i]], msg.as_string())
    server.quit()


def verificaSeAtualizou():
    caminhoDiretorioScript = os.path.dirname(__file__)
    nomeArquivo = "numero-anterior.txt"

    absCaminhoArquivo = os.path.join(caminhoDiretorioScript, nomeArquivo)

    anteriorExiste = verifica_arquivo_anterior_existe(absCaminhoArquivo)

    if anteriorExiste:
        qtdEditalAnterior = get_qtd_editais_anteriores(absCaminhoArquivo)
        attQtdEdital = get_qtd_editais_att()[2]

        if qtdEditalAnterior != attQtdEdital:
            update_local(absCaminhoArquivo, attQtdEdital)
            enviar_email(get_qtd_editais_att)
        else:
            print("SEM ATUALIZAÇÕES")
    else:
        attQtdEdital = get_qtd_editais_att()[2]
        update_local(absCaminhoArquivo, attQtdEdital)
        enviar_email(get_qtd_editais_att)


def main():
    updateFrequencyInSeconds = 3600

    while (True):
        verificaSeAtualizou()
        time.sleep(updateFrequencyInSeconds)


if __name__ == "__main__":
    main()