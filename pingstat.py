import pyping
import datetime


print datetime.datetime.now() 

hostname = "mymusictaste.com"

response = pyping.ping(hostname,count=100)


packet_lost = response.packet_lost
min_rtt = response.min_rtt
avg_rtt = response.avg_rtt
max_rtt = response.max_rtt
ip_info = response.destination_ip
ret_code = response.ret_code
packet_size = response.packet_size
timeout = response.timeout
destination = response.destination

print "Packet Lost : " , packet_lost
print "Min Rtt : " , min_rtt
print "Max Rtt : " , max_rtt
print "Avg Rtt : " , avg_rtt
print "ret_code : ", ret_code
print "packet_size : " , packet_size
print "timeout : " , timeout
print "destination : " , destination

if packet_lost > 50:
    
    import re
    import subprocess
    
    command = "traceroute -I -w 1 -n -q 1 "+ip_info
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()
    outwithoutreturn = out.rstrip('\n')
    
    outputlist =  re.split('\n',out)
    index = 0
    serverstate = 0
    for linelist in outputlist[:-1]:
        if index < 9:
            temp = linelist[1:]
        else:
            temp = linelist
        index += 1
        linesplit = re.split('\s{1,}',temp)

        if ip_info == linesplit[1] and int(linesplit[0]) <64:
            print "Server is alive!!"
            serverstate = 1
            break
    if not serverstate:
        print "Server is dead!!"      
        import MySQLdb     
        db = MySQLdb.connect("192.168.73.180", "root", "dnflwlq2", "status")
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS ping_stat(
                            regTm TIMESTAMP NOT NULL DEFAULT NOW(),
                            pkLt FLOAT(5) NOT NULL,
                            minRtt FLOAT(4) NOT NULL,
                            maxRtt FLOAT(4) NOT NULL,
                            avgRtt FLOAT(4) NOT NULL,
                            DetnIp VARCHAR(15) NOT NULL)""")
        cursor.execute("INSERT INTO ping_stat(pkLt,minRtt,maxRtt,avgRtt,DetnIp) VALUES('%s', '%s', '%s','%s','%s')" % (packet_lost, min_rtt, max_rtt, avg_rtt,ip_info))
        db.commit()
        db.close()
        
        import smtplib
        pingmessage = "Packet Lost : %s \
        Min Rtt : %s \
        Max Rtt : %s \
        Avg Rtt : %s \
        Destination IP : %s" % (packet_lost, min_rtt, max_rtt, avg_rtt, ip_info)
        message = pingmessage + out
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEBase import MIMEBase
        from email.MIMEText import MIMEText
        from email import Encoders
        from email import Utils
        from email.header import Header
        import os
        smtp_server  = "smtp.gmail.com"
        port = "587"
        userid = "hannut91@gmail.com"
        passwd = "s7458154"

        def send_mail(from_user, to_user, subject, text, attach):
            COMMASPACE = ", "
            msg = MIMEMultipart("alternative")
            msg["From"] = from_user
            msg["To"] = to_user
            msg["Subject"] = Header(s=subject, charset="utf-8")
            msg["Date"] = Utils.formatdate(localtime = 1)
            msg.attach(MIMEText(text, "html", _charset="utf-8"))

            if (attach != None):
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(open(attach, "rb").read())
                    Encoders.encode_base64(part)
                    part.add_header("Content-Disposition", "attachment; filename=\"%s\"" % os.path.basename(attach))
                    msg.attach(part)

            smtp = smtplib.SMTP_SSL('smtp.gmail.com:465')
            smtp.ehlo()
            smtp.login(userid, passwd)
            smtp.sendmail(from_user,to_user, msg.as_string())
            smtp.close()
            
        send_mail("hannut91@gmail.com","hannut91@gmail.com","Your server status summary",message,None)
