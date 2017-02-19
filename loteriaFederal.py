import string
import os
import urllib2
import sys
import sendgrid
from sendgrid.helpers.mail import *
from Resultado import Resultado
from bs4 import BeautifulSoup
from cookielib import CookieJar

reload(sys)
sys.setdefaultencoding('utf-8')

urlLoteria = "http://loterias.caixa.gov.br/wps/portal/loterias/landing/federal"
    
def enviar_email(assunto, corpo, destino):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("andreb.angelucci@gmail.com")
    to_email = Email(destino)
    subject = assunto
    content = Content("text/plain", corpo)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())    
    if 200 <= response.status_code < 300:
        print "E-mail enviado com sucesso."
    else:
        print "Nao foi possivel enviar o e-mail."

def crawler():
    #busca o resultado da loteria federal.

    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    request = opener.open(urlLoteria)
    resultadoUrl = BeautifulSoup(request, "html.parser")    

    if (resultadoUrl is None):
        return

    concurso = resultadoUrl.find(attrs={"class", "title-bar"})    
    classResultado = resultadoUrl.find(attrs={"class":"resultado-loteria"})    
    strConcurso = concurso.h2.span.text
    strResultados = concurso.h2.span.text+ "\n"
    for resultados in classResultado.tbody.findAll('tr'):
        objResultado = Resultado()
        objResultado.premio = resultados.contents[1].text
        objResultado.set_resultado(resultados.contents[3].text)
        objResultado.valor = resultados.contents[5].text 
        strResultados = strResultados + objResultado.printar()

    print strResultados
    if (len(sys.argv) > 1):
        enviar_email("Loteria federal: " + strConcurso, strResultados, sys.argv[1])

if (__name__ == "__main__"):
    crawler()

