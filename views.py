from django.shortcuts import render
from django.db import connection
from datetime import datetime
from datetime import timedelta
from django.utils.encoding import smart_str
from hashlib import sha1 as sha_constructor
from passlib.hash import pbkdf2_sha256
# Create your views here.

def loginusercheck():
    mycursor = connection.cursor()
    mycursor.execute("select * from LOGGEDINUSER Natural join USER")
    loggedinuser = mycursor.fetchall()
    mycursor.close()
    return loggedinuser

def signin(request):
    mycursor = connection.cursor()
    loggedinuser = loginusercheck()
    if len(loggedinuser)==0:
        if request.method == "POST":
            user = request.POST["username"]
            password = request.POST["password"]
            userType = request.POST["login_user"]
            if userType == 'admin':
                mycursor.execute("select User_id, Password,Fname from USER where User_id = '{0}' and User_type='admin' ".format(user))
            else:
                mycursor.execute("select User_id, Password,Fname from USER where User_id = '{0}' and User_type='user' ".format(user))
            data = mycursor.fetchall()
            if len(data) == 0:
                mycursor.close()
                return render(request, 'signin.html', {'err': ['Email or Password is incorrect']})
            else:
                try:
                    if pbkdf2_sha256.verify(str(password),data[0][1]):
                        if userType == 'admin':
                            mycursor.execute("delete from LOGGEDINUSER")
                            mycursor.execute("insert into LOGGEDINUSER(User_id) values('{}')".format(user))
                            mycursor.close()
                            loggedinuser = loginusercheck()
                            return render(request, 'adminhomebrs.html', {'Name': loggedinuser[0][3].title()})
                        else:
                            mycursor.execute("delete from LOGGEDINUSER")
                            mycursor.execute("insert into LOGGEDINUSER(User_id) values('{}')".format(user))
                            mycursor.close()
                            loggedinuser = loginusercheck()
                            return render(request, 'homebrs.html',{'Name':loggedinuser[0][3].title()})
                    else:
                        mycursor.close()
                        return render(request, 'signin.html', {'err': ['Email or Password is incorrect']})
                except ValueError:
                    mycursor.close()
                    return render(request, 'signin.html', {'err': ['Exception Email or Password is incorrect']})
        else:
            mycursor.close()
            return render(request, 'signin.html')
    else:
        mycursor.close()
        loggedinuser = loginusercheck()
        return render(request, 'homebrs.html',{'Name':loggedinuser[0][3].title()})

def signup(request):
    if request.method=="POST":
        mycursor = connection.cursor()
        userSSN = str(request.POST['user_ssn'])
        userEmail = str(request.POST['email_id'])
        userName = str(request.POST['username'])
        fName = str(request.POST["Fname"])
        lName = str(request.POST["Lname"])
        gen = str(request.POST["gender-user"])
        mycursor.execute("select count(*) from user")
        tUsers = mycursor.fetchall()
        #tUsers = 5000
        #print(tUsers[0][0])
        mycursor.execute("select Ssn, email, User_id from user")
        data = mycursor.fetchall()
        cnt = 1
        pas = str(request.POST['original_password'])
        pas = pbkdf2_sha256.encrypt(pas)
        for i,j,k in data:
            err = []
            #print(userSSN != i ,"  __  ", userEmail!=j ,"  __  ", userName!=k ,"  __  ", cnt==len(data))
            #print("GENDER:  ",gen)
            if userSSN == i:
                err.append(userSSN)
                userSSN = ''
            if userEmail == j:
                err.append(userEmail)
                userEmail = ''
            if userName == k:
                err.append(userName)
                userName = ''
            if tUsers[0][0] >= 5000:
                err.append("Max. Limit of 5000")
            if err:
                mycursor.close()
                return render(request, 'signup.html', {'con':err, 'errExtra':"Please review the following:", 'fName': fName, 'lName': lName, 'gen':gen, 'userName':userName, 'userEmail': userEmail, 'userSSN':userSSN})
            elif cnt==len(data):
                mycursor.execute("""insert into USER(User_id,Ssn,email,Fname,Lname,Gender,User_type,Password)
                                        VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')""".format(request.POST["username"],
                                                                                          request.POST["user_ssn"],
                                                                                          request.POST["email_id"],
                                                                                          request.POST["Fname"],
                                                                                          request.POST["Lname"],
                                                                                          request.POST["gender-user"],
                                                                                          "user",
                                                                                           pas))
                mycursor.close()
                return render(request, 'signin.html', {'con':['Registration Successfull!']})
            else:
                cnt +=1
        else:
            mycursor.execute("""insert into USER(User_id,Ssn,email,Fname,Lname,Gender,User_type,Password)
                                                    VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')""".format(
                request.POST["username"],
                request.POST["user_ssn"],
                request.POST["email_id"],
                request.POST["Fname"],
                request.POST["Lname"],
                request.POST["gender-user"],
                "user",
                pas))
    else:
        return render(request, 'signup.html')

def signout(request):
    mycursor = connection.cursor()
    mycursor.execute("delete from LOGGEDINUSER")
    mycursor.close()
    return render(request, 'signin.html', {'con':['Logged out!']})

def about(request):
    return render(request, 'about.html')

def reset(request):
    if request.method=="POST":
        mycursor = connection.cursor()
        userSSN = str(request.POST['user_ssn'])
        mycursor.execute("select Ssn from user where User_type='user'")
        data = mycursor.fetchall()
        cnt = 1
        for ssnT in data:
            if userSSN in ssnT:
                mycursor.close()
                return render(request, 'reset_confirm.html', {'uSSN': userSSN})
            elif cnt == len(data):
                mycursor.close()
                return render(request, 'reset.html', {'err':['SSN is not Registered!']})
            else:
                cnt +=1
    else:
        return render(request, 'reset.html')

def resetNew(request):
    if request.method=="POST":
        mycursor = connection.cursor()
        userNP = str(request.POST['original_password'])
        userNPC = str(request.POST['confirm_password'])
        userSSN = str(request.POST['user_ssn'])
        pas = str(request.POST['original_password'])
        pas = pbkdf2_sha256.encrypt(pas)
        if userSSN.strip():
            mycursor.execute("update user set Password = '{0}' where Ssn='{1}'".format(pas, request.POST['user_ssn']))
            mycursor.close()
            return render(request, 'signin.html', {'con':['Reset Sucessfully!']})
        else:
            mycursor.close()
            return render(request, 'signin.html', {'err':['SSN cannot be reset like That!']})
    else:
        return render(request, 'reset_confirm.html', {'err':['Try Again!!']})

def homebrs(request):
    usercheck = loginusercheck()
    if len(usercheck) ==0:
        return render(request, 'signin.html')
    else:
        return render(request, 'homebrs.html',{'Name':usercheck[0][3]})

def adminhomebrs(request):
    usercheck = loginusercheck()
    if len(usercheck) == 0:
        return render(request, 'signin.html')
    else:
        return render(request, 'adminhomebrs.html',{'Name':usercheck[0][3]})


def addbus(request):
    usercheck = loginusercheck()
    if len(usercheck) == 0:
        return render(request, 'signin.html')
    else:
        mycursor = connection.cursor()
        mycursor.execute("select distinct(City_name) from CITY")
        City_name = mycursor.fetchall()
        mycursor.execute("select distinct(Bus_id) from BUS")
        Bus_ids = mycursor.fetchall()

        mycursor.execute("""select available from Bus where bus_id = '{0}'
                            """.format(request.GET["bus_id"]))
        avail = mycursor.fetchall()

        mycursor.execute("""
                                select count(bus_id) from(
                                select distinct bus_id from bus where Available = true
                                union
                                select distinct additional_busid as bus_id from additionalbus
                                ) as buses
                            """)
        total = mycursor.fetchall()

        if(total[0][0]>=200):
            mycursor.close()
            return render(request, 'addbus.html',
                          {"City_name": City_name, "Bus_id": Bus_ids, 'msg': "Limit(200) reached, cannot add new buses!",
                           'Name': usercheck[0][3]})

        if(not(avail[0][0])):
            mycursor.execute("""update bus
                                set available = true
                                where bus_id = '{0}'""".format(request.GET["bus_id"]))
        else:
            mycursor.execute("select additional_busid from additionalbus where bus_id = {0}".format(request.GET["bus_id"]))
            addi_bus = mycursor.fetchall()
            dups = set()
            for tup in addi_bus:
                dups.add(tup[0])

            new_bus = ""
            bus_id = request.GET["bus_id"]
            for i in ('A','B','C','D','E'):
                if(bus_id+i not in dups):
                    new_bus = bus_id+i
                    break

            mycursor.execute("""insert into additionalbus
                                values('{0}','{1}')
            """.format(bus_id,new_bus))

        mycursor.close()
        return render(request, 'addbus.html', {"City_name": City_name, "Bus_id": Bus_ids,'msg':"New bus successfully added" ,'Name': usercheck[0][3]})


def adminBusAdd(request):
    usercheck = loginusercheck()
    if len(usercheck) == 0:
        return render(request, 'signin.html')
    else:
        if request.method == 'POST':
            mycursor = connection.cursor()
            mycursor.execute("select distinct(City_name) from CITY")
            City_name = mycursor.fetchall()
            mycursor.execute("select distinct(Bus_id) from BUS")
            Bus_id = mycursor.fetchall()
            Source = str(request.POST['Source'])
            Destination = str(request.POST['Destination'])
            Source = Source.strip(' ')
            Source = Source.replace(" ", "[[:space:]]*")
            Destination = Destination.strip(' ')
            Destination = Destination.replace(" ", "[[:space:]]*")
            Source = "^[[:space:]]*" + Source + "[[:space:]]*$"
            Destination = "^[[:space:]]*" + Destination + "[[:space:]]*$"

            if request.POST["Bus_id"]=="----":
                mycursor.execute("""select avail_bus.bus_id,Bus_name,Departure_time,Arrival_time,ifnull(count(additional_busid),0) as duplicates
                from
                (select a.bus_id,a.Bus_name,a.Arrival_time,a.Departure_time
                 from(select distinct(available_buses.Bus_id),Bus.Bus_name,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                 Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time
                 from(Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time
                 from (select distinct(bus_id),City_id,stop_order,Departure_time from STOPS
                 where city_id in (select city_id from CITY where City_name regexp '{0}'))as Source,
                 (select distinct(bus_id),City_id,stop_order,Arrival_time from STOPS
                 where city_id in (select city_id from CITY where City_name regexp '{1}'))as Destination
                 where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order)as available_buses
                 natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id) as a,STOPS as s,stops as d
                 where s.Bus_id = a.Bus_id and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id)as avail_bus Left outer join additionalbus on avail_bus.bus_id = additionalbus.bus_id group by bus_id
                                                        """.format(Source, Destination))
            else:
                mycursor.execute("""select avail_bus.bus_id,Bus_name,Departure_time,Arrival_time,ifnull(count(additional_busid),0) as duplicates
                               from
                               (select a.bus_id,a.Bus_name,a.Arrival_time,a.Departure_time
                                from(select distinct(available_buses.Bus_id),Bus.Bus_name,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time
                                from(Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time
                                from (select distinct(bus_id),City_id,stop_order,Departure_time from STOPS
                                where city_id in (select city_id from CITY where City_name regexp '{0}'))as Source,
                                (select distinct(bus_id),City_id,stop_order,Arrival_time from STOPS
                                where city_id in (select city_id from CITY where City_name regexp '{1}'))as Destination
                                where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order)as available_buses
                                natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id) as a,STOPS as s,stops as d
                                where s.Bus_id = a.Bus_id and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id)as avail_bus Left outer join additionalbus on avail_bus.bus_id = additionalbus.bus_id
                                where avail_bus.bus_id = '{2}' group by bus_id
                                                                       """.format(Source, Destination,request.POST["Bus_id"]))
            data = mycursor.fetchall()

            mycursor.close()
            return render(request, 'addbus.html', {"City_name": City_name,"bus_num":request.POST["Bus_id"],"source":request.POST['Source'],"destination":request.POST['Destination'] ,"Bus_id": Bus_id,'msg':"","msg1":"Sorry No buses available in this route",'Name': usercheck[0][3],'buses':data})
        else:
            mycursor = connection.cursor()
            mycursor.execute("select distinct(City_name) from CITY")
            City_name = mycursor.fetchall()
            mycursor.execute("select distinct(Bus_id) from BUS")
            Bus_id = mycursor.fetchall()
            mycursor.close()
            return render(request, 'addbus.html',{"City_name":City_name,"Bus_id":Bus_id,"msg":"",'Name':usercheck[0][3]})
	
def adminUserDelete(request):
    usercheck = loginusercheck()
    if len(usercheck) == 0:
        return render(request, 'signin.html')
    else:
        if request.method=='POST':
            UserId = request.POST["deleteUserId"]
            msg = ""
            mycursor = connection.cursor()
            mycursor.execute("select * from user where user_id = '{0}'".format(UserId))
            list1 =mycursor.fetchall()
            if(len(list1)==0):
                msg = "Entered User Id doesnot exist!"
            else:
                mycursor.execute("delete from user where user_id ='{0}'".format(UserId))
                msg = "Bus successfully deleted"
            return render(request, 'adminUserDelete.html', {'Name': usercheck[0][3],"msg":msg})
        else:
            return render(request, 'adminUserDelete.html',{'Name':usercheck[0][3],"msg":""})

def adminSQL(request):
    usercheck = loginusercheck()
    if len(usercheck) == 0:
        return render(request, 'signin.html')
    else:
        if request.method=='POST':
            sqlQuery = request.POST["sqlQuery"]
            msg = ""
            mycursor = connection.cursor()
            try: 
                mycursor.execute(str(sqlQuery))
                list1 =mycursor.fetchall()
            except Exception as e:
                return render(request, 'adminSQL.html', {'Name': usercheck[0][3],"msg":"This query cannot be performed"})
            return render(request, 'adminSQL.html', {'Name': usercheck[0][3],"msg":msg,"data":list1})
        else:
            return render(request, 'adminSQL.html',{'Name':usercheck[0][3],"msg":""})

