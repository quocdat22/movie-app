# **Supabase Authentication với Python: Hướng dẫn nâng cao cho Lập trình viên Senior**

Tài liệu này tập trung vào việc sử dụng thư viện supabase-py để triển khai các luồng xác thực phức tạp và an toàn trong môi trường backend, với các ví dụ cụ thể cho FastAPI. Chúng ta sẽ không đề cập đến các API cơ bản như sign\_up hay sign\_in một cách chi tiết, mà thay vào đó là các pattern và cân nhắc về mặt kiến trúc.

## **1\. Khởi tạo Client: Service Role vs. Anon Key**

Một lập trình viên senior cần phải hiểu rõ sự khác biệt và trường hợp sử dụng của hai chế độ khởi tạo client:

* **Anonymous (Anon) Key**: Sử dụng cho các hoạt động từ phía client hoặc từ backend thay mặt cho một người dùng cụ thể. Client này sẽ tuân thủ các quy tắc Row Level Security (RLS).  
* **Service Role Key**: Sử dụng **CHỈ** ở môi trường backend an toàn. Client này có quyền truy cập tối cao, bỏ qua tất cả các quy tắc RLS. Đây là chìa khóa để thực hiện các tác vụ quản trị.

\# Ví dụ: config.py  
import os  
from supabase import create\_client, Client

SUPABASE\_URL \= os.environ.get("SUPABASE\_URL")  
SUPABASE\_ANON\_KEY \= os.environ.get("SUPABASE\_ANON\_KEY")  
SUPABASE\_SERVICE\_KEY \= os.environ.get("SUPABASE\_SERVICE\_KEY")

\# Client với quyền quản trị cao nhất, chỉ dùng ở backend.  
\# Nên được khởi tạo một lần và tái sử dụng (singleton).  
supabase\_admin: Client \= create\_client(SUPABASE\_URL, SUPABASE\_SERVICE\_KEY)

## **2\. Tích hợp với FastAPI**

Sử dụng hệ thống Dependency Injection của FastAPI là cách tiếp cận hiệu quả và gọn gàng nhất để quản lý client Supabase và xác thực người dùng.

### **Dependency để xác thực người dùng**

Chúng ta sẽ tạo một dependency để lấy token từ header Authorization, xác thực nó và trả về thông tin người dùng.

\# Ví dụ: dependencies.py  
from fastapi import Depends, HTTPException, status  
from fastapi.security import OAuth2PasswordBearer  
from gotrue.errors import AuthApiError  
from gotrue.types import User  
from supabase import create\_client

from .config import SUPABASE\_URL, SUPABASE\_ANON\_KEY, supabase\_admin

oauth2\_scheme \= OAuth2PasswordBearer(tokenUrl="token")

def get\_user\_from\_token(jwt: str) \-\> User:  
    """Xác thực JWT và trả về thông tin người dùng."""  
    try:  
        \# Khởi tạo client tạm thời chỉ để xác thực  
        client \= create\_client(SUPABASE\_URL, SUPABASE\_ANON\_KEY)  
        user\_response \= client.auth.get\_user(jwt)  
        return user\_response.user  
    except AuthApiError as e:  
        raise HTTPException(  
            status\_code=status.HTTP\_401\_UNAUTHORIZED,  
            detail=f"Invalid authentication credentials: {e}",  
            headers={"WWW-Authenticate": "Bearer"},  
        )

async def get\_current\_user(token: str \= Depends(oauth2\_scheme)) \-\> User:  
    """Dependency để lấy người dùng hiện tại từ token."""  
    return get\_user\_from\_token(token)

### **Sử dụng trong các Route**

Giờ đây, bạn có thể bảo vệ các endpoint của mình một cách dễ dàng.

\# Ví dụ: main.py  
from fastapi import FastAPI, Depends  
from gotrue.types import User

from .dependencies import get\_current\_user  
from .config import supabase\_admin

app \= FastAPI()

@app.get("/users/me")  
async def read\_users\_me(current\_user: User \= Depends(get\_current\_user)):  
    """Endpoint được bảo vệ, chỉ user đã đăng nhập mới truy cập được."""  
    return current\_user

