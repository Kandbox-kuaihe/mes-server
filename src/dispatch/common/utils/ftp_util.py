import os
import ftplib
import tempfile

from dispatch.log import getLogger


logger = getLogger(__name__)


class FTPTool:
    def __init__(self, host, user, password, port=21):
        """
        初始化 FTP 连接
        :param host: FTP 服务器地址
        :param user: FTP 用户名
        :param password: FTP 用户密码
        :param port: FTP 服务器端口，默认为 21
        """
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.ftp = None

    def __enter__(self):
        try:
            self.ftp = ftplib.FTP()
            self.ftp.connect(self.host, self.port, timeout=5)
            self.ftp.login(self.user, self.password)
            logger.info("Connected to FTP server success.")
            return self
        except Exception as e:
            logger.error(f"Connected to FTP server failed: {e}")
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.ftp:
            try:
                self.ftp.quit()
                logger.info("Disconnected from FTP server success.")
            except Exception as e:
                logger.error(f"Disconnected from FTP server failed: {e}")
    
    def _create_directory_if_not_exists(self, directory):
        """
        检查并创建 FTP 服务器上的目录
        :param directory: 要检查和创建的目录路径
        """
        try:
            self.ftp.cwd(directory)
        except ftplib.error_perm:
            parts = directory.strip('/').split('/')
            current_dir = ''
            for part in parts:
                current_dir = f"{current_dir}/{part}" if current_dir else f"/{part}"
                try:
                    self.ftp.cwd(current_dir)
                except ftplib.error_perm:
                    self.ftp.mkd(current_dir)
                    self.ftp.cwd(current_dir)

    def upload_file(self, local_file_path, remote_file_path):
        """
        上传本地文件到 FTP 服务器
        :param local_file_path: 本地文件的路径
        :param remote_file_path: FTP 服务器上的目标文件路径
        :return: 上传成功返回 True, 失败返回 False
        """
        if not self.ftp:
            logger.warning("There is no FTP connection.")
            return False
        try:
            remote_directory = os.path.dirname(remote_file_path)
            if remote_directory:
                self._create_directory_if_not_exists(remote_directory)

            with open(local_file_path, 'rb') as file:
                self.ftp.storbinary(f'STOR {remote_file_path}', file)
            logger.info(f"File: {local_file_path} upload to {remote_file_path} success.")
            return True
        except Exception as e:
            logger.error(f"Upload fail to {remote_file_path} failed: {e}")
            return False

    def download_file(self, remote_file_path):
        """
        从 FTP 服务器下载文件到本地
        :param remote_file_path: FTP 服务器上的文件路径
        :param local_file_path: 本地保存文件的路径
        :return: 下载成功返回 True, 失败返回 False
        """
        if not self.ftp:
            logger.warning("There is no FTP connection.")
            return False
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_path = temp_file.name
                self.ftp.retrbinary(f'RETR {remote_file_path}', temp_file.write)
            logger.info(f"File: {remote_file_path} download to {temp_file_path} success.")
            return temp_file_path
        except Exception as e:
            logger.error(f"Download from {remote_file_path}: {e}")
            return None

    def check_file_change(self, remote_file_path):
        """
        检查远程文件是否发生变化
        :param remote_file_path: FTP 服务器上的文件路径
        :return: 返回文件最近改动时间
        """
        if not self.ftp:
            logger.warning("[Check file change] There is no FTP connection.")
            return False
        try:
            # 获取远程文件的最后修改时间
            modify_time = self.ftp.sendcmd(f'MDTM {remote_file_path}').split()[1]
            return modify_time
        except ftplib.error_perm as e:
            logger.error(f"Check file change failed: {e}")