def adminBusDelete(request):
    usercheck = loginusercheck()
    if len(usercheck) == 0:
        return render(request, 'signin.html')
    else:
        if request.method=='POST':
            busid = request.POST["deleteBusId"]
            msg = ""
            mycursor = connection.cursor()
            mycursor.execute("select * from bus where bus_id = '{0}'".format(busid))
            list1 =mycursor.fetchall()
            if(len(list1)==0):
                mycursor.execute("select * from additionalbus where additional_busid = '{0}'".format(busid))
                list2 = mycursor.fetchall()
                if(len(list2)==0):
                    msg = "Entered BusId doesnot exist!"
                else:
                    mycursor.execute("delete from additionalbus where additional_busid='{0}'".format(busid))
                    mycursor.execute("""
                                                        delete from ticket
                                                        where bus_id = '{0}'
                                                        """.format(busid))
                    msg = "Bus successfully deleted"
            else:
                mycursor.execute("""update bus
                                    set available = false
                                    where bus_id='{0}'""".format(busid))
                mycursor.execute("""
                                    delete from ticket
                                    where bus_id = '{0}'
                                    """.format(busid))
                msg = "Bus successfully deleted"

            return render(request, 'adminbusDelete.html', {'Name': usercheck[0][3],"msg":msg})
        else:
            return render(request, 'adminbusDelete.html',{'Name':usercheck[0][3],"msg":""})

def bookinghistory(request):
    usercheck = loginusercheck()
    if len(usercheck) == 0:
        return render(request, 'signin.html')
    else:
        mycursor = connection.cursor()
        mycursor.execute(""" SELECT distinct t1.Ticket_id, t1.start_date, t1.Source, t2.Destination, t1.Bus_id, t1.Bus_name, t1.Passenger_count FROM
        (SELECT Ticket_id, start_date, t.Bus_id, b.Bus_name, City_name as Source, Passenger_count
        FROM TICKET t, BUS b,additionalbus a, City c
        where (b.Bus_id = t.Bus_id or (t.bus_id = a.additional_busid and a.bus_id=b.bus_id)) and t.source_id = c.city_id and  User_id = '{0}') t1
        NATURAL JOIN
        (SELECT Ticket_id, start_date, t.Bus_id, b.Bus_name, City_name as Destination, Passenger_count
        FROM TICKET t, BUS b,additionalbus a , City c
        where (b.Bus_id = t.Bus_id or (t.bus_id = a.additional_busid and a.bus_id=b.bus_id)) and t.destination_id = c.city_id and  User_id = '{0}') t2
        order by start_date DESC""".format(usercheck[0][0]))
        data = mycursor.fetchall()
        mycursor.close()
        return render(request, 'bookinghistory.html',{'Name':usercheck[0][3],'data':data})
	
def upcomingtrips(request):
    usercheck = loginusercheck()
    if len(usercheck) == 0:
        return render(request, 'signin.html')
    else:
        mycursor = connection.cursor()
        mycursor.execute("""SELECT distinct t1.Ticket_id, t1.Start_date, t1.Bus_id, t1.Bus_name, t1.Source, t2.Destination,  t1.Departure_time, t2.Arrival_time, t1.Passenger_count  FROM
    (SELECT distinct Ticket_id, Start_date, t.Bus_id, b.Bus_name, City_name as Source, Passenger_count, Departure_time
            FROM TICKET t, BUS b,additionalbus a, stops s, city c
            where (b.Bus_id = t.Bus_id or (t.bus_id = a.additional_busid and b.bus_id=a.bus_id)) and t.Source_id = c.City_id and (t.Bus_id = s.Bus_id or (t.bus_id = a.additional_busid and a.bus_id=s.bus_id)) and t.Source_id = s.City_id and User_id = '{0}') t1
    NATURAL JOIN
    (SELECT distinct Ticket_id, Start_date, t.Bus_id, b.Bus_name, City_name as Destination, Passenger_count, Arrival_time
            FROM TICKET t, BUS b, additionalbus a , stops s, city c
            where (b.Bus_id = t.Bus_id or (t.bus_id = a.additional_busid and a.bus_id=b.bus_id)) and t.Destination_id = c.City_id and (t.Bus_id = s.Bus_id or (t.bus_id = a.additional_busid and a.bus_id=s.bus_id)) and t.Destination_id = s.City_id and User_id = '{0}') t2
            where t1.Start_date>NOW() order by Start_date""".format(usercheck[0][0]))
        data = mycursor.fetchall()
        mycursor.close()
        return render(request, 'upcomingtrips.html', {'Name': usercheck[0][3], 'data': data})
	
def bus_schedule(request):
    usercheck = loginusercheck()
    if len(usercheck) == 0:
        return render(request, 'signin.html')
    else:
        if request.method != 'POST':
            mycursor = connection.cursor()
            mycursor.execute("""select bus_id from bus
                                union
                                select additional_busid from additionalbus
                                order by bus_id;
                                """)
            buses = mycursor.fetchall()
            mycursor.close()
            return render(request, 'bus_schedule.html',{'Name':usercheck[0][3],'bus_id':'',"buses":buses})
        else:
            mycursor = connection.cursor()
            mycursor.execute("""select bus_id from bus
                                            union
                                            select additional_busid from additionalbus
                                            order by bus_id;
                                            """)
            buses = mycursor.fetchall()
            mycursor.execute("""SELECT City_name as City, Arrival_time,
                             Departure_time  FROM STOPS s, CITY c
                             where s.City_id = c.City_id
                             and (s.Bus_id = '{0}' or s.Bus_id =(SELECT Bus_id FROM additionalbus where additional_Busid = '{0}'))
                             order by stop_order;
                            """.format(request.POST["Bus_ID"]))
            schedule = mycursor.fetchall()
            zero_time = datetime.strptime("00:00:00", "%H:%M:%S")
            mycursor.close()
            return render(request, 'bus_schedule.html', {'Name': usercheck[0][3], "buses": buses,'schedule':schedule,'bus_id':request.POST["Bus_ID"],'zero_time':zero_time.time()})

def bookticket(request):
    usercheck = loginusercheck()
    if len(usercheck) == 0:
        return render(request, 'signin.html')
    else:
        if request.method == 'POST':
            Source = str(request.POST['Source'])
            Destination = str(request.POST['Destination'])
            Source = Source.strip(' ')
            Source = Source.replace(" ","[[:space:]]*")
            Destination = Destination.strip(' ')
            Destination = Destination.replace(" ", "[[:space:]]*")
            Source = "^[[:space:]]*"+Source+"[[:space:]]*$"
            Destination = "^[[:space:]]*" + Destination + "[[:space:]]*$"
            travel_date = request.POST["traveldate"]
            #print(travel_date)
            mycursor = connection.cursor()

            if (not (request.POST['start_time'] or request.POST['end_time'])):
                if request.POST["Bus_no"] == "----":
                    mycursor.execute("""

            select bus_id,Bus_name,Source,Destination,Departure_time,Arrival_time,ifnull((20-sum(Passenger_count)),20) as Availability
                                from
                                (
                                select avail_bus.bus_id,avail_bus.Bus_name,Source,Destination,avail_bus.Departure_time,avail_bus.Arrival_time,Source_id,Destination_id,Passenger_count,avail_bus.sourceday_number,avail_bus.Destinationday_number
                                from
                                (

                                   select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                   from(
                                           select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                           Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                           from(
                                                   Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number,Destination.Day_number as Destinationday_number
                                                   from (
                                                           select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                           where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                        )
                                                   as Source,
                                                   (
                                                       select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                       where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                   )as Destination

                                                    where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order

                                                )as available_buses
                                            natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                        ) as a,STOPS as s,stops as d
                                    where s.Bus_id = a.Bus_id
                                    and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id and a.Available=true

                                    union

                                    select additional_busid as Bus_id,Bus_name,Source_order,Source,Destination_order,Destination,Arrival_time,Departure_time,a.sourceday_number,a.Destinationday_number
                                    from
                                    (
                                        select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                        from(
                                                select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                                Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                                 from(
                                                         Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number, Destination.Day_number as Destinationday_number
                                                            from (
                                                                    select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                                )as Source,
                                                                (
                                                                    select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                                )as Destination
                                                            where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order
                                                    )as available_buses
                                                natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                            ) as a,STOPS as s,stops as d
                                        where s.Bus_id = a.Bus_id
                                        and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id

                                    )as a natural join additionalbus as b

                                ) as avail_bus Left OUTER JOIN

                                    (select distinct t.user_id,t.Ticket_id,t.Bus_id,s.stop_order as source_stopOrder,s.departure_time as source_time,
                                    Source_id,d.Arrival_time as destination_time,
                                    d.stop_order as Destination_stopOrder,Destination_id,t.Passenger_count,t.start_date,t.end_date from STOPS as s,stops as d,ticket as t, additionalbus as a where ((s.Bus_id = t.Bus_id and d.bus_id = t.bus_id) or (t.bus_id=a.Additional_busid and (a.Bus_id = s.bus_id and d.bus_id = a.bus_id)))
                                    and t.Source_id = s.city_id and t.Destination_id = d.city_id)as booked_tkt

                                    on avail_bus.bus_id = booked_tkt.bus_id AND

                                    (((concat(date'{2}',' ',avail_bus.departure_time)<=concat(booked_tkt.start_date ,' ',booked_tkt.source_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)> concat(booked_tkt.start_date ,' ',booked_tkt.source_time)))

                                    or

                                    ((concat(date'{2}',' ',avail_bus.departure_time)<concat(booked_tkt.end_date,' ',booked_tkt.destination_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)>= concat(booked_tkt.end_date,' ',booked_tkt.destination_time))))

                                    )
                                    as avail


                                group by bus_id;

                                            """.format(Source, Destination, travel_date))
                else:
                    mycursor.execute("""

            select bus_id,Bus_name,Source,Destination,Departure_time,Arrival_time,ifnull((20-sum(Passenger_count)),20) as Availability
                                from
                                (
                                select avail_bus.bus_id,avail_bus.Bus_name,Source,Destination,avail_bus.Departure_time,avail_bus.Arrival_time,Source_id,Destination_id,Passenger_count,avail_bus.sourceday_number,avail_bus.Destinationday_number
                                from
                                (

                                   select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                   from(
                                           select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                           Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                           from(
                                                   Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number,Destination.Day_number as Destinationday_number
                                                   from (
                                                           select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                           where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                        )
                                                   as Source,
                                                   (
                                                       select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                       where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                   )as Destination

                                                    where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order

                                                )as available_buses
                                            natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                        ) as a,STOPS as s,stops as d
                                    where s.Bus_id = a.Bus_id
                                    and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id and a.Available=true

                                    union

                                    select additional_busid as Bus_id,Bus_name,Source_order,Source,Destination_order,Destination,Arrival_time,Departure_time,a.sourceday_number,a.Destinationday_number
                                    from
                                    (
                                        select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                        from(
                                                select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                                Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                                 from(
                                                         Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number, Destination.Day_number as Destinationday_number
                                                            from (
                                                                    select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                                )as Source,
                                                                (
                                                                    select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                                )as Destination
                                                            where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order
                                                    )as available_buses
                                                natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                            ) as a,STOPS as s,stops as d
                                        where s.Bus_id = a.Bus_id
                                        and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id

                                    )as a natural join additionalbus as b

                                ) as avail_bus Left OUTER JOIN

                                    (select distinct t.user_id,t.Ticket_id,t.Bus_id,s.stop_order as source_stopOrder,s.departure_time as source_time,
                                    Source_id,d.Arrival_time as destination_time,
                                    d.stop_order as Destination_stopOrder,Destination_id,t.Passenger_count,t.start_date,t.end_date from STOPS as s,stops as d,ticket as t, additionalbus as a where ((s.Bus_id = t.Bus_id and d.bus_id = t.bus_id) or (t.bus_id=a.Additional_busid and (a.Bus_id = s.bus_id and d.bus_id = a.bus_id)))
                                    and t.Source_id = s.city_id and t.Destination_id = d.city_id)as booked_tkt

                                    on avail_bus.bus_id = booked_tkt.bus_id AND

                                    (((concat(date'{2}',' ',avail_bus.departure_time)<=concat(booked_tkt.start_date ,' ',booked_tkt.source_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)> concat(booked_tkt.start_date ,' ',booked_tkt.source_time)))

                                    or

                                    ((concat(date'{2}',' ',avail_bus.departure_time)<concat(booked_tkt.end_date,' ',booked_tkt.destination_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)>= concat(booked_tkt.end_date,' ',booked_tkt.destination_time))))

                                    )
                                     as avail where bus_id = '{3}' group by bus_id;

                                                                """.format(Source, Destination, travel_date,request.POST["Bus_no"]))
            else:
                if request.POST["Bus_no"] == "----":
                    if (request.POST['start_time'] and not(request.POST['end_time'])):
                        mycursor.execute("""

                                    select bus_id,Bus_name,Source,Destination,Departure_time,Arrival_time,ifnull((20-sum(Passenger_count)),20) as Availability
                                from
                                (
                                select avail_bus.bus_id,avail_bus.Bus_name,Source,Destination,avail_bus.Departure_time,avail_bus.Arrival_time,Source_id,Destination_id,Passenger_count,avail_bus.sourceday_number,avail_bus.Destinationday_number
                                from
                                (

                                   select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                   from(
                                           select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                           Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                           from(
                                                   Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number,Destination.Day_number as Destinationday_number
                                                   from (
                                                           select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                           where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                        )
                                                   as Source,
                                                   (
                                                       select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                       where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                   )as Destination

                                                    where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order

                                                )as available_buses
                                            natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                        ) as a,STOPS as s,stops as d
                                    where s.Bus_id = a.Bus_id
                                    and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id and a.Available=true

                                    union

                                    select additional_busid as Bus_id,Bus_name,Source_order,Source,Destination_order,Destination,Arrival_time,Departure_time,a.sourceday_number,a.Destinationday_number
                                    from
                                    (
                                        select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                        from(
                                                select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                                Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                                 from(
                                                         Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number, Destination.Day_number as Destinationday_number
                                                            from (
                                                                    select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                                )as Source,
                                                                (
                                                                    select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                                )as Destination
                                                            where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order
                                                    )as available_buses
                                                natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                            ) as a,STOPS as s,stops as d
                                        where s.Bus_id = a.Bus_id
                                        and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id

                                    )as a natural join additionalbus as b

                                ) as avail_bus Left OUTER JOIN

                                    (select distinct t.user_id,t.Ticket_id,t.Bus_id,s.stop_order as source_stopOrder,s.departure_time as source_time,
                                    Source_id,d.Arrival_time as destination_time,
                                    d.stop_order as Destination_stopOrder,Destination_id,t.Passenger_count,t.start_date,t.end_date from STOPS as s,stops as d,ticket as t, additionalbus as a where ((s.Bus_id = t.Bus_id and d.bus_id = t.bus_id) or (t.bus_id=a.Additional_busid and (a.Bus_id = s.bus_id and d.bus_id = a.bus_id)))
                                    and t.Source_id = s.city_id and t.Destination_id = d.city_id)as booked_tkt

                                    on avail_bus.bus_id = booked_tkt.bus_id AND

                                    (((concat(date'{2}',' ',avail_bus.departure_time)<=concat(booked_tkt.start_date ,' ',booked_tkt.source_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)> concat(booked_tkt.start_date ,' ',booked_tkt.source_time)))

                                    or

                                    ((concat(date'{2}',' ',avail_bus.departure_time)<concat(booked_tkt.end_date,' ',booked_tkt.destination_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)>= concat(booked_tkt.end_date,' ',booked_tkt.destination_time))))

                                    )
                                    as avail where (Departure_time >= '{3}') group by bus_id;

                                                                    """.format(Source, Destination, travel_date,
                                                                               request.POST['start_time']))
                    elif(not(request.POST['start_time']) and request.POST['end_time']):
                        mycursor.execute("""

                                                        select bus_id,Bus_name,Source,Destination,Departure_time,Arrival_time,ifnull((20-sum(Passenger_count)),20) as Availability
                                from
                                (
                                select avail_bus.bus_id,avail_bus.Bus_name,Source,Destination,avail_bus.Departure_time,avail_bus.Arrival_time,Source_id,Destination_id,Passenger_count,avail_bus.sourceday_number,avail_bus.Destinationday_number
                                from
                                (

                                   select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                   from(
                                           select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                           Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                           from(
                                                   Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number,Destination.Day_number as Destinationday_number
                                                   from (
                                                           select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                           where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                        )
                                                   as Source,
                                                   (
                                                       select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                       where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                   )as Destination

                                                    where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order

                                                )as available_buses
                                            natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                        ) as a,STOPS as s,stops as d
                                    where s.Bus_id = a.Bus_id
                                    and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id and a.Available=true

                                    union

                                    select additional_busid as Bus_id,Bus_name,Source_order,Source,Destination_order,Destination,Arrival_time,Departure_time,a.sourceday_number,a.Destinationday_number
                                    from
                                    (
                                        select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                        from(
                                                select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                                Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                                 from(
                                                         Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number, Destination.Day_number as Destinationday_number
                                                            from (
                                                                    select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                                )as Source,
                                                                (
                                                                    select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                                )as Destination
                                                            where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order
                                                    )as available_buses
                                                natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                            ) as a,STOPS as s,stops as d
                                        where s.Bus_id = a.Bus_id
                                        and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id

                                    )as a natural join additionalbus as b

                                ) as avail_bus Left OUTER JOIN

                                    (select distinct t.user_id,t.Ticket_id,t.Bus_id,s.stop_order as source_stopOrder,s.departure_time as source_time,
                                    Source_id,d.Arrival_time as destination_time,
                                    d.stop_order as Destination_stopOrder,Destination_id,t.Passenger_count,t.start_date,t.end_date from STOPS as s,stops as d,ticket as t, additionalbus as a where ((s.Bus_id = t.Bus_id and d.bus_id = t.bus_id) or (t.bus_id=a.Additional_busid and (a.Bus_id = s.bus_id and d.bus_id = a.bus_id)))
                                    and t.Source_id = s.city_id and t.Destination_id = d.city_id)as booked_tkt

                                    on avail_bus.bus_id = booked_tkt.bus_id AND

                                    (((concat(date'{2}',' ',avail_bus.departure_time)<=concat(booked_tkt.start_date ,' ',booked_tkt.source_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)> concat(booked_tkt.start_date ,' ',booked_tkt.source_time)))

                                    or

                                    ((concat(date'{2}',' ',avail_bus.departure_time)<concat(booked_tkt.end_date,' ',booked_tkt.destination_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)>= concat(booked_tkt.end_date,' ',booked_tkt.destination_time))))

                                    )
                                    as avail where (Departure_time<='{3}') group by bus_id;

                                                                    """.format(Source, Destination, travel_date,
                                                                               request.POST['end_time']))
                    else:
                        mycursor.execute("""
            select bus_id,Bus_name,Source,Destination,Departure_time,Arrival_time,ifnull((20-sum(Passenger_count)),20) as Availability
                                from
                                (
                                select avail_bus.bus_id,avail_bus.Bus_name,Source,Destination,avail_bus.Departure_time,avail_bus.Arrival_time,Source_id,Destination_id,Passenger_count,avail_bus.sourceday_number,avail_bus.Destinationday_number
                                from
                                (

                                   select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                   from(
                                           select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                           Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                           from(
                                                   Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number,Destination.Day_number as Destinationday_number
                                                   from (
                                                           select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                           where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                        )
                                                   as Source,
                                                   (
                                                       select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                       where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                   )as Destination

                                                    where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order

                                                )as available_buses
                                            natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                        ) as a,STOPS as s,stops as d
                                    where s.Bus_id = a.Bus_id
                                    and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id and a.Available=true

                                    union

                                    select additional_busid as Bus_id,Bus_name,Source_order,Source,Destination_order,Destination,Arrival_time,Departure_time,a.sourceday_number,a.Destinationday_number
                                    from
                                    (
                                        select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                        from(
                                                select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                                Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                                 from(
                                                         Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number, Destination.Day_number as Destinationday_number
                                                            from (
                                                                    select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                                )as Source,
                                                                (
                                                                    select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                                )as Destination
                                                            where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order
                                                    )as available_buses
                                                natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                            ) as a,STOPS as s,stops as d
                                        where s.Bus_id = a.Bus_id
                                        and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id

                                    )as a natural join additionalbus as b

                                ) as avail_bus Left OUTER JOIN

                                    (select distinct t.user_id,t.Ticket_id,t.Bus_id,s.stop_order as source_stopOrder,s.departure_time as source_time,
                                    Source_id,d.Arrival_time as destination_time,
                                    d.stop_order as Destination_stopOrder,Destination_id,t.Passenger_count,t.start_date,t.end_date from STOPS as s,stops as d,ticket as t, additionalbus as a where ((s.Bus_id = t.Bus_id and d.bus_id = t.bus_id) or (t.bus_id=a.Additional_busid and (a.Bus_id = s.bus_id and d.bus_id = a.bus_id)))
                                    and t.Source_id = s.city_id and t.Destination_id = d.city_id)as booked_tkt

                                    on avail_bus.bus_id = booked_tkt.bus_id AND

                                    (((concat(date'{2}',' ',avail_bus.departure_time)<=concat(booked_tkt.start_date ,' ',booked_tkt.source_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)> concat(booked_tkt.start_date ,' ',booked_tkt.source_time)))

                                    or

                                    ((concat(date'{2}',' ',avail_bus.departure_time)<concat(booked_tkt.end_date,' ',booked_tkt.destination_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)>= concat(booked_tkt.end_date,' ',booked_tkt.destination_time))))

                                    )
                                    as avail where (Departure_time >= '{3}' and Departure_time<='{4}') group by bus_id;

                                                """.format(Source, Destination, travel_date, request.POST['start_time'],
                                                       request.POST['end_time']))
                else:
                    if (request.POST['start_time'] and not(request.POST['end_time'])):
                        mycursor.execute("""
            select bus_id,Bus_name,Source,Destination,Departure_time,Arrival_time,ifnull((20-sum(Passenger_count)),20) as Availability
                                from
                                (
                                select avail_bus.bus_id,avail_bus.Bus_name,Source,Destination,avail_bus.Departure_time,avail_bus.Arrival_time,Source_id,Destination_id,Passenger_count,avail_bus.sourceday_number,avail_bus.Destinationday_number
                                from
                                (

                                   select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                   from(
                                           select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                           Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                           from(
                                                   Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number,Destination.Day_number as Destinationday_number
                                                   from (
                                                           select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                           where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                        )
                                                   as Source,
                                                   (
                                                       select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                       where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                   )as Destination

                                                    where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order

                                                )as available_buses
                                            natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                        ) as a,STOPS as s,stops as d
                                    where s.Bus_id = a.Bus_id
                                    and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id and a.Available=true

                                    union

                                    select additional_busid as Bus_id,Bus_name,Source_order,Source,Destination_order,Destination,Arrival_time,Departure_time,a.sourceday_number,a.Destinationday_number
                                    from
                                    (
                                        select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                        from(
                                                select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                                Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                                 from(
                                                         Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number, Destination.Day_number as Destinationday_number
                                                            from (
                                                                    select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                                )as Source,
                                                                (
                                                                    select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                                )as Destination
                                                            where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order
                                                    )as available_buses
                                                natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                            ) as a,STOPS as s,stops as d
                                        where s.Bus_id = a.Bus_id
                                        and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id

                                    )as a natural join additionalbus as b

                                ) as avail_bus Left OUTER JOIN

                                    (select distinct t.user_id,t.Ticket_id,t.Bus_id,s.stop_order as source_stopOrder,s.departure_time as source_time,
                                    Source_id,d.Arrival_time as destination_time,
                                    d.stop_order as Destination_stopOrder,Destination_id,t.Passenger_count,t.start_date,t.end_date from STOPS as s,stops as d,ticket as t, additionalbus as a where ((s.Bus_id = t.Bus_id and d.bus_id = t.bus_id) or (t.bus_id=a.Additional_busid and (a.Bus_id = s.bus_id and d.bus_id = a.bus_id)))
                                    and t.Source_id = s.city_id and t.Destination_id = d.city_id)as booked_tkt

                                    on avail_bus.bus_id = booked_tkt.bus_id AND

                                    (((concat(date'{2}',' ',avail_bus.departure_time)<=concat(booked_tkt.start_date ,' ',booked_tkt.source_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)> concat(booked_tkt.start_date ,' ',booked_tkt.source_time)))

                                    or

                                    ((concat(date'{2}',' ',avail_bus.departure_time)<concat(booked_tkt.end_date,' ',booked_tkt.destination_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)>= concat(booked_tkt.end_date,' ',booked_tkt.destination_time))))

                                    )
                                    as avail  where (Departure_time >= '{3}' and bus_id = '{4}') group by bus_id;

                                                                    """.format(Source, Destination, travel_date,
                                                                               request.POST['start_time'],request.POST["Bus_no"]))
                    elif(not(request.POST['start_time']) and request.POST['end_time']):
                        mycursor.execute("""
            select bus_id,Bus_name,Source,Destination,Departure_time,Arrival_time,ifnull((20-sum(Passenger_count)),20) as Availability
                                from
                                (
                                select avail_bus.bus_id,avail_bus.Bus_name,Source,Destination,avail_bus.Departure_time,avail_bus.Arrival_time,Source_id,Destination_id,Passenger_count,avail_bus.sourceday_number,avail_bus.Destinationday_number
                                from
                                (

                                   select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                   from(
                                           select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                           Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                           from(
                                                   Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number,Destination.Day_number as Destinationday_number
                                                   from (
                                                           select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                           where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                        )
                                                   as Source,
                                                   (
                                                       select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                       where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                   )as Destination

                                                    where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order

                                                )as available_buses
                                            natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                        ) as a,STOPS as s,stops as d
                                    where s.Bus_id = a.Bus_id
                                    and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id and a.Available=true

                                    union

                                    select additional_busid as Bus_id,Bus_name,Source_order,Source,Destination_order,Destination,Arrival_time,Departure_time,a.sourceday_number,a.Destinationday_number
                                    from
                                    (
                                        select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                        from(
                                                select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                                Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                                 from(
                                                         Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number, Destination.Day_number as Destinationday_number
                                                            from (
                                                                    select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                                )as Source,
                                                                (
                                                                    select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                                )as Destination
                                                            where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order
                                                    )as available_buses
                                                natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                            ) as a,STOPS as s,stops as d
                                        where s.Bus_id = a.Bus_id
                                        and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id

                                    )as a natural join additionalbus as b

                                ) as avail_bus Left OUTER JOIN

                                    (select distinct t.user_id,t.Ticket_id,t.Bus_id,s.stop_order as source_stopOrder,s.departure_time as source_time,
                                    Source_id,d.Arrival_time as destination_time,
                                    d.stop_order as Destination_stopOrder,Destination_id,t.Passenger_count,t.start_date,t.end_date from STOPS as s,stops as d,ticket as t, additionalbus as a where ((s.Bus_id = t.Bus_id and d.bus_id = t.bus_id) or (t.bus_id=a.Additional_busid and (a.Bus_id = s.bus_id and d.bus_id = a.bus_id)))
                                    and t.Source_id = s.city_id and t.Destination_id = d.city_id)as booked_tkt

                                    on avail_bus.bus_id = booked_tkt.bus_id AND

                                    (((concat(date'{2}',' ',avail_bus.departure_time)<=concat(booked_tkt.start_date ,' ',booked_tkt.source_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)> concat(booked_tkt.start_date ,' ',booked_tkt.source_time)))

                                    or

                                    ((concat(date'{2}',' ',avail_bus.departure_time)<concat(booked_tkt.end_date,' ',booked_tkt.destination_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)>= concat(booked_tkt.end_date,' ',booked_tkt.destination_time))))

                                    )
                                    as avail where (Departure_time<='{3}' and bus_id = '{4}') group by bus_id;

                                                                    """.format(Source, Destination, travel_date,
                                                                               request.POST['end_time'],request.POST["Bus_no"]))
                    else:
                        mycursor.execute("""
            select bus_id,Bus_name,Source,Destination,Departure_time,Arrival_time,ifnull((20-sum(Passenger_count)),20) as Availability
                                from
                                (
                                select avail_bus.bus_id,avail_bus.Bus_name,Source,Destination,avail_bus.Departure_time,avail_bus.Arrival_time,Source_id,Destination_id,Passenger_count,avail_bus.sourceday_number,avail_bus.Destinationday_number
                                from
                                (

                                   select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                   from(
                                           select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                           Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                           from(
                                                   Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number,Destination.Day_number as Destinationday_number
                                                   from (
                                                           select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                           where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                        )
                                                   as Source,
                                                   (
                                                       select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                       where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                   )as Destination

                                                    where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order

                                                )as available_buses
                                            natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                        ) as a,STOPS as s,stops as d
                                    where s.Bus_id = a.Bus_id
                                    and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id and a.Available=true

                                    union

                                    select additional_busid as Bus_id,Bus_name,Source_order,Source,Destination_order,Destination,Arrival_time,Departure_time,a.sourceday_number,a.Destinationday_number
                                    from
                                    (
                                        select a.bus_id,a.Bus_name,s.stop_order as Source_order,a.Source,d.Stop_order as Destination_order,a.Destination,a.Arrival_time,a.Departure_time,a.sourceday_number,a.Destinationday_number
                                        from(
                                                select distinct(available_buses.Bus_id),Bus.Bus_name,Bus.Available,Source_city.City_name as Source,Destination_city.City_name as Destination,Source_city.City_id as Source_id,
                                                Destination_city.City_id as Destination_id,available_buses.Departure_time,available_buses.Arrival_time,available_buses.sourceday_number,available_buses.Destinationday_number
                                                 from(
                                                         Select Source.bus_id,Source.City_id as Source_id,Destination.City_id as Destination_id,Source.Departure_time,Destination.Arrival_time,Source.Day_number as sourceday_number, Destination.Day_number as Destinationday_number
                                                            from (
                                                                    select distinct(bus_id),City_id,stop_order,Departure_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{0}')
                                                                )as Source,
                                                                (
                                                                    select distinct(bus_id),City_id,stop_order,Arrival_time,Day_number from STOPS
                                                                    where city_id in (select city_id from CITY where City_name regexp '{1}')
                                                                )as Destination
                                                            where Source.bus_id=Destination.bus_id AND Source.stop_order<Destination.stop_order
                                                    )as available_buses
                                                natural join Bus join City as Source_city on Source_id=Source_city.City_id join City as Destination_city on Destination_id=Destination_city.City_id
                                            ) as a,STOPS as s,stops as d
                                        where s.Bus_id = a.Bus_id
                                        and d.bus_id = a.bus_id and a.Source_id = s.city_id and a.Destination_id = d.city_id

                                    )as a natural join additionalbus as b

                                ) as avail_bus Left OUTER JOIN

                                    (select distinct t.user_id,t.Ticket_id,t.Bus_id,s.stop_order as source_stopOrder,s.departure_time as source_time,
                                    Source_id,d.Arrival_time as destination_time,
                                    d.stop_order as Destination_stopOrder,Destination_id,t.Passenger_count,t.start_date,t.end_date from STOPS as s,stops as d,ticket as t, additionalbus as a where ((s.Bus_id = t.Bus_id and d.bus_id = t.bus_id) or (t.bus_id=a.Additional_busid and (a.Bus_id = s.bus_id and d.bus_id = a.bus_id)))
                                    and t.Source_id = s.city_id and t.Destination_id = d.city_id)as booked_tkt

                                    on avail_bus.bus_id = booked_tkt.bus_id AND

                                    (((concat(date'{2}',' ',avail_bus.departure_time)<=concat(booked_tkt.start_date ,' ',booked_tkt.source_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)> concat(booked_tkt.start_date ,' ',booked_tkt.source_time)))

                                    or

                                    ((concat(date'{2}',' ',avail_bus.departure_time)<concat(booked_tkt.end_date,' ',booked_tkt.destination_time))and(concat(date(DATE'{2}'+(avail_bus.Destinationday_number-avail_bus.sourceday_number)),' ',avail_bus.arrival_time)>= concat(booked_tkt.end_date,' ',booked_tkt.destination_time))))

                                    )
                                    as avail where (Departure_time >= '{3}' and Departure_time<='{4}' and bus_id = '{5}') group by bus_id;

                                                """.format(Source, Destination, travel_date, request.POST['start_time'],
                                                       request.POST['end_time'],request.POST["Bus_no"]))



            Data = mycursor.fetchall()

            mycursor.execute("select distinct(City_name) from CITY")
            City_name = mycursor.fetchall()
            mycursor.execute("""select bus_id from bus
                                            union
                                            select additional_busid from additionalbus
                                            order by bus_id;
                                            """)
            Bus_id = mycursor.fetchall()
            mycursor.close()
            return render(request, 'bookticket.html', {"date_travel":request.POST["traveldate"],
                                                       "bus_no":request.POST["Bus_no"],
                                                       "End_time":request.POST["end_time"],
                                                       "Start_time":request.POST["start_time"],
                                                       "source_selected":request.POST["Source"],
                                                       "destination_selected":request.POST["Destination"],
                                                       "City_name": City_name, "Bus_id": Bus_id,
                                                       'Name':usercheck[0][3],
                                                       'Available_buses':Data,
                                                       'msg': '',
                                                       'rslt':"Sorry, No buses available in this route"})
        else:
            mycursor = connection.cursor()
            mycursor.execute("select distinct(City_name) from CITY")
            City_name = mycursor.fetchall()
            mycursor.execute("""select bus_id from bus
                                            union
                                            select additional_busid from additionalbus
                                            order by bus_id;
                                            """)
            Bus_id = mycursor.fetchall()
            mycursor.close()
            return render(request, 'bookticket.html',{"date_travel":"------",
                                                      "bus_no":"----",
                                                      "end_time":"------",
                                                      "start_time":"------",
                                                      "source_selected":"",
                                                      "destination_selected":"",
                                                      "City_name":City_name,
                                                      "Bus_id":Bus_id,
                                                      'Name':usercheck[0][3],
                                                      'Available_buses':[],
                                                      'msg':''})


