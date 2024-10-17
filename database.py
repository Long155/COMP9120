#!/usr/bin/env python3
import psycopg2

#####################################################
##  Database Connection
#####################################################

'''
Connect to the database using the connection string
'''
def openConnection():
    # connection parameters - ENTER YOUR LOGIN AND PASSWORD HERE
    userid = "y24s2c9120_jlyu0662"
    passwd = "pYj7CD26"
    myHost = "awsprddbs4836.shared.sydney.edu.au"


    # Create a connection to the database
    conn = None
    try:
        # Parses the config file and connects using the connect string
        conn = psycopg2.connect(database=userid,
                                    user=userid,
                                    password=passwd,
                                    host=myHost)

    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)
    
    # return the connection to use
    return conn

'''
Validate staff based on username and password
'''
def checkLogin(login, password):
    conn = openConnection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT UserName, FirstName, LastName, Email
            FROM Administrator
            WHERE UserName = %s AND Password = %s
        """, (login, password))

        result = cursor.fetchone()
        if result:
            return {
                'login': result[0],
                'FirstName': result[1],
                'LastName': result[2],
                'Email': result[3]
            }
        else:
            return None
    except psycopg2.Error as e:
        print("Error checking login: ", e)
        return None
    finally:
        cursor.close()
        conn.close()


'''
List all the associated admissions records in the database by staff
'''
def findAdmissionsByAdmin(login):

    conn = openConnection()  # 打开数据库连接  
    cursor = conn.cursor()  
    
    try:  
        # 调用存储过程  
        cursor.callproc('find_admissions_by_admin', (login,))  
        
        # 获取结果  
        records = cursor.fetchall()  # 获取所有结果  
        return records  # 返回结果  
    except psycopg2.Error as e:  
        print("Error fetching admissions by admin: ", e)  
        return None  # 返回 None 表示发生错误  
    finally:  
        cursor.close()  # 关闭游标  
        conn.close()  # 关闭连接  


'''
Find a list of admissions based on the searchString provided as parameter
See assignment description for search specification
'''
def findAdmissionsByCriteria(searchString):
    conn = openConnection()  
    cursor = conn.cursor()  
    
    try:  

        # 调用存储过程  
        cursor.callproc('search_admissions', (searchString,))  
        
        # 获取结果  
        records = cursor.fetchall()  
        return records  
    except psycopg2.Error as e:  
        print("Error searching admissions: ", e)  
        return None  
    finally:  
        cursor.close()  
        conn.close()  


'''
Add a new addmission 
'''
def addAdmission(admission_type_name, department_name, patient, condition, admin):  
    conn = openConnection()  # 打开数据库连接  
    cursor = conn.cursor()  
    
    try:  
        # 查询 AdmissionType 的 ID  
        cursor.execute("SELECT AdmissionTypeID FROM AdmissionType WHERE TAdmissionTypeName = %s", (admission_type_name,))  
        admission_type_id = cursor.fetchone()  
        if admission_type_id is None:  
            raise ValueError("Invalid Admission Type")  

        # 查询 Department 的 ID  
        cursor.execute("SELECT DeptID FROM Department WHERE DeptName = %s", (department_name,))  
        department_id = cursor.fetchone()  
        if department_id is None:  
            raise ValueError("Invalid Department")  

        # 转换 patient 参数为小写字母  
        patient_lower = patient.lower()  

        # 调用存储过程，插入新的入院记录  
        cursor.execute("CALL add_admission(%s, %s, %s, %s, %s)",   
                       (admission_type_id[0], department_id[0], patient_lower, admin, condition))  
        conn.commit()  # 提交事务  
        return True  # 成功  
    except psycopg2.Error as e:  
        print("Error adding admission: ", e)  
        conn.rollback()  # 回滚事务  
        return False  # 失败  
    except ValueError as ve:  
        print(ve)  # 打印自定义错误信息  
        return False  # 失败  
    finally:  
        cursor.close()  # 关闭游标  
        conn.close()  # 关闭连接  


'''
Update an existing admission 
'''
def updateAdmission(id, type, department, dischargeDate, fee, patient, condition): #可进一步增加容错性
    conn = openConnection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE Admission
            SET AdmissionType = %s, Department = %s, DischargeDate = %s, Fee = %s, Patient = %s, Condition = %s
            WHERE AdmissionID = %s
        """, (type, department, dischargeDate, fee, patient, condition, id))
        
        conn.commit()
        return cursor.rowcount > 0
    except psycopg2.Error as e:
        print("Error updating admission: ", e)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

