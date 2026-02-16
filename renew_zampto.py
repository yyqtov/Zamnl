import time
from seleniumbase import SB

# ================= 配置区域 =================
USERNAME = "xxxx@xxxx.gmail.com"
PASSWORD = "mypassword"
LOCAL_PROXY = "http://127.0.0.1:8080"
# ===========================================

def run_zampto():
    print(f"🔧 [Zampto-Renew] 启动浏览器")
    
    with SB(uc=True, test=True, proxy=LOCAL_PROXY) as sb:
        print("🚀 浏览器已启动")

        # --- 0. 验证 IP ---
        print("[-] 正在验证代理 IP...")
        try:
            sb.open("https://api.ipify.org/?format=json")
            current_ip = sb.get_text("body")
            print(f"✅ 当前出口 IP: {current_ip}")
        except:
            print("⚠️ IP 验证超时，跳过")

        # --- 1. 访问登录页 ---
        login_url = "https://auth.zampto.net/sign-in?app_id=bmhk6c8qdqxphlyscztgl"
        print(f"[-] 访问登录页: {login_url}")
        sb.uc_open_with_reconnect(login_url, 20)
        
        if sb.is_element_visible('iframe[src*="cloudflare"]'):
            sb.uc_gui_click_captcha()

        # --- 2. 输入账号 ---
        print("[-] 输入账号...")
        sb.type('input[name="identifier"]', USERNAME)
        sb.click('button[type="submit"]')

        # --- 3. 检查跳转 (密码页) ---
        print("[-] 等待跳转到密码页...")
        try:
            sb.wait_for_element_visible('input[name="password"]', timeout=15)
            print("✅ 已跳转到密码页")
        except:
            print("❌ 未跳转到密码页")
            sb.save_screenshot("step3_fail.png")
            return

        # --- 4. 输入密码 ---
        print("[-] 输入密码...")
        sb.type('input[name="password"]', PASSWORD)
        sb.click('button[name="submit"]')
        
        time.sleep(2)
        if sb.is_element_visible('iframe[src*="cloudflare"]'):
            sb.uc_gui_click_captcha()

        # --- 5. 检查跳转 (首页) ---
        print("[-] 等待跳转 Homepage...")
        is_logged_in = False
        for i in range(30):
            if "/homepage" in sb.get_current_url():
                print(f"✅ 登录成功！当前 URL: {sb.get_current_url()}")
                is_logged_in = True
                break
            time.sleep(1)
        
        if not is_logged_in:
            print("❌ 登录失败，未跳转 homepage")
            sb.save_screenshot("step5_fail.png")
            return

        # --- 6. 点击 View Server ---
        print("[-] 寻找服务器按钮 (id=2711)...")
        target_server_selector = 'a.server-btn[href*="id=2711"]'
        
        try:
            sb.wait_for_element_visible(target_server_selector, timeout=15)
            sb.click(target_server_selector)
            print("✅ 点击了 View Server")
        except:
            print(f"❌ 未找到服务器按钮")
            sb.save_screenshot("step6_fail.png")
            return

        # --- 7. 检查跳转 (服务器详情页) ---
        print("[-] 等待跳转服务器详情页...")
        server_page_loaded = False
        for i in range(20):
            if "id=2711" in sb.get_current_url():
                print("✅ 已进入服务器详情页")
                server_page_loaded = True
                break
            time.sleep(1)

        # --- 8. 点击 Renew Server ---
        print("[-] 寻找 Renew 按钮...")
        renew_xpath = "//span[contains(., 'Renew Server')]"
        
        try:
            sb.wait_for_element_visible(renew_xpath, timeout=10)
            sb.click(renew_xpath)
            print("✅ 已点击 Renew Server，等待弹窗...")
            time.sleep(3) 
        except:
            print("❌ 超时未找到 Renew Server 按钮")
            sb.save_screenshot("step8_fail.png")
            return

        # --- 9. 处理弹窗里的 Cloudflare (核心修复) ---
        print("[-] 正在处理弹窗验证...")
        
        # 🟢 只做一件事：点击验证码
        sb.uc_gui_click_captcha()
        
        # 🟢 绝对不去找什么 Confirm 按钮了，直接死等
        print("⏳ 验证码已点击，等待 5 秒让系统自动提交...")
        time.sleep(5)

        # --- 10. 验证结果 ---
        print("[-] 刷新页面获取最新时间...")
        sb.refresh()
        
        try:
            sb.wait_for_element_visible("#nextRenewalTime", timeout=15)
            time_text = sb.get_text("#nextRenewalTime")
            print(f"⏱️ 页面显示的剩余时间: [{time_text}]")
            
            if "1 day 23h" in time_text or "2 days" in time_text:
                print("🎉🎉🎉 验证成功！续期已生效！")
                sb.save_screenshot("zampto_success_final.png")
            else:
                print(f"⚠️ 警告：时间似乎未重置 (当前显示: {time_text})")
                sb.save_screenshot("zampto_warning.png")
        except Exception as e:
            print(f"❌ 读取时间失败: {e}")
            sb.save_screenshot("zampto_verify_error.png")

if __name__ == "__main__":
    run_zampto()