def cancellation(request):
    usercheck = loginusercheck()
    if len(usercheck) == 0:
        return render(request, 'signin.html')
    else:
        if request.method == "POST":
            bus_id = request.POST["bus_id"]
            print("busif" + bus_id)
            source = request.POST["source"]
            ticket_id = request.POST["ticket_id"]
            traveldate = request.POST["traveldate"]
            bus_name = request.POST["bus_name"]
            destination = request.POST["destination"]
            departure_time = request.POST["departure_time"]
            arrival_time = request.POST["arrival_time"]
            passenger_count = request.POST["passenger_count"]

            # mycursor = connection.cursor()
            # mycursor.execute("select Name, Passenger_id from passengers where Ticket_Id='{0}'".format(ticketid))
            # data=mycursor.fetchall()
            for i in ["1", "2", "3", "4"]:
                if i in request.POST:
                    print("wdwdwdwd:-", ticket_id, type(ticket_id))
                    mycursor = connection.cursor()
                    mycursor.execute(
                        "delete from passengers where Passenger_id ='{0}' and Ticket_id ='{1}'".format(i, ticket_id))
                    mycursor.close()

                    mycursor = connection.cursor()
                    mycursor.execute("update ticket set Passenger_count = \
                                         case  when Passenger_count>0 then Passenger_count-1 \
                                            when Passenger_count = 0 then 0 \
                                             end where Ticket_id = '{0}'".format(ticket_id))
                    mycursor.close()

                    mycursor = connection.cursor()

                    mycursor.execute("select Passenger_count from ticket where Ticket_id = '{0}'".format(ticket_id))
                    data = mycursor.fetchall()
                    mycursor.close()
                    print("************************************", data)
                    if (data[0][0] == 0):
                        msg="There are no Upcoming Trips!"
                        mycursor = connection.cursor()
                        mycursor.execute("delete from ticket where Ticket_id ='{0}'".format(ticket_id))
                        mycursor.close()
                        mycursor = connection.cursor()
                        mycursor.execute("""SELECT distinct t1.Ticket_id, t1.Start_date, t1.Bus_id, t1.Bus_name, t1.Source, t2.Destination,  t1.Departure_time, t2.Arrival_time, t1.Passenger_count  FROM
                                                    (SELECT distinct Ticket_id, Start_date, t.Bus_id, b.Bus_name, City_name as Source, Passenger_count, Departure_time
                                                            FROM TICKET t, BUS b,additionalbus a, stops s, city c
                                                            where (b.Bus_id = t.Bus_id or (t.bus_id = a.additional_busid and b.bus_id=a.bus_id)) and t.Source_id = c.City_id and (t.Bus_id = s.Bus_id or (t.bus_id = a.additional_busid and a.bus_id=s.bus_id)) and t.Source_id = s.City_id and User_id = '{0}') t1
                                                    NATURAL JOIN
                                                    (SELECT distinct Ticket_id, Start_date, t.Bus_id, b.Bus_name, City_name as Destination, Passenger_count, Arrival_time
                                                            FROM TICKET t, BUS b, additionalbus a , stops s, city c
                                                            where (b.Bus_id = t.Bus_id or (t.bus_id = a.additional_busid and a.bus_id=b.bus_id)) and t.Destination_id = c.City_id and (t.Bus_id = s.Bus_id or (t.bus_id = a.additional_busid and a.bus_id=s.bus_id)) and t.Destination_id = s.City_id and User_id = '{0}') t2
                                                            where t1.Start_date>NOW() order by Start_date""".format(usercheck[0][0]))
                        data = mycursor.fetchall()
                        mycursor.close()
                        return render(request, 'upcomingtrips.html', {'Name': usercheck[0][3], 'data': data,'msg':msg})

            mycursor = connection.cursor()
            mycursor.execute("select Name, Passenger_id from passengers where Ticket_Id='{0}'".format(ticket_id))
            data = mycursor.fetchall()
            mycursor.close()

            return render(request, "cancellation.html", {'Name': usercheck[0][3],
                                                         'bus_id': bus_id,
                                                         'passengers': data,
                                                         'source': source,
                                                         'ticket_id': ticket_id,
                                                         'traveldate': traveldate,
                                                         'destination': destination,
                                                         'departure_time': departure_time,
                                                         'arrival_time': arrival_time})
        else:
            bus_id = request.GET["bus_id"]
            source = request.GET["source"]
            ticket_id = request.GET["ticket_id"]
            traveldate = request.GET["traveldate"]
            bus_name = request.GET["bus_name"]
            destination = request.GET["destination"]
            departure_time = request.GET["departure_time"]
            arrival_time = request.GET["arrival_time"]
            passenger_count = request.GET["passenger_count"]

            mycursor = connection.cursor()
            mycursor.execute("select Name, Passenger_id from passengers where Ticket_Id='{0}'".format(ticket_id))
            data = mycursor.fetchall()
            mycursor.close();

            return render(request, "cancellation.html", {'Name': usercheck[0][3],
                                                         'passengers': data,
                                                         'bus_id': bus_id,
                                                         'source': source,
                                                         'traveldate': traveldate,
                                                         'destination': destination,
                                                         'bus_id': bus_id,
                                                         'departure_time': departure_time,
                                                         'arrival_time': arrival_time,
                                                         'ticket_id': ticket_id})

