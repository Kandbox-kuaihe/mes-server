from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from dispatch.database import get_db
from dispatch.SOPsendFTP.test1 import SRM_COHTRAN8,BBMSTKTFR,MFSO2SOP
import ftplib
import io
import datetime
router = APIRouter()

@router.post("/COHTRAN8")
def MessageCOHTRAN8(*, db: Session = Depends(get_db)):
    content = SRM_COHTRAN8(db_session=db, id=3)
    print(content)
    # 将这段文本以换行的字节形式存到一个 BytesIO 中，相当于“内存里的文件”
    # content = content + '\n'
    # file_like_object = io.BytesIO(content.encode("utf-8")) 
    # file_like_object.seek(0)   
    # #使用 ftplib 上传到 FTP
    # ftp = ftplib.FTP("10.11.12.81", "ftpuser", "ftpuser")
    # #  storbinary 适用于二进制上传，这里传入 BytesIO 对象即可
    # filename = f"/hproot/srm/ftpibm/COHTRAN8test.txt"
    # # 执行上传
    # try:
    #     ftp.storbinary("APPE "+filename , file_like_object)
    #     print("Append operation completed successfully.")
    # except ftplib.all_errors as e:
    #     print("An error occurred while appending the file:")
    #     print(e)
    # ftp.quit()

    return {"status": "success", "message": "Uploaded memory content to FTP!"}

@router.post("/MFSO2SOP")
def MessageMFSO2SOP(*, db: Session = Depends(get_db)):
    content = MFSO2SOP(db_session=db, id=3)
    print(content)
    # 将这段文本以换行的字节形式存到一个 BytesIO 中，相当于“内存里的文件”
    # content = content + '\n'
    # file_like_object = io.BytesIO(content.encode("utf-8")) 
    # file_like_object.seek(0)   
    # #使用 ftplib 上传到 FTP
    # ftp = ftplib.FTP("10.11.12.81", "ftpuser", "ftpuser")
    # #  storbinary 适用于二进制上传，这里传入 BytesIO 对象即可
    # filename = f"/hproot/srm/ftpibm/COHTRAN8test.txt"
    # # 执行上传
    # try:
    #     ftp.storbinary("APPE "+filename , file_like_object)
    #     print("Append operation completed successfully.")
    # except ftplib.all_errors as e:
    #     print("An error occurred while appending the file:")
    #     print(e)
    # ftp.quit()

    return {"status": "success", "message": "Uploaded memory content to FTP!"}


@router.post("/BBMSTKTFR")
def MessageBBMTRAN1(*, db: Session = Depends(get_db)):
    content = BBMSTKTFR(db_session=db, id=3)
    print(content)


    # 将这段文本以换行的字节形式存到一个 BytesIO 中，相当于“内存里的文件”
    content = content + '\n'
    file_like_object = io.BytesIO(content.encode("utf-8")) 
    file_like_object.seek(0)   
    #使用 ftplib 上传到 FTP
    ftp = ftplib.FTP("10.11.12.81", "ftpuser", "ftpuser")
    #  storbinary 适用于二进制上传，这里传入 BytesIO 对象即可
    filename = f"/hproot/srm/ftpibm/BBMSTKTFRtest.txt"
    # 执行上传
    try:
        ftp.storbinary("APPE "+filename , file_like_object)
        print("Append operation completed successfully.")
    except ftplib.all_errors as e:
        print("An error occurred while appending the file:")
        print(e)
    ftp.quit()

    return {"status": "success", "message": "Uploaded memory content to FTP!"}