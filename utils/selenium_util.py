import os
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class WebCrawler:
    def __init__(self, headless: bool = True):
        """
        初始化浏览器驱动
        :param headless: 是否启用无头模式（后台运行，不弹出浏览器窗口）
        """
        self.options = Options()
        if headless:
            self.options.add_argument("--headless=new")  # 推荐使用新版无头模式
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")  # 设置标准分辨率

        #ser =ChromeDriverManager().install()
        #service = Service(ser)
        service = Service('/Users/kangkai/.wdm/drivers/chromedriver/mac64/155.0.8059.84/chromedriver-mac-x64/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=self.options)
        
        # 创建截图保存目录
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)

    def visit_and_screenshot(self, url: str, save_path: str, filename_prefix: str = "page") -> str:
        """
        访问指定网址并截图保存到本地
        :param url: 目标网页地址
        :param filename_prefix: 截图文件名前缀
        :return: 截图文件的完整保存路径
        """
        try:
            # 1. 访问指定地址
            self.driver.get(url)
            
            # 2. 生成带时间戳的文件名，防止覆盖
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{filename_prefix}.png"
            save_path = Path(save_path)
            #file_path = self.screenshot_dir / file_name
            #file_path  = save_path + '/' + file_name
            file_path = save_path / file_name

            # 3. 判断是否有遮罩层，有则尝试关闭
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#login-panel-new"))
                )
                login_close_btns = self.driver.find_elements(by=By.CSS_SELECTOR, value='#login-panel-new .uotczcdY div')
                if(len(login_close_btns) == 2):
                    login_close_btns[1].click()
            except Exception as e1:
                print(f"等待超时，遮罩层元素不存在：{e1}")
            
            # 4. 截取当前页面并保存
            self.driver.save_screenshot(str(file_path))
            print(f"✅ 截图成功！文件已保存至: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"❌ 访问或截图失败: {e}")
            return None

    def close(self):
        """关闭浏览器，释放资源"""
        self.driver.quit()
        print("🔒 浏览器已关闭")

# ================= 运行示例 =================
if __name__ == "__main__":
    # 实例化爬虫类
    crawler = WebCrawler(headless=True)
    
    try:
        # 访问目标地址并截图
        target_url = "https://www.douyin.com/user/MS4wLjABAAAAKrlXFRHBndoSLfgmiitRTdmr0YTSeFJFF3ZFlZXr8KQ"
        crawler.visit_and_screenshot(target_url,save_path=Path("screenshots"), filename_prefix="baidu_home")
        
    finally:
        # 确保无论是否报错，浏览器都能被正常关闭
        crawler.close()