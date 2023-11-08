import mysql.connector

if __name__ == "__main__":
    conn = mysql.connector.connect(
        host="10.211.55.4",
        user="root", 
        password="123456")
    cursor = conn.cursor()
    cursor.execute("use test")
    sql = '''
    CREATE TABLE IF NOT EXISTS pfc_mesh(
        id int unsigned auto_increment,
        type varchar(6) not NULL,
        time bigint,
        node int unsigned,
        indev int unsigned,
        qindex int unsigned,
        primary key (id)
    )
    '''
    try:
        cursor.execute(sql)
    except:
        print('error in creating table')
    
    file = "../simulation/mix/pcn/dcqcn_out/pfc_dcqcn_mesh.txt"
    f = open(file, mode='r')
    for line in f.readlines():
        d = line.replace('\n', '').split(' ')
        # print(d)
        insert_sql="INSERT INTO pfc_mesh(type, time, node, indev, qindex) VALUES('%s', %d, %d, %d, %d)" % (d[0], int(d[1]), int(d[2]), int(d[3]), int(d[4]))
        # print(insert_sql)
        # try:
        cursor.execute(insert_sql)
        conn.commit()
        # except:
        #     conn.rollback()
        #     print('exit')
        #     break
    conn.close()
            
    
