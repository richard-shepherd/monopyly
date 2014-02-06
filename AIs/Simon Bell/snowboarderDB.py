###########################################################
## File        : SnowboarderDB.py
## Description : 

import sqlite3 as sql

# Class Dependencies

class SnowboarderDB():

# Class Attributes


# Constructor

    def __init__(self):

# Instance Attributes

        self.Connection=sql.connect(':memory:')

# Class Initialisation

        self.CreatePropertySet()
        self.CreateProperty()
        return

# Operations

    def CreatePropertySet(self):
        try:
            Cursor=self.Connection.cursor() 
            Cursor.execute("create table PropertySet(PropertySetName text,Value int)")
            Cursor.execute("insert into PropertySet values ('Brown',1)")
            Cursor.execute("insert into PropertySet values ('Light blue',2)")
            Cursor.execute("insert into PropertySet values ('Purple',3)")
            Cursor.execute("insert into PropertySet values ('Orange',4)")
            Cursor.execute("insert into PropertySet values ('Red',5)")
            Cursor.execute("insert into PropertySet values ('Yellow',6)")
            Cursor.execute("insert into PropertySet values ('Green',7)")
            Cursor.execute("insert into PropertySet values ('Dark blue',8)")
            Cursor.close()
        except Exception as err:
            print("Exception thrown: "+str(err))
        return

    def CreateProperty(self):
        try:
            Cursor=self.Connection.cursor() 
            Cursor.execute("create table Property(PropertyName text,Owned int,DealAttempts int,PropertySetName text,Value int,SingleProperty float,CompleteSet float,House1 float,House2 float,House3 float,House4 float,Hotel float,Cost float,Mortgage float,Site float,BuildHouse1 float,BuildHouse2 float,BuildHouse3 float,BuildHouse4 float,BuildHotel float)")
            Cursor.execute("insert into Property values ('Old Kent Road',0,0,'Brown',1,1494.5282,370.8991,415.1467,124.544,41.5147,35.584,27.6764,60,30,2,10,30,90,160,250)")
            Cursor.execute("insert into Property values ('Whitechapel Road',0,0,'Brown',2,736.4116,295.4227,204.5588,61.3676,20.4559,17.5336,18.8823,60,30,4,20,60,180,320,450)")
            Cursor.execute("insert into Property values ('The Angel Islington',0,0,'Light blue',3,781.8495,178.4163,130.3083,39.0925,13.0308,18.0427,15.637,100,50,6,30,90,270,400,550)")
            Cursor.execute("insert into Property values ('Euston Road',0,0,'Light blue',4,761.9564,177.3596,126.9927,38.0978,12.6993,17.5836,15.2391,100,50,6,30,90,270,400,550)")
            Cursor.execute("insert into Property values ('Pentonville Road',0,0,'Light blue',5,691.8736,198.0109,96.0936,38.4374,11.5312,15.375,15.375,120,60,8,40,100,300,450,600)")
            Cursor.execute("insert into Property values ('Pall Mall',0,0,'Purple',6,547.7404,137.3005,130.4144,39.1243,13.0414,22.3568,31.2995,140,70,10,50,150,450,625,750)")
            Cursor.execute("insert into Property values ('Whitehall',0,0,'Purple',7,643.9566,142.6429,153.323,45.9969,15.3323,26.2839,36.7975,140,70,10,50,150,450,625,750)")
            Cursor.execute("insert into Property values ('Northumberland Avenue',0,0,'Purple',8,549.7065,151.64,114.5222,34.3567,12.8837,20.614,20.614,160,80,12,60,180,500,700,900)")
            Cursor.execute("insert into Property values ('Bow Street',0,0,'Orange',9,479.7082,112.8324,88.8348,28.7005,10.6602,18.6553,18.6553,180,90,14,70,200,550,750,950)")
            Cursor.execute("insert into Property values ('Marlborough Street',0,0,'Orange',10,455.7593,111.4549,84.3999,27.2677,10.128,17.724,17.724,180,90,14,70,200,550,750,950)")
            Cursor.execute("insert into Property values ('Vine Street',0,0,'Orange',11,444.5587,119.7646,74.0931,25.4034,9.3591,17.7823,17.7823,200,100,16,80,220,600,800,1000)")
            Cursor.execute("insert into Property values ('Strand',0,0,'Red',12,467.5215,109.9014,106.2549,35.861,12.7506,32.7872,32.7872,220,110,18,90,250,700,875,1050)")
            Cursor.execute("insert into Property values ('Fleet Street',0,0,'Red',13,476.1134,110.3696,108.2076,36.5201,12.9849,33.3898,33.3898,220,110,18,90,250,700,875,1050)")
            Cursor.execute("insert into Property values ('Trafalgar Square',0,0,'Red',14,400.9446,112.6859,83.5301,25.059,11.1373,28.6389,28.6389,240,120,20,100,300,750,925,1100)")
            Cursor.execute("insert into Property values ('Leicester Square',0,0,'Yellow',15,465.834,115.2667,89.5835,26.875,12.5798,33.7858,33.7858,260,130,22,110,330,800,975,1150)")
            Cursor.execute("insert into Property values ('Coventry Street',0,0,'Yellow',16,469.1373,115.4679,90.2187,27.0656,12.669,34.0253,34.0253,260,130,22,110,330,800,975,1150)")
            Cursor.execute("insert into Property values ('Piccadilly',0,0,'Yellow',17,478.5081,122.6644,85.4479,25.6344,12.5556,35.1557,35.1557,280,140,22,120,360,850,1025,1200)")
            Cursor.execute("insert into Property values ('Regent Street',0,0,'Green',18,457.2156,114.7708,101.6035,30.481,15.5394,39.6253,45.2861,300,150,26,130,390,900,1100,1275)")
            Cursor.execute("insert into Property values ('Oxford Street',0,0,'Green',19,466.7445,115.362,103.721,31.1163,15.8632,40.4512,46.2299,300,150,26,130,390,900,1100,1275)")
            Cursor.execute("insert into Property values ('Bond Street',0,0,'Green',20,485.6852,122.2951,90.4201,28.3316,15.4536,42.4975,42.4975,320,160,28,150,450,1000,1200,1400)")
            Cursor.execute("insert into Property values ('Park Lane',0,0,'Dark blue',21,485.5496,130.4382,92.4856,29.88,16.185,48.555,48.555,350,175,35,175,500,1100,1300,1500)")
            Cursor.execute("insert into Property values ('Mayfair',0,0,'Dark blue',22,322.1658,124.8429,80.5414,20.1354,10.0677,26.8471,26.8471,400,200,50,200,600,1400,1700,2000)")
            Cursor.close()
        except Exception as err:
            print("Exception thrown: "+str(err))
        return

    def Query(self,selection,source,criteria,sort):
        try:
            Cursor=self.Connection.cursor() 
            sql='select '+selection+' from '+source+(' where '+criteria if len(criteria)>0 else '')+(' order by '+sort if len(sort)>0 else '')
            Cursor.execute(sql)
            results=Cursor.fetchall()
            return results
        except Exception as err:
            print("Exception thrown: "+str(err))
        return

    def UpdateOwnership(self,propertyNames):
        try:
            Cursor=self.Connection.cursor() 
            for propertyName in propertyNames:
                sql='update Property set Owned=1 where PropertyName=\''+propertyName+'\''
                Cursor.execute(sql)
        except Exception as err:
            print("Exception thrown: "+str(err))
        return

    def UpdateDealAttempts(self,propertyName):
        try:
            Cursor=self.Connection.cursor() 
            sql='update Property set DealAttempts=DealAttempts+1 where PropertyName=\''+propertyName+'\''
            Cursor.execute(sql)
        except Exception as err:
            print("Exception thrown: "+str(err))
        return

    def FindMissingProperties(self):
        try:
            Cursor=self.Connection.cursor() 
            sql=\
            """
            select
                P.PropertyName
            from
                Property P
            where
                P.PropertySetName
                in
                (
                select
                    PS.PropertySetName
                from
                    PropertySet PS
                    left outer join Property P1 on P1.PropertySetName=PS.PropertySetName
                    left outer join Property P2 on P2.PropertySetName=PS.PropertySetName and P2.Owned=1 and P2.PropertyName=P1.PropertyName
                group by
                    PS.PropertySetName
                having
                    count(P2.Owned)>0
                order by
                    (count(P1.Owned)-count(P2.Owned)),
                    PS.Value desc
                )
                and
                P.Owned=0
            order by
                P.Value desc
            """
            Cursor.execute(sql)
            results=Cursor.fetchall()
            return results
        except Exception as err:
            print("Exception thrown: "+str(err))
        return

