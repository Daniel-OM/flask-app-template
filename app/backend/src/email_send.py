
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from pathlib import Path


class EmailSender:

    '''
    Class for coordinating the email server in gmail.
    '''

    def login(self,user:str='omsignalstrading@gmail.com',password:str='tpufrsjyiuijpnnl',tls:bool=True) -> None:

        '''
        Logs in the email server. Doesn't return anything.

        Parameters
        ----------
        user: str
            Email used.
        password: str
            Password for the email used.
        tls: bool
            True for starting tls (security protocol).
        '''

        self.user: str = user
        self.password: str = password
        
        # Creates SMTP session
        self.smtp: smtplib.SMTP = smtplib.SMTP(host='smtp.gmail.com', port=587)

        if tls:
            # Start TLS for security
            self.smtp.starttls()

        # Authentication
        self.smtp.login(user=self.user, password=self.password)

    def send(self,message:str,subject:str='OM Trading Signals',destinatary:list=['dcaronm@gmail.com'],
            files:list=[],html:bool=False) -> None:

        '''
        Sends an email. Doesn't return anything.

        Parameters
        ----------
        message: str
            Main content of the email.
        subject: str
            Subject of the email.
        destinatary: list
            List of destinatary emails.
        files: list
            List of paths to the files we want to attach to the email.
        html: bool
            True to attach html.
        '''
        
        # Instance of MIMEMultipart
        self.msg: MIMEMultipart = MIMEMultipart()
        self.msg['From'] = self.user
        self.msg['To'] = COMMASPACE.join(destinatary)
        self.msg['Date'] = formatdate(localtime=True)
        self.msg['Subject'] = subject

        # Message to be sent
        if html:
            self.msg.attach(payload=MIMEText(_text=message,_subtype='html'))
        else:
            self.msg.attach(payload=MIMEText(_text=message))

        
        for path in files:
            part: MIMEBase = MIMEBase(_maintype='application', _subtype="octet-stream")
            with open(file=path, mode='rb') as file:
                part.set_payload(payload=file.read())
            encoders.encode_base64(msg=part)
            part.add_header(_name='Content-Disposition',
                            _value='attachment; filename={}'.format(Path(path).name))
            self.msg.attach(payload=part)

        message: str = self.msg.as_string()
        for dest in destinatary:
            # Sending the mail
            self.smtp.sendmail(from_addr=self.user, to_addrs=dest, msg=message)

    def logout(self) -> None:

        '''
        Logs out of the email session. Doesn't return anything.
        '''
        
        # Terminating the session
        self.smtp.quit()

if __name__ == '__main__':

    es = EmailSender()
    es.login()
    es.send(message='Esta es la prueba de una señal',files=[])
    es.logout()