@app.get("/admin/users")  
async def list\_all\_users(current\_user: User \= Depends(get\_current\_user)):  
    """Endpoint quản trị, yêu cầu quyền admin (logic kiểm tra quyền cần được thêm vào)."""  
    \# Logic kiểm tra vai trò 'admin' của current\_user.user\_metadata  
    if not current\_user.user\_metadata.get("is\_admin"):  
         raise HTTPException(status\_code=403, detail="Not an admin")

    \# Sử dụng client admin để thực hiện tác vụ  
    response \= supabase\_admin.auth.admin.list\_users()  
    return response.users

## **3\. Quản lý Session và JWT ở Backend**

(Nội dung không thay đổi)

## **4\. Luồng Xác thực Nâng cao từ Backend**

(Nội dung không thay đổi)

## **5\. Quản lý Người dùng (Admin Tasks)**

(Nội dung không thay đổi)

## **6\. Khôi phục mật khẩu qua Email (Server-Side Flow)**

Đây là một tác vụ phổ biến cần được xử lý an toàn từ backend.

### **Bước 1: Gửi Email khôi phục**

Tạo một endpoint để người dùng yêu cầu reset mật khẩu. Backend sẽ gọi Supabase để gửi email chứa link khôi phục.

\# Trong file main.py hoặc một router riêng  
from pydantic import BaseModel, EmailStr

class PasswordResetRequest(BaseModel):  
    email: EmailStr

@app.post("/auth/password-reset")  
async def request\_password\_reset(body: PasswordResetRequest):  
    """  
    Bắt đầu quy trình khôi phục mật khẩu.  
    API này không cần xác thực.  
    """  
    try:  
        \# Sử dụng client anon key để gửi yêu cầu  
        \# redirect\_to là trang trên frontend của bạn để người dùng nhập mật khẩu mới  
        client \= create\_client(SUPABASE\_URL, SUPABASE\_ANON\_KEY)  
        client.auth.reset\_password\_for\_email(  
            email=body.email,  
            options={'redirect\_to': 'https://your-app.com/update-password'}  
        )  
        return {"message": "Nếu email tồn tại, một liên kết khôi phục mật khẩu đã được gửi."}  
    except AuthApiError as e:  
        \# Không nên báo lỗi chi tiết để tránh dò quét email  
        print(f"Password reset attempt for {body.email} resulted in: {e}")  
        return {"message": "Nếu email tồn tại, một liên kết khôi phục mật khẩu đã được gửi."}

**Lưu ý quan trọng:** Người dùng sẽ nhận được một email có link dạng https://your-app.com/update-password\#access\_token=...\&refresh\_token=.... Frontend của bạn sẽ phải lấy access\_token từ URL fragment này.

### **Bước 2: Cập nhật mật khẩu mới**

Sau khi người dùng nhấp vào link và được chuyển hướng đến trang của bạn, frontend sẽ gửi access\_token (lấy từ URL) cùng với mật khẩu mới lên một endpoint backend để hoàn tất việc cập nhật.

\# Trong file main.py hoặc một router riêng  
class UpdatePasswordRequest(BaseModel):  
    new\_password: str

@app.post("/auth/update-password")  
async def update\_password(  
    body: UpdatePasswordRequest,  
    current\_user: User \= Depends(get\_current\_user) \# Sử dụng dependency để xác thực token  
):  
    """  
    Cập nhật mật khẩu của người dùng bằng token từ email.  
    Token được truyền qua header Authorization.  
    """  
    try:  
        \# Khi đã có user object từ get\_current\_user, ta có thể dùng admin client để cập nhật  
        response \= supabase\_admin.auth.admin.update\_user\_by\_id(  
            user\_id=current\_user.id,  
            attributes={'password': body.new\_password}  
        )  
        return {"message": "Mật khẩu đã được cập nhật thành công.", "user\_id": response.id}  
    except AuthApiError as e:  
        raise HTTPException(status\_code=status.HTTP\_400\_BAD\_REQUEST, detail=str(e))

## **7\. Các Vấn đề Cần Lưu ý**

(Tên mục được đổi từ 5 thành 7, nội dung không thay đổi)

* **Row Level Security (RLS)**  
* **Error Handling**  
* **Lưu trữ Token**  
* **Custom Claims**

Tài liệu này cung cấp một cái nhìn tổng quan về các khía cạnh nâng cao khi làm việc với Supabase Auth trong Python, đặc biệt là trong môi trường FastAPI. Việc hiểu rõ khi nào nên sử dụng service\_role và cách quản lý các luồng xác thực phức tạp từ backend là chìa khóa để xây dựng các ứng dụng an toàn và có khả năng mở rộng.