import streamlit as st
import sqlite3
from member.user import Member

class MemberDao:
    # 한번만 실행
    con=sqlite3.connect('mydb.db')
    cur=con.execute("""
    create table if not exists User(
    User_Id char(15) primary key,
    User_Pw char(20),
    User_Name char(45),
    User_Email char(100),
    User_Phone char(20))
    """)

    # User테이블에 입력받은 정보를 삽입하는 메서드
    def insert(self, a:Member):
        con=sqlite3.connect('mydb.db')
        cur=con.cursor()
        cur.execute(f'INSERT INTO User (User_Id, User_Pw, User_Name, User_Email, User_Phone) VALUES("{a.User_Id}","{a.User_Pw}","{a.User_Name}","{a.User_Email}","{a.User_Phone}")')
        con.commit()
        cur.close()
        con.close()

    # User테이블에 입력받은 User_Id에 해당하는 인스턴스를 검색하는 메서드
    def select(self,User_Id):
        con = sqlite3.connect('mydb.db')
        cur = con.cursor()
        try:
            cur.execute(f'select * from User where User_Id="{User_Id}"')
            user_info=cur.fetchone()
            if user_info:
                return Member(user_info[0],user_info[1],user_info[2],user_info[3],user_info[4])
        except Exception as e:
            st.write(e)
        finally:
            cur.close()
            con.close()

    # User테이블에 입력받은 User_Id에 해당하는 인스턴스를 삭제하는 메서드
    def delete(self, User_Id:str):
        con = sqlite3.connect('mydb.db')
        cur = con.cursor()
        try:
            cur.execute(f'delete from User where User_Id="{User_Id}"')
            con.commit()
            return st.write('삭제가 완료되었습니다.')
        except Exception as e:
            st.write(e)
        finally:
            cur.close()
            con.close()

    # User테이블에 입력받은 정보로 수정하는 메서드
    def update(self, a:Member):
        con = sqlite3.connect('mydb.db')
        cur = con.cursor()
        try:
            cur.execute(f'update User set User_Name="{a.User_Name}", User_Email="{a.User_Email}", User_Phone="{a.User_Phone}"')
            con.commit()
            return st.write('수정 완료되었습니다.')
        except Exception as e:
            st.write(e)
        finally:
            cur.close()
            con.close()