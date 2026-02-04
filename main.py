import flet as ft
from datetime import datetime

# --- CẤU HÌNH ---
DEF_BET = 10
PLAYERS_DEF = ["Người 1", "Người 2", "Người 3", "Người 4"]

def main(page: ft.Page):
    # --- CẤU HÌNH TRANG (FIX LỖI TAI THỎ & MÀN HÌNH TRẮNG) ---
    page.title = "TÁ LẢ PRO"
    page.theme_mode = ft.ThemeMode.LIGHT
    # Màu nền xám nhẹ dịu mắt
    page.bgcolor = "#F0F2F5"
    # QUAN TRỌNG: Padding top=50 để tránh tai thỏ/camera
    page.padding = ft.padding.only(top=50, left=15, right=15, bottom=20)
    # QUAN TRỌNG: Bật scroll AUTO để tránh lỗi màn hình trắng/xám
    page.scroll = ft.ScrollMode.AUTO
    
    # --- BIẾN TOÀN CỤC ---
    state = {
        "bet": DEF_BET,
        "pot": 0,
        "players": [{"name": n, "money": 0} for n in PLAYERS_DEF],
        "history": [],      
        "current_logs": [] 
    }
    
    temp_data = {}

    # --- HÀM TẠO NÚT (TƯƠNG THÍCH MỌI PHIÊN BẢN) ---
    def create_btn(text, action, bg="blue", color="white", expand=True):
        return ft.ElevatedButton(
            content=ft.Container(
                content=ft.Text(text, size=15, weight="bold", color=color, text_align="center"),
                padding=ft.padding.symmetric(vertical=12),
                alignment=ft.alignment.center
            ),
            on_click=action,
            bgcolor=bg,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=0, # Reset padding mặc định của nút
            ),
            # Expand giúp nút tự giãn chiều ngang nếu cần
            width=1000 if expand else None 
        )

    # --- HÀM GHI LỊCH SỬ ---
    def commit_log(title, result_details):
        timestamp = datetime.now().strftime("%H:%M")
        final_details = []
        
        if state["current_logs"]:
            final_details.append("--- Diễn biến ---")
            final_details.extend(state["current_logs"])
            final_details.append("--- Kết quả ---")
            
        final_details.extend(result_details)
        
        state["history"].insert(0, {
            "time": timestamp,
            "title": title,
            "details": final_details
        })
        state["current_logs"] = [] 

    # --- MÀN HÌNH CHÍNH ---
    def view_dashboard():
        page.clean()
        
        # 1. THANH THÔNG TIN (HEADER)
        # Sử dụng Container có bóng đổ nhẹ
        info_card = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("MỨC CƯỢC", size=12, color="grey", weight="bold"),
                    ft.Text(f"{int(state['bet']):,} K", size=22, weight="bold", color="#333333")
                ], alignment="center", horizontal_alignment="center"),
                
                ft.Container(width=1, height=40, bgcolor="#DDDDDD"), # Vạch ngăn
                
                ft.Column([
                    ft.Text("QUỸ GÀ", size=12, color="#F57C00", weight="bold"),
                    ft.Text(f"{int(state['pot']):,} K", size=28, weight="bold", color="#F57C00")
                ], alignment="center", horizontal_alignment="center"),
            ], alignment="spaceEvenly"),
            
            padding=20, border_radius=15, bgcolor="white",
            shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.with_opacity(0.1, "black"))
        )

        # 2. DANH SÁCH NGƯỜI CHƠI
        list_col = ft.Column(spacing=12)
        for p in state["players"]:
            money_val = int(p["money"])
            money_color = "#2E7D32" if money_val >= 0 else "#C62828" # Xanh/Đỏ
            bg_money = "#E8F5E9" if money_val >= 0 else "#FFEBEE"
            
            # Card người chơi
            card = ft.Container(
                content=ft.Row([
                    ft.Row([
                        # Avatar: Dùng ft.Icon("person") an toàn
                        ft.Container(
                            content=ft.Icon("person", size=24, color="white"),
                            padding=10, bgcolor="#90A4AE", border_radius=50
                        ),
                        ft.Column([
                            ft.Text(p["name"], weight="bold", size=16, color="#37474F"),
                            ft.Container(
                                content=ft.Text("✎ Sửa tên", size=12, color="#1976D2"),
                                on_click=lambda e, x=p: goto_rename(x),
                                padding=ft.padding.only(top=2, bottom=2)
                            )
                        ], spacing=2),
                    ]),
                    ft.Container(
                        content=ft.Text(f"{money_val:,} k", color=money_color, weight="bold", size=16),
                        bgcolor=bg_money, padding=ft.padding.symmetric(horizontal=10, vertical=5), 
                        border_radius=8
                    )
                ], alignment="spaceBetween"),
                padding=15, bgcolor="white", border_radius=12,
                shadow=ft.BoxShadow(blur_radius=2, color=ft.colors.with_opacity(0.05, "black"))
            )
            list_col.controls.append(card)

        # 3. CÁC NÚT CHỨC NĂNG
        actions = ft.Column([
            ft.Container(height=10), # Khoảng cách
            
            # Hàng 1: Nộp gà & Ù
            ft.Row([
                ft.Expanded(create_btn("NỘP GÀ (ĂN)", lambda e: goto_selector("Ai bị ăn?", state["players"], on_nop_ga_auto), bg="#FFA726")),
                ft.Container(width=10),
                ft.Expanded(create_btn("XỬ LÝ Ù", lambda e: goto_selector("Ai Ù?", state["players"], on_u_selected), bg="#EF5350")),
            ]),
            
            # Hàng 2: Xếp hạng
            ft.Row([
                ft.Expanded(create_btn("XẾP HẠNG VÁN ĐẤU", lambda e: goto_selector("Ai NHẤT?", state["players"], on_nhat_selected), bg="#42A5F5")),
            ]),
            
            ft.Container(height=10),
            
            # Hàng 3: Công cụ
            ft.Row([
                ft.Expanded(create_btn("LỊCH SỬ", view_history, bg="#78909C")),
                ft.Container(width=10),
                ft.Expanded(create_btn("CÀI ĐẶT", goto_settings, bg="#78909C")),
                ft.Container(width=10),
                ft.Expanded(create_btn("RESET", reset_game, bg="#78909C")),
            ])
        ], spacing=10)

        # Thêm khoảng trống cuối trang để vuốt cho dễ
        page.add(info_card, ft.Container(height=5), list_col, actions, ft.Container(height=30))
        page.update()

    # --- MÀN HÌNH CHỌN (CHUNG) ---
    def goto_selector(title, items, callback, multi=False):
        page.clean()
        
        controls = []
        # Tiêu đề
        controls.append(ft.Container(
            content=ft.Text(title, size=20, weight="bold", color="#333333", text_align="center"),
            padding=ft.padding.only(bottom=20),
            alignment=ft.alignment.center
        ))

        if not multi:
            # Chọn 1 người
            for p in items:
                # Dùng create_btn để giao diện đồng nhất
                btn = create_btn(p["name"], lambda e, x=p: callback(x), bg="white", color="#1976D2")
                # Thêm viền cho nút chọn
                btn.style.side = ft.BorderSide(1, "#1976D2") 
                controls.append(ft.Row([ft.Expanded(btn)]))
                controls.append(ft.Container(height=8))
        else:
            # Chọn nhiều người (Checkbox)
            checks = []
            for p in items:
                cb = ft.Checkbox(label=p["name"], fill_color="#1976D2")
                container = ft.Container(
                    content=cb, padding=10, bgcolor="white", border_radius=8,
                    border=ft.border.all(1, "#E0E0E0")
                )
                checks.append({"cb": cb, "val": p})
                controls.append(container)
                controls.append(ft.Container(height=8))
            
            def submit_multi(e):
                callback([x["val"] for x in checks if x["cb"].value])
            
            controls.append(ft.Container(height=15))
            controls.append(create_btn("XÁC NHẬN", submit_multi, bg="#4CAF50"))

        controls.append(ft.Container(height=20))
        controls.append(
            ft.TextButton("Quay lại / Bỏ qua", on_click=lambda e: (callback(None) if not multi else callback([])), style=ft.ButtonStyle(color="grey"))
        )
        
        page.add(ft.Column(controls))
        page.update()

    # ========================================================
    # LOGIC (GIỮ NGUYÊN NHƯ BẠN ĐÃ TEST)
    # ========================================================
    def on_nop_ga_auto(p):
        if not p: return view_dashboard()
        count = 0
        for log in state["current_logs"]:
            if log.startswith(f"{p['name']}"): count += 1
        
        if count >= 3:
            page.snack_bar = ft.SnackBar(ft.Text(f"{p['name']} đã bị ăn đủ 3 cây!"), bgcolor="red")
            page.snack_bar.open = True; page.update(); return view_dashboard()

        lan_thu = count + 1
        he_so = 1 if lan_thu == 1 else (2 if lan_thu == 2 else 4)
        amt = state["bet"] * he_so
        p["money"] -= amt; state["pot"] += amt
        
        state["current_logs"].append(f"{p['name']} bị ăn cây {lan_thu}: -{int(amt)}k (Gà +{int(amt)}k)")
        page.snack_bar = ft.SnackBar(ft.Text(f"Thu {p['name']} cây thứ {lan_thu} ({int(amt)}k)"), bgcolor="green")
        page.snack_bar.open = True; view_dashboard()

    def on_nhat_selected(nhat):
        if not nhat: return view_dashboard()
        temp_data.clear(); temp_data["nhat"] = nhat
        others = [p for p in state["players"] if p != nhat]
        goto_selector("Ai bị MÓM?", others, on_mom_selected, multi=True)

    def on_mom_selected(moms):
        temp_data["moms"] = moms
        nhat = temp_data["nhat"]
        normals = [p for p in state["players"] if p != nhat and p not in moms]
        if len(normals) <= 1:
            if len(normals) == 1: temp_data["nhi"] = normals[0]
            finalize_rank()
        else: goto_selector("Ai về NHÌ?", normals, on_nhi_selected)

    def on_nhi_selected(nhi):
        if not nhi: return finalize_rank()
        temp_data["nhi"] = nhi
        nhat = temp_data["nhat"]; moms = temp_data["moms"]
        remaining = [p for p in state["players"] if p not in [nhat, nhi] + moms]
        if len(remaining) > 1: goto_selector("Ai về BA?", remaining, on_ba_selected)
        else: finalize_rank()

    def on_ba_selected(ba):
        if ba: temp_data["ba"] = ba
        finalize_rank()

    def finalize_rank():
        nhat = temp_data["nhat"]; moms = temp_data["moms"]
        normal_losers = []
        if "nhi" in temp_data: normal_losers.append(temp_data["nhi"])
        if "ba" in temp_data: normal_losers.append(temp_data["ba"])
        accounted = [nhat] + moms + normal_losers
        normal_losers.extend([p for p in state["players"] if p not in accounted])

        total_win = 0; rank_details = []
        for p in moms:
            amt = state["bet"] * 4; p["money"] -= amt; total_win += amt
            rank_details.append(f"{p['name']} (Móm): -{int(amt)}k")
        for i, p in enumerate(normal_losers):
            amt = state["bet"] * (i + 1); p["money"] -= amt; total_win += amt
            rank_name = ["Nhì", "Ba", "Bét"][i] if i < 3 else "Bét"
            rank_details.append(f"{p['name']} ({rank_name}): -{int(amt)}k")
            
        nhat["money"] += total_win
        rank_details.insert(0, f"{nhat['name']} (Nhất): +{int(total_win)}k")
        commit_log("Tổng kết ván", rank_details); temp_data.clear(); view_dashboard()

    def on_u_selected(u):
        if not u: return view_dashboard()
        temp_data["u"] = u
        goto_selector("Có ai ĐỀN LÀNG không?", [p for p in state["players"] if p != u], on_den_selected)

    def on_den_selected(den):
        u = temp_data["u"]; tien = state["bet"] * 5; u_details = []
        if den:
            phat = tien * 3; den["money"] -= phat; u["money"] += phat
            u_details.append(f"{den['name']} đền: -{int(phat)}k")
        else:
            for p in state["players"]:
                if p != u: p["money"] -= tien; u["money"] += tien; u_details.append(f"{p['name']}: -{int(tien)}k")
        if state["pot"] > 0:
            u["money"] += state["pot"]; u_details.append(f"Ăn gà: +{int(state['pot'])}k"); state["pot"] = 0
        u_details.insert(0, f"{u['name']} Ù"); commit_log("Ván Ù", u_details); view_dashboard()

    def view_history(e):
        page.clean()
        controls = [ft.Text("Lịch sử đấu", size=24, weight="bold", color="#333333")]
        if not state["history"]: controls.append(ft.Text("Trống", color="grey"))
        else:
            for log in state["history"]:
                detail_col = ft.Column(spacing=2)
                for line in log["details"]:
                    txt_color = "green" if "+" in line else ("red" if "-" in line else "black")
                    if "---" in line: txt_color = "grey"
                    detail_col.controls.append(ft.Text(line, size=14, color=txt_color))
                controls.append(ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text(log["title"], weight="bold"), ft.Text(log["time"], size=12, color="grey")], alignment="spaceBetween"),
                        ft.Divider(height=1), detail_col
                    ]), padding=15, bgcolor="white", border_radius=10, border=ft.border.all(1, "#EEEEEE")
                ))
        controls.append(ft.Container(height=20))
        controls.append(create_btn("QUAY LẠI", lambda e: view_dashboard(), bg="grey"))
        page.add(ft.Column(controls)); page.update()

    def goto_rename(player):
        page.clean()
        tf_name = ft.TextField(label="Tên mới", value=player["name"], text_align="center", text_size=20)
        def save(e): 
            if tf_name.value.strip(): player["name"] = tf_name.value.strip()
            view_dashboard()
        page.add(ft.Column([ft.Text("Đổi tên", size=24), tf_name, create_btn("LƯU", save, bg="#4CAF50")], spacing=20))
        page.update()

    def goto_settings(e):
        page.clean()
        tf = ft.TextField(value=str(int(state["bet"])), text_align="center", keyboard_type="number")
        def save(e):
            try: state["bet"] = float(tf.value)
            except: pass
            view_dashboard()
        page.add(ft.Column([ft.Text("Cài đặt cược", size=24), tf, create_btn("LƯU", save, bg="#4CAF50")], spacing=20))
        page.update()

    def reset_game(e):
        for p in state["players"]: p["money"] = 0
        state["pot"] = 0; state["history"] = []; state["current_logs"] = []
        view_dashboard()

    view_dashboard()

ft.app(target=main)
