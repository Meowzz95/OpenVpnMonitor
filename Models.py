from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine,BIGINT,DateTime

from Config import config
from Decos import auto_repr

Base = declarative_base()

@auto_repr
class ClientSession(Base):
    __tablename__="ClientSession"

    id=Column(Integer,primary_key=True)
    commName=Column(String(50))
    realAddr=Column(String(50))
    bytesRev=Column(BIGINT())
    bytesSent=Column(BIGINT())
    connectedSince=Column(String(100))
    connectedTo=Column(DateTime())

class MonitorActivity(Base):
    __tablename__="MonitorActivity"

    id=Column(Integer,primary_key=True)
    lastSeen=Column(DateTime())



engine = create_engine(config["connstr"])
print(config["connstr"])
Base.metadata.create_all(engine)


if __name__=="__main__":
    cs=ClientSession(id=1,commName="aa")
    print(cs)

