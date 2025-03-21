from member.user import Member
from member.dao_db import MemberDao
import streamlit as st

class MemberService:

    loginId=''

    # 로그인된 사용자의 이름을 출력하고, 로그인되지 않은 경우 메시지를 보내는 기능
    def login_user(self,print1=True,print2=True):
        if MemberService.loginId=='':
            if print2:
                st.write('로그인 후 이용하세요')
            return MemberService.loginId
        else:
            a = self.dao.select(MemberService.loginId)
            if print1:
                st.write(a.User_Name+'님:smile:')
            return a.User_Name

    def __init__(self):
        self.dao=MemberDao()

    # 입력받은 정보를 db에 추가하는 기능
    def addMember(self,User_Id, User_Pw, User_Name, User_Email, User_Phone):
        a=Member(User_Id=User_Id,User_Pw=User_Pw,User_Name=User_Name,User_Email=User_Email,User_Phone=User_Phone)
        self.dao.insert(a)

    # 입력받은 User_Id로 정보를 출력하는 기능
    def getById(self,User_Id):
        a:Member=self.dao.select(User_Id=User_Id)
        if a==None:
            st.error('없는 아이디 입니다.', icon="🚨")
        else:
            st.write(a)

    # 입력받은 User_Id의 정보를 삭제하는 기능
    def delMember(self,User_Id):
        if MemberService.loginId !='':
            self.dao.delete(User_Id=User_Id)
            MemberService.loginId = ''
        else:
            st.error('로그인 하세요', icon="🚨")
            return

    # 입력받은 User_Id, User_Pw로 로그인 기능
    def login(self,User_Id,User_Pw):
        if MemberService.loginId!='':
            st.error('이미 로그인 중 입니다. ', icon="🚨")
            return
        a=self.dao.select(User_Id=User_Id)
        if a==None:
            st.error('없는 아이디 입니다. 회원가입 하세요', icon="🚨")
            return
        else:
            if User_Pw==a.User_Pw:
                MemberService.loginId=User_Id
                st.success('로그인 되었습니다.', icon="✅")
                return 1
            else:
                st.error('비밀번호들 다시 입력하세요', icon="🚨")
                return

    # 로그아웃 기능
    def logout(self):
        if MemberService.loginId=='':
            st.error('로그인 먼저 하세요', icon="🚨")
            return
        MemberService.loginId=''
        st.success('로그아웃 완료!', icon="✅")




