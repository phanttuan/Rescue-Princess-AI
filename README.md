# Rescue-Princess-AI
Đồ án cuối kì môn Trí tuệ nhân tạo Trường Đại học Sư phạm kỹ thuật TP. HCM 
**Nhóm sinh viên thực hiện:**
23110225 - Nguyễn Lâm Huy
23110278 - Bùi Phúc Nhân
23110355 - Phan Việt Tuấn

# Rescue the Princess

**Rescue the Princess** là một trò chơi giải đố phiêu lưu được phát triển bằng Python và Pygame, nơi bạn sẽ dẫn dắt một hiệp sĩ vượt qua mê cung nguy hiểm, tránh quái vật, giải cứu công chúa và tìm đường thoát hiểm. Trò chơi hỗ trợ cả chế độ người chơi và AI, với nhiều mức độ khó và các thuật toán AI khác nhau.

---

## Mục lục

- [Tính năng](#tính-năng)
- [Cài đặt](#cài-đặt)
- [Cách chơi](#cách-chơi)
- [Chế độ AI & Thống kê](#chế-độ-ai--thống-kê)
- [Quản lý bản đồ](#quản-lý-bản-đồ)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Đóng góp](#đóng-góp)

---

## Tính năng

- **Chế độ chơi người & AI:** Chọn chơi thủ công hoặc để AI tự động giải mê cung.
- **Nhiều mức độ khó:** Dễ (hiển thị toàn bộ bản đồ), Khó (ẩn bản đồ, chỉ hiển thị vùng đã khám phá).
- **Thuật toán AI:** Hỗ trợ nhiều thuật toán tìm đường (A*, BFS, DFS, v.v.).
- **Quản lý bản đồ:** Dễ dàng thêm, chỉnh sửa bản đồ mê cung qua file `maps.txt`.
- **Bảng điểm & Thống kê AI:** Lưu lại thành tích người chơi và AI, hiển thị chi tiết số liệu AI (tỉ lệ thắng, số bước, thời gian, v.v.).
- **Giao diện đẹp, hiện đại:** Bố cục hợp lý, dễ nhìn, hỗ trợ độ phân giải 1280x720.

---

## Cài đặt

### Yêu cầu

- Python 3.8+
- Pygame

### Cài đặt thư viện

```bash
pip install pygame
```

### Chạy trò chơi

```bash
python main.py
```

---

## Cách chơi

- **Di chuyển:** Sử dụng các phím mũi tên để di chuyển hiệp sĩ trong mê cung.
- **Mục tiêu:** Tìm và giải cứu công chúa (ô số 2), sau đó dẫn cả hai đến cửa thoát hiểm (ô số 3).
- **Tránh quái vật:** Nếu chạm vào quái vật, bạn sẽ thua cuộc.
- **Chế độ dễ:** Toàn bộ bản đồ, vị trí công chúa và cửa thoát hiểm đều hiển thị.
- **Chế độ khó:** Chỉ vùng đã khám phá mới hiển thị, tăng độ thử thách.

---

## Chế độ AI & Thống kê

- **Chọn AI:** Tại menu chính, chọn "AI PLAY" và thuật toán mong muốn.
- **Thống kê AI:** Nhấn nút "AI STATS" ở menu chính để xem thống kê chi tiết:
  - Thuật toán, số lần chơi, số bước trung bình, thời gian trung bình, có cứu được công chúa hay không.
- **Lưu điểm:** Kết quả AI lưu ở `ai_score.txt`, người chơi lưu ở `player_scores.txt`.

---

## Quản lý bản đồ

- **File bản đồ:** Tất cả bản đồ nằm trong `maps.txt`.
- **Cấu trúc:** Mỗi bản đồ gồm tên (dòng đầu), tiếp theo là 16 dòng ma trận 16x16 (1: tường, 0: đường đi, 2: công chúa, 3: cửa thoát).
- **Thêm bản đồ:** Thêm tên bản đồ mới và ma trận vào cuối file 'maps.txt'.

---

## Cấu trúc dự án

```
Rescue-Princess/
│           # Thuật toán AI
├── game.py              # Khởi chạy game
├── maps.txt             # Danh sách bản đồ mê cung
├── player_scores.txt      # Bảng điểm người chơi
├── ai_score.txt         # Bảng điểm AI
├── images              # Hình ảnh
├── sounds              # Âm thanh
└── README.md            # Giới thiệu
```

---

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo pull request hoặc issue nếu bạn muốn đề xuất tính năng mới, sửa lỗi hoặc cải thiện tài liệu.


**Chúc bạn chơi game vui vẻ và giải cứu công chúa thành công!**
