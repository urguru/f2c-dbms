from app import mysql
from random import randint

def generate_farmer_id():
    curr=mysql.connection.cursor()
    id=randint(0,99999)
    curr.execute('SELECT * FROM FARMER WHERE idFarmer= {}'.format(id))
    data=curr.fetchall()
    while data:
        id = randint(0, 99999)
        curr.execute('SELECT * FROM FARMER WHERE idFarmer= {}'.format(id))
        data = curr.fetchall()
    curr.close()
    return id
print(generate_farmer_id())