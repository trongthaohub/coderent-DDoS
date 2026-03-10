# ⚡ coderent-Resilience: HardStresser.org API Edition ⚡

[ **English** | [**Tiếng Việt**](#tiếng-viet) ]

**coderent-Resilience** is a professional network performance and stress-testing tool. It is designed to help system administrators and security researchers evaluate server stability by simulating high-traffic scenarios via the **HardStresser.org API**. Featuring a modern terminal interface inspired by the "China Tech UI" aesthetic.

---

## 🚀 Key Features (English)
*   **💎 API Integration**: Simulate traffic through multiple HardStresser accounts simultaneously.
*   **📂 Session Management**: Auto-load credentials and manage active testing sessions.
*   **⏳ Smart Cooldown**: Automated status tracking (Ready/Busy) to optimize testing cycles.
*   **📱 Multi-Platform**: Optimized for Windows, Linux, and Android (Termux).

## 📘 HardStresser Setup & Integration
1. **Sign Up**: Create an account at [HardStresser.org](https://hardstresser.org).
2. **Add Accounts**:
   - **Automatic**: Create a file named `accounts.txt` in the root folder. Add accounts as `username:password` (one per line).
   - **Manual**: Enter credentials interactively when prompted after running the tool.
3. **Optimization**: For free tier accounts, we recommend a **60s** duration per test for maximum API stability.

## 🛰️ Installation & Setup

### 💻 Windows/Linux (PC & VPS)
```bash
git clone https://github.com/trongthaohub/coderent-DDoS.git
cd coderent-DDoS
pip install requests colorama cloudscraper undetected-chromedriver httpx urllib3
python main.py
```

### 📱 Android (Termux)
```bash
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/trongthaohub/coderent-DDoS.git
cd coderent-DDoS
pip install requests colorama cloudscraper httpx urllib3
python main.py
```

---

<a name="tiếng-viet"></a>
# ⚡ coderent-Resilience: Phiên bản API HardStresser.org ⚡

**coderent-Resilience** là công cụ kiểm thử hiệu năng và độ ổn định hạ tầng mạng chuyên nghiệp. Được thiết kế dành cho các quản trị viên hệ thống để đo lường giới hạn chịu tải của máy chủ thông qua **API HardStresser.org**.

## 🚀 Tính năng nổi bật (Tiếng Việt)
*   **💎 Tích hợp API**: Kiểm thử hiệu năng thông qua một hoặc nhiều tài khoản HardStresser cùng lúc.
*   **📂 Quản lý phiên**: Tự động lưu và quản lý thông tin đăng nhập linh hoạt.
*   **⏳ Cooldown thông minh**: Theo dõi trạng thái tài khoản tự động để tối ưu hóa quá trình kiểm thử.
*   **📱 Đa nền tảng**: Chạy mượt mà trên Windows, Linux và Android (Termux).

## 📘 Hướng dẫn thiết lập & Tích hợp HardStresser
1. **Đăng ký**: Truy cập [HardStresser.org](https://hardstresser.org) để tạo tài khoản.
2. **Thêm tài khoản**:
   - **Tự động**: Tạo file `accounts.txt` trong thư mục gốc. Nhập định dạng `user:pass` (mỗi dòng 1 acc).
   - **Thủ công**: Nhập trực tiếp khi tool yêu cầu lúc bắt đầu khởi chạy.
3. **Lưu ý**: Khuyến khích đặt thời gian test là **60s** để đạt độ ổn định cao nhất cho tài khoản API.

## 📋 Hướng dẫn cài đặt
### 💻 Máy tính (Windows/Linux) & 📱 Android (Termux)
*(Vui lòng tham khảo các lệnh cài đặt ở phần tiếng Anh bên trên)*

---

## 🛠 Supported Methods / Phương thức hỗ trợ
| Layer 7 (Application) | Layer 4 (Network) |
| :--- | :--- |
| `CLOUDFLARE`, `RAW` | `UDP`, `TCP`, `DNS` |
| `HTTP`, `HTTPS`, `TLS` | `LDAP`, `NTP`, `STUN` |

---

⚖️ **Disclaimer / Miễn trừ trách nhiệm:**
This tool is for educational and authorized stress-testing purposes only. The developers are not responsible for any misuse.
Công cụ này được cung cấp cho mục đích giáo dục và kiểm thử hạ tầng được cấp phép. Chúng tôi không chịu trách nhiệm cho các hành vi sử dụng trái phép.

**Developed with ❤️ by the coderent Team.**

