from datetime import datetime
import time
from typing import List

from Models import ClientSession,MonitorActivity
import Models
from sqlalchemy import create_engine
from Config import config
from sqlalchemy.orm import sessionmaker


class Monitor(object):
    def __init__(self,path:str):
        self.path=path
        Session = sessionmaker(bind=Models.engine)
        self.session = Session()

    def execute(self):
        print("Starting")
        self.update_activity()
        print("Monitor activity updated")
        sessions=self.parse_file()
        if sessions:
            self.process_client_sessions(sessions)
        else:
            print("[NO CONNECTION]")
        print("Finished")

    def parse_file(self)->List[ClientSession]:
        clientsInfo = []  # type:List[str]
        with open(self.path) as f:
            startFlag=False
            for line in f.readlines():
                if line.startswith("Common Name"):
                    startFlag=True
                    print("Entering interested area")
                    continue
                if line.startswith("ROUTING TABLE"):
                    startFlag=False
                    print("Exit interested area")
                    break
                if startFlag:
                    if line.strip():
                        clientsInfo.append(line.strip())
        print("Extracted client info")
        print(clientsInfo)
        csList=[] #type:List[ClientSession]
        if len(clientsInfo)==0:
            return None
        for info in clientsInfo:
            csList.append(self.parse_line(info))
        return csList

    def parse_line(self,line:str)->ClientSession:
        attrs=line.split(",")
        if len(attrs)<5:
            print("[ERROR DATA ERROR - not enough attributes]")
            return
        cs=ClientSession(commName=attrs[0],
                         realAddr=attrs[1],
                         bytesRev=int(attrs[2]),
                         bytesSent=int(attrs[3]),
                         connectedSince=attrs[4],
                         connectedTo=datetime.now())
        return cs
    def process_client_sessions(self,sessions:List[ClientSession]):
        for index,session in enumerate(sessions):
            print("----------Processing session %d----------"%index)
            csOld=self.get_recorded_session(session)
            if csOld:
                csOld.bytesRev=session.bytesRev
                csOld.bytesSent=session.bytesSent
                csOld.connectedTo=datetime.now()
                self.session.commit()
                print("Existing session updated (%s)"%csOld)
                print("[UPDATED %s]"%csOld.commName)
            else:
                self.session.add(session)
                self.session.commit()
                print("No existing session found, added new session (%s)"%session)
                print("[ADDED %s]"%session.commName)

    def get_recorded_session(self,cs:ClientSession)->ClientSession:
        csOld=self.session.query(ClientSession).filter_by(commName=cs.commName,connectedSince=cs.connectedSince).all()
        if len(csOld)==0:
            print("No session found for %s"%cs)
            return None
        print("Session found ({0})".format(cs))
        print("Old session (%s)"%csOld)
        return csOld[0]

    def update_activity(self):
        existingRow=self.session.query(MonitorActivity).first() #type:MonitorActivity
        if existingRow:
            existingRow.lastSeen=datetime.now()
            self.session.commit()
        else:
            activity=MonitorActivity()
            activity.lastSeen=datetime.now()
            self.session.add(activity)
            self.session.commit()


if __name__=="__main__":
    m=Monitor(config["logPath"])
    while True:
        m.execute()
        time.sleep(int(config["logInterval"]))


