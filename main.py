
import requests,smtplib,subprocess,time,random,logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

MON_NUMERO="+2620692559626"
GMAIL_ADDRESS="insafahar29@gmail.com"
GMAIL_PASSWORD="pghd vibo hxxk hpik"
TELEGRAM_BOT_TOKEN="8511612333:AAH0Lm2CcQRY6qI6hw0IvmK0_LtAyINOZnM"
TELEGRAM_CHAT_ID="7532311421"

INTERVALLE_MIN=30
INTERVALLE_MAX=60

USER_AGENTS=["Mozilla/5.0 (Linux; Android 13; Samsung Galaxy S23) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"]

DEMARCHES={"Premiere demande":{"url":"https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/6860/creneau/"},"Renouvellement":{"url":"https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/6880/creneau/"}}

logging.basicConfig(level=logging.INFO,format="%(asctime)s %(message)s")
log=logging.getLogger(__name__)

def envoyer_sms(m):
    try:
        subprocess.run(["termux-sms-send","-n",MON_NUMERO,m],timeout=15)
        log.info("SMS envoye !")
    except Exception as e:
        log.error(f"SMS erreur: {e}")

def envoyer_telegram(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",data={"chat_id":TELEGRAM_CHAT_ID,"text":m},timeout=10)
        log.info("Telegram envoye !")
    except Exception as e:
        log.error(f"Telegram erreur: {e}")

def envoyer_email(s,m):
    try:
        msg=MIMEMultipart()
        msg["Subject"]=s
        msg["From"]=GMAIL_ADDRESS
        msg["To"]=GMAIL_ADDRESS
        msg.attach(MIMEText(m,"plain","utf-8"))
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as srv:
            srv.login(GMAIL_ADDRESS,GMAIL_PASSWORD)
            srv.sendmail(GMAIL_ADDRESS,GMAIL_ADDRESS,msg.as_string())
        log.info("Email envoye !")
    except Exception as e:
        log.error(f"Email erreur: {e}")

def notifier(d,url):
    now=datetime.now().strftime("%d/%m/%Y a %H:%M:%S")
    m=f"CRENEAU DISPO ! MAYOTTE\n{d}\n{now}\nRESERVE VITE : {url}"
    envoyer_sms(m)
    envoyer_telegram(m)
    envoyer_email("URGENT RDV MAYOTTE "+d,m)

def verifier(nom,url,session):
    try:
        headers={"User-Agent":random.choice(USER_AGENTS),"Accept-Language":"fr-FR,fr;q=0.9","Accept":"text/html","Referer":"https://www.google.fr/"}
        r=session.get(url,headers=headers,timeout=15)
        t=r.text.lower()
        if r.status_code!=200:
            log.warning(f"Statut {r.status_code} pour {nom} - on ignore")
            return False
        if "enable javascript" in t or "enable cookies" in t or "just a moment" in t or "challenge" in t:
            log.warning(f"Cloudflare bloque {nom} - on ignore")
            return False
        if "choisissez votre cr\u00e9neau" in t:
            log.info(f"DISPO !!! {nom}")
            return True
        log.info(f"INDISPO: {nom}")
        return False
    except Exception as e:
        log.error(f"Erreur {nom}: {e}")
        return False

def main():
    log.info("SURVEILLANCE DEMARREE !")
    session=requests.Session()
    alerte={n:False for n in DEMARCHES}
    c=0
    while True:
        c+=1
        log.info(f"Verification #{c}")
        for nom,config in DEMARCHES.items():
            dispo=verifier(nom,config["url"],session)
            if dispo and not alerte[nom]:
                notifier(nom,config["url"])
                alerte[nom]=True
            elif not dispo and alerte[nom]:
                alerte[nom]=False
        attente=random.uniform(INTERVALLE_MIN,INTERVALLE_MAX)
        log.info(f"Prochain controle dans {attente:.0f}s")
        time.sleep(attente)

if __name__=="__main__":
    try:main()
    except KeyboardInterrupt:log.info("Arrete.")