def passengerinfo_ticket(request):
    usercheck = loginusercheck()
    if len(usercheck) == 0:
        return render(request, 'signin.html')
    else:
        if request.method=="POST":
            mycursor = connection.cursor()
            avail = int(request.POST["availability"])
            if avail > 4:
                avail = 4

            mycursor.execute("select * from Ticket")

            booked = mycursor.fetchall()
            tkt_id = 1
            if(len(booked)!=0):
                mycursor.execute("select max(ticket_id) from Ticket")
                booked = mycursor.fetchall()
                tkt_id = int(booked[0][0])+1

            passenger_cnt = 0

            Source = str(request.POST['source'])
            Destination = str(request.POST['destination'])
            Source = Source.strip(' ')
            Source = Source.replace(" ", "%")
            Destination = Destination.strip(' ')
            Destination = Destination.replace(" ", "%")
            Source = "%" + Source + "%"
            Destination = "%" + Destination + "%"

            mycursor.execute("select city_id from City where City_name like '{0}'".format(Source))
            sourceid = mycursor.fetchall()

            mycursor.execute("select city_id from City where City_name like '{0}'".format(Destination))
            destinationid = mycursor.fetchall()

            start_date = datetime.strptime(request.POST["traveldate"], "%Y-%m-%d")

            print(request.POST["bus_id"])
            print(sourceid[0][0])

            mycursor.execute("select day_number from stops natural left join additionalbus where (bus_id = '{0}' or additional_busid = '{0}' )  and city_id = '{1}'".format(request.POST["bus_id"],sourceid[0][0]))
            source_day = mycursor.fetchall()

            print(source_day)

            print(request.POST["bus_id"])
            print(destinationid[0][0])
            mycursor.execute("select day_number from stops natural left join additionalbus where (bus_id = '{0}' or additional_busid = '{0}' )  and city_id = '{1}'".format(request.POST["bus_id"],
                                                                                               destinationid[0][0]))
            dest_day = mycursor.fetchall()

            print(dest_day)

            end_date = start_date+timedelta(dest_day[0][0]-source_day[0][0])

            mycursor.execute("""insert into Ticket(User_id,Ticket_id,Bus_id,Source_id,Destination_id,start_date,End_date,Passenger_count)
                                            VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')""".format(usercheck[0][0],
                                                                                                        tkt_id,
                                                                                                        request.POST["bus_id"],
                                                                                                        sourceid[0][0],
                                                                                                        destinationid[0][0],
                                                                                                        start_date.date(),
                                                                                                        end_date.date(),
                                                                                                        passenger_cnt))

            for i in range(1,avail+1):
                if(request.POST["name"+str(i)]!="" and request.POST["age"+str(i)]!="" ):
                    passenger_cnt +=1
                    temp = request.POST["age"+str(i)]
                    temp = temp.strip(' ')
                    print("age: {}".format(temp))
                    mycursor.execute("""insert into passengers(Ticket_id,Passenger_id,Name,Age,Gender)
                                VALUES('{0}','{1}','{2}','{3}','{4}')""".format(tkt_id,passenger_cnt,request.POST["name"+str(i)],
                                                                      int(temp),
                                                                      request.POST["gender"+str(i)]))


            if passenger_cnt==0:
                mycursor.execute("""delete from ticket where ticket_id = '{0}'""".format(tkt_id))
            else:
                mycursor.execute("""update ticket
                                set passenger_count = '{0}'
                                where ticket_id = '{1}'""".format(passenger_cnt,tkt_id))

            mycursor.execute("select distinct(City_name) from CITY")
            City_name = mycursor.fetchall()
            mycursor.execute("select distinct(Bus_id) from BUS")
            Bus_id = mycursor.fetchall()
            mycursor.close()

            msg = ''
            if passenger_cnt>0:
                msg = 'Booking successful!'

            return render(request, 'bookticket.html',
                          {"date_travel": "------", "bus_no": "----", "end_time": "------", "start_time": "------",
                           "source_selected": "", "destination_selected": "", "City_name": City_name, "Bus_id": Bus_id,
                           'Name': usercheck[0][3], 'Available_buses': [],'msg':msg})

        else:
            temp = request.GET["dep_time"]
            temp = temp.replace(".","")
            if(':' not in temp):
                temp = temp.replace(" ",":00 ")

            deptime = datetime.strptime(temp,"%I:%M %p")
            print(deptime.time())
            avail = int(request.GET["availability"])
            if avail > 4:
                avail = 4

            avail1 = []
            for i in range(1,avail+1):
                avail1.append(i)

            return render(request,"passengerinfo_ticket.html",{'Name':usercheck[0][3],'bus_id':request.GET["bus_id"],
                                                           "bus_name":request.GET["bus_name"],
                                                           "source":request.GET["source"],
                                                           "destination":request.GET["destination"],
                                                           "dep_time":request.GET["dep_time"],
                                                           "arr_time":request.GET["arr_time"],
                                                           "traveldate":request.GET["traveldate"],
                                                            "availability":request.GET["availability"],
                                                            "avail":avail1})
