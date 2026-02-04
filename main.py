import flet as ft
from datetime import datetime

# --- CẤU HÌNH GIAO DIỆN ---
# Bảng màu Tân Cổ Điển
COLOR_BG = "#121212"          # Nền tối sang trọng
COLOR_CARD_BG = "#1E1E1E"     # Nền thẻ bài
COLOR_GOLD = "#FFD700"        # Vàng kim
COLOR_GOLD_DIM = "#C5A000"    # Vàng tối (để tạo khối)
COLOR_TEXT = "#E0E0E0"        # Chữ trắng ngà
COLOR_GREEN = "#00C853"       # Xanh thắng tiền
COLOR_RED = "#D50000"         # Đỏ thua tiền

DEF_BET = 10
PLAYERS_DEF = ["Người 1", "Người 2", "Người 3", "Người 4"]

def main(page: ft.Page):
    # Cấu hình trang
    page.title = "TÁ LẢ PRO 3D"
    page.theme_mode = ft.ThemeMode.DARK 
    page.bgcolor = COLOR_BG
    page.padding = 0 
    # Tắt cuộn trang chính để giao diện không bị giật, 
    # chúng ta sẽ cuộn bên trong danh sách
    page.scroll = None 

    # --- BIẾN TOÀN CỤC ---
    state = {
        "bet": DEF_BET,
        "pot": 0,
        "players": [{"name": n, "money": 0} for n in PLAYERS_DEF],
        "history": [],      
        "current_logs": []
    }
    
    temp_data = {}

    # --- HÀM UI: TẠO NÚT 3D (AN TOÀN CHO ANDROID) ---
    def create_3d_btn(text, action, base_color="#333333", text_color="white", height=50, expand=True):
        return ft.Container(
            content=ft.Text(text, size=15, weight="bold", color=text_color, text_align="center"),
            on_click=action,
            padding=10,
            alignment=ft.alignment.center,
            height=height,
            expand=expand,
            border_radius=8,
            # Gradient dùng tọa độ số để tránh lỗi phiên bản
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1), # Top Left
                end=ft.Alignment(1, 1),     # Bottom Right
                colors=[
                    base_color,
                    base_color # Dùng màu phẳng giả gradient nhẹ để an toàn nhất
                ],
            ),
            border=ft.border.all(1, ft.colors.with_opacity(0.3, "white")),
            # Shadow nhẹ nhàng
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.with_opacity(0.5, "black"),
                offset=ft.Offset(2, 2),
            ),
            ink=True,
        )
    
    # --- HÀM UI: TẠO THẺ NGƯỜI CHƠI 3D ---
    def create_player_card(p):
        money_color = COLOR_GREEN if p["money"] >= 0 else COLOR_RED
        
        return ft.Container(
            padding=15,
            border_radius=12,
            # Màu nền Card an toàn
            bgcolor=COLOR_CARD_BG,
            border=ft.border.all(1, ft.colors.with_opacity(0.2, COLOR_GOLD)),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.colors.with_opacity(0.4, "black"), offset=ft.Offset(2,2)),
            content=ft.Row([
                # Avatar & Tên
                ft.Row([
                    # SỬA LỖI: Dùng chuỗi tên icon thay vì ft.icons.XXX
                    ft.Icon(name="account_circle", size=40, color=COLOR_GOLD_DIM),
                    ft.Column([
                        ft.Text(p["name"], weight="bold", size=16, color=COLOR_GOLD),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(name="edit", size=12, color="grey"),
                                ft.Text("Sửa tên", size=11, color="grey")
                            ], spacing=2),
                            on_click=lambda e, x=p: goto_rename(x),
                            padding=ft.padding.only(top=2, bottom=2)
                        )
                    ], spacing=2, alignment="center"),
                ]),
                # Tiền (Dạng LED số)
                ft.Container(
                    content=ft.Text(f"{int(p['money']):,} k", color=money_color, weight="bold", size=18, font_family="monospace"),
                    bgcolor="black",
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border_radius=6,
                    border=ft.border.all(1, ft.colors.with_opacity(0.3, money_color))
                )
            ], alignment="spaceBetween")
        )

    # --- HÀM LOGIC CỐT LÕI ---
    def commit_log(title, result_details):
        timestamp = datetime.now().strftime("%H:%M")
        final_details = []
        if state["current_logs"]:
            final_details.append("--- Diễn biến ---")
            final_details.extend(state["current_logs"])
            final_details.append("--- Kết quả ---")
        final_details.extend(result_details)
        state["history"].insert(0, {"time": timestamp, "title": title, "details": final_details})
        state["current_logs"] = []

    # --- MÀN HÌNH CHÍNH (DASHBOARD) ---
    def view_dashboard():
        page.clean()
        
        # 1. Header & Thông tin chung
        header = ft.Container(
            padding=20,
            border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20),
            gradient=ft.LinearGradient(
                colors=["#1F1F1F", "#000000"], 
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1)
            ),
            border=ft.border.only(bottom=ft.BorderSide(2, COLOR_GOLD_DIM)),
            shadow=ft.BoxShadow(blur_radius=15, color="black"),
            content=ft.Column([
                # Tiêu đề
                ft.Container(
                    content=ft.Text("TÁ LẢ PRO", size=24, weight="bold", color=COLOR_GOLD, font_family="serif"),
                    alignment=ft.alignment.center
                ),
                ft.Divider(color=ft.colors.with_opacity(0.3, COLOR_GOLD), height=20),
                # Bảng điểm
                ft.Row([
                    ft.Column([
                        ft.Text("MỨC CƯỢC", size=12, color="grey"),
                        ft.Text(f"{int(state['bet']):,} K", size=22, weight="bold", color="white")
                    ], horizontal_alignment="center"),
                    
                    ft.Container(width=1, height=40, bgcolor=ft.colors.with_opacity(0.3, "white")), # Vạch ngăn
                    
                    ft.Column([
                        ft.Text("QUỸ GÀ", size=12, color=COLOR_GOLD),
                        ft.Text(f"{int(state['pot']):,} K", size=30, weight="bold", color=COLOR_GOLD)
                    ], horizontal_alignment="center"),
                ], alignment="spaceEvenly")
            ])
        )

        # 2. Danh sách người chơi
        list_container = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO)
        for p in state["players"]:
            list_container.controls.append(create_player_card(p))
        
        # Thêm khoảng trống dưới cùng để không bị che
        list_container.controls.append(ft.Container(height=20))

        body = ft.Container(
            content=list_container,
            padding=15,
            expand=True # Quan trọng: Giãn hết phần giữa
        )

        # 3. Thanh công cụ (Dưới cùng)
        actions = ft.Container(
            padding=15,
            bgcolor="#1A1A1A",
            border_radius=ft.border_radius.only(top_left=20, top_right=20),
            shadow=ft.BoxShadow(blur_radius=10, color="black", offset=ft.Offset(0, -2)),
            content=ft.Column([
                ft.Row([
                    create_3d_btn("NỘP GÀ", lambda e: goto_selector("AI NỘP GÀ?", state["players"], on_nop_ga_auto), base_color="#FF8F00", text_color="black"),
                    create_3d_btn("XỬ LÝ Ù", lambda e: goto_selector("AI Ù?", state["players"], on_u_selected), base_color="#D32F2F"),
                ], spacing=10),
                ft.Container(height=5),
                ft.Row([
                    create_3d_btn("XẾP HẠNG VÁN THƯỜNG", lambda e: goto_selector("AI VỀ NHẤT?", state["players"], on_nhat_selected), base_color="#1976D2"),
                ]),
                ft.Container(height=5),
                ft.Row([
                    create_3d_btn("LỊCH SỬ", view_history, base_color="#455A64"),
                    create_3d_btn("CÀI ĐẶT", goto_settings, base_color="#616161"),
                    create_3d_btn("RESET", reset_game, base_color="#616161"),
                ], spacing=10)
            ])
        )

        # --- BỐ CỤC CHÍNH VỚI SafeArea ---
        # SafeArea giúp tránh tai thỏ và cạnh bo tròn của màn hình
        layout = ft.SafeArea(
            ft.Column(
                controls=[header, body, actions],
                spacing=0,
                expand=True
            ),
            expand=True
        )

        page.add(layout)
        page.update()

    # --- CÁC MÀN HÌNH PHỤ ---

    def goto_selector(title, items, callback, multi=False):
        page.clean()
        
        controls = []
        controls.append(ft.Container(
            content=ft.Text(title, size=24, weight="bold", color=COLOR_GOLD, font_family="serif"),
            padding=30, alignment=ft.alignment.center
        ))

        if not multi:
            for p in items:
                btn = ft.Container(
                    content=ft.Text(p["name"], size=18, weight="bold", color="white"),
                    padding=15,
                    border_radius=10,
                    gradient=ft.LinearGradient(colors=["#2C2C2C", "#1A1A1A"]),
                    border=ft.border.all(1, ft.colors.with_opacity(0.5, "#1976D2")),
                    on_click=lambda e, x=p: callback(x),
                    alignment=ft.alignment.center
                )
                controls.append(btn)
        else:
            checks = []
            for p in items:
                cb = ft.Checkbox(label=p["name"], fill_color=COLOR_GOLD, check_color="black")
                con = ft.Container(
                    content=cb, padding=15, border_radius=10, bgcolor="#2C2C2C",
                    border=ft.border.all(1, "grey")
                )
                checks.append({"cb": cb, "val": p})
                controls.append(con)
            
            def submit(e): callback([x["val"] for x in checks if x["cb"].value])
            controls.append(create_3d_btn("XÁC NHẬN", submit, base_color=COLOR_GREEN))

        controls.append(ft.Container(height=20))
        controls.append(ft.TextButton("Quay lại / Bỏ qua", on_click=lambda e: (callback(None) if not multi else callback([])), style=ft.ButtonStyle(color="grey")))
        
        # Bọc SafeArea cho màn hình chọn
        page.add(ft.SafeArea(
            ft.Container(
                content=ft.Column(controls, spacing=15, scroll=ft.ScrollMode.AUTO),
                padding=20, expand=True
            )
        ))
        page.update()

    # --- LOGIC GIỮ NGUYÊN ---
    def on_nop_ga_auto(p):
        if not p: return view_dashboard()
        count = 0
        for log in state["current_logs"]:
            if log.startswith(f"{p['name']}"): count += 1
        
        if count >= 3:
            page.snack_bar = ft.SnackBar(ft.Text(f"LỖI: {p['name']} đã nộp đủ 3 lần!", color="white"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return view_dashboard()

        lan_thu = count + 1
        he_so = 4 if lan_thu == 3 else (2 if lan_thu == 2 else 1)
        amt = state["bet"] * he_so
        
        p["money"] -= amt
        state["pot"] += amt
        state["current_logs"].append(f"{p['name']} bị ăn cây {lan_thu}: -{int(amt)}k (Gà +{int(amt)}k)")
        
        page.snack_bar = ft.SnackBar(ft.Text(f"Thu {p['name']} cây thứ {lan_thu}: {int(amt)}k", color="black"), bgcolor=COLOR_GOLD)
        page.snack_bar.open = True
        view_dashboard()

    def on_nhat_selected(nhat):
        if not nhat: return view_dashboard()
        temp_data.clear(); temp_data["nhat"] = nhat
        goto_selector("CHỌN NGƯỜI BỊ MÓM (NẾU CÓ):", [p for p in state["players"] if p != nhat], on_mom_selected, multi=True)

    def on_mom_selected(moms):
        temp_data["moms"] = moms
        normals = [p for p in state["players"] if p != temp_data["nhat"] and p not in moms]
        if len(normals) <= 1: 
            if len(normals) == 1: temp_data["nhi"] = normals[0]
            finalize_rank()
        else: goto_selector("AI VỀ NHÌ?", normals, on_nhi_selected)

    def on_nhi_selected(nhi):
        if not nhi: return finalize_rank()
        temp_data["nhi"] = nhi
        remaining = [p for p in state["players"] if p not in [temp_data["nhat"], nhi] + temp_data["moms"]]
        if len(remaining) > 1: goto_selector("AI VỀ BA?", remaining, on_ba_selected)
        else: finalize_rank()

    def on_ba_selected(ba):
        if ba: temp_data["ba"] = ba
        finalize_rank()

    def finalize_rank():
        nhat = temp_data["nhat"]
        moms = temp_data["moms"]
        normal_losers = []
        if "nhi" in temp_data: normal_losers.append(temp_data["nhi"])
        if "ba" in temp_data: normal_losers.append(temp_data["ba"])
        
        accounted = [nhat] + moms + normal_losers
        normal_losers.extend([p for p in state["players"] if p not in accounted])

        total_win = 0
        rank_details = []

        for p in moms:
            amt = state["bet"] * 4; p["money"] -= amt; total_win += amt
            rank_details.append(f"{p['name']} (Móm): -{int(amt)}k")
            
        for i, p in enumerate(normal_losers):
            amt = state["bet"] * (i + 1); p["money"] -= amt; total_win += amt
            rank_name = ["Nhì", "Ba", "Bét"][i] if i < 3 else "Bét"
            rank_details.append(f"{p['name']} ({rank_name}): -{int(amt)}k")
            
        nhat["money"] += total_win
        rank_details.insert(0, f"{nhat['name']} (Nhất): +{int(total_win)}k")
        commit_log("Tổng kết ván", rank_details)
        temp_data.clear()
        view_dashboard()

    def on_u_selected(u):
        if not u: return view_dashboard()
        temp_data["u"] = u
        goto_selector("CÓ AI ĐỀN LÀNG KHÔNG?", [p for p in state["players"] if p != u], on_den_selected)

    def on_den_selected(den):
        u = temp_data["u"]
        tien = state["bet"] * 5
        u_details = []
        if den:
            phat = tien * 3; den["money"] -= phat; u["money"] += phat
            u_details.append(f"{den['name']} đền: -{int(phat)}k")
        else:
            for p in state["players"]:
                if p != u: 
                    p["money"] -= tien; u["money"] += tien
                    u_details.append(f"{p['name']}: -{int(tien)}k")
        
        if state["pot"] > 0:
            u["money"] += state["pot"]
            u_details.append(f"Ăn gà: +{int(state['pot'])}k")
            state["pot"] = 0
        
        u_details.insert(0, f"{u['name']} Ù: +Tổng tiền")
        commit_log("Ván Ù", u_details)
        view_dashboard()

    def view_history(e):
        page.clean()
        controls = [ft.Text("LỊCH SỬ ĐẤU", size=24, weight="bold", color=COLOR_GOLD)]
        if not state["history"]:
            controls.append(ft.Text("Chưa có dữ liệu", italic=True, color="grey"))
        else:
            for log in state["history"]:
                details = ft.Column()
                for line in log["details"]:
                    clr = COLOR_GOLD if "---" in line else (COLOR_GREEN if "+" in line else (COLOR_RED if "-" in line else "white"))
                    details.controls.append(ft.Text(line, size=14, color=clr))
                
                card = ft.Container(
                    padding=15, border_radius=10, bgcolor="#2C2C2C",
                    border=ft.border.all(1, "grey"),
                    content=ft.Column([
                        ft.Row([ft.Text(log["title"], weight="bold"), ft.Text(log["time"], color="grey")], alignment="spaceBetween"),
                        ft.Divider(color="grey"),
                        details
                    ])
                )
                controls.append(card)
        
        controls.append(ft.Container(height=20))
        controls.append(create_3d_btn("QUAY LẠI", lambda e: view_dashboard(), base_color="#455A64"))
        
        # SafeArea cho lịch sử
        page.add(ft.SafeArea(
            ft.Container(content=ft.Column(controls, scroll=ft.ScrollMode.AUTO), padding=20, expand=True)
        ))
        page.update()

    def goto_rename(player):
        page.clean()
        tf = ft.TextField(label="Tên mới", value=player["name"], text_size=20, text_align="center", border_color=COLOR_GOLD, color="white")
        def save(e):
            if tf.value.strip(): player["name"] = tf.value.strip()
            view_dashboard()
        
        page.add(ft.SafeArea(
            ft.Container(
                padding=30, alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Text("ĐỔI TÊN", size=24, color=COLOR_GOLD, weight="bold"),
                    tf, ft.Container(height=20),
                    create_3d_btn("LƯU THAY ĐỔI", save, base_color=COLOR_GREEN)
                ])
            )
        ))
        page.update()

    def goto_settings(e):
        page.clean()
        tf = ft.TextField(label="Mức cược (k)", value=str(int(state["bet"])), text_size=20, text_align="center", keyboard_type="number", border_color=COLOR_GOLD, color="white")
        def save(e):
            try: state["bet"] = float(tf.value)
            except: pass
            view_dashboard()
        
        page.add(ft.SafeArea(
            ft.Container(
                padding=30, alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Text("CÀI ĐẶT", size=24, color=COLOR_GOLD, weight="bold"),
                    tf, ft.Container(height=20),
                    create_3d_btn("LƯU CÀI ĐẶT", save, base_color=COLOR_GREEN)
                ])
            )
        ))
        page.update()

    def reset_game(e):
        for p in state["players"]: p["money"] = 0
        state["pot"] = 0; state["history"] = []; state["current_logs"] = []
        view_dashboard()

    view_dashboard()

ft.app(target=main)
