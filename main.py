import flet as ft
from datetime import datetime

# --- BẢNG MÀU HOÀNG GIA (Dùng mã Hex trực tiếp để tránh lỗi Android) ---
COLOR_BG = "#F5F7FA"          
COLOR_CARD = "#FFFFFF"        
COLOR_TEXT_MAIN = "#2C3E50"   
COLOR_GOLD = "#B8860B"        
# Mã màu có độ trong suốt (Alpha Hex): 26 = 15% opacity
COLOR_SHADOW = "#26000000" 

# Các màu nút bấm
COLOR_BTN_PRIMARY = "#1A237E" 
COLOR_BTN_DANGER = "#C62828"
COLOR_BTN_ORANGE = "#F57C00"
COLOR_BTN_GREY = "#546E7A"

DEF_BET = 10
PLAYERS_DEF = ["Người 1", "Người 2", "Người 3", "Người 4"]

def main(page: ft.Page):
    # Cấu hình Android
    page.title = "TÁ LẢ HOÀNG GIA"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = COLOR_BG
    page.padding = 0 
    page.safe_area = True 

    # --- BIẾN TOÀN CỤC ---
    state = {
        "bet": DEF_BET,
        "pot": 0,
        "players": [{"name": n, "money": 0} for n in PLAYERS_DEF],
        "history": [],      
        "current_logs": []
    }
    
    temp_data = {}

    # --- UI COMPONENT: NÚT 3D (Đã sửa lỗi ft.colors) ---
    def create_3d_btn(text, action, bg_color, height=55, text_size=14):
        # Tạo màu tối hơn cho gradient thủ công
        # (Để tránh dùng ft.colors.with_opacity gây lỗi)
        return ft.Container(
            content=ft.Text(text, size=text_size, weight="bold", color="white", text_align="center"),
            on_click=action,
            alignment=ft.Alignment(0, 0), # Dùng tọa độ thay vì ft.alignment.center
            height=height,
            border_radius=12,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[
                    bg_color,
                    bg_color # Dùng màu phẳng cho an toàn trên Android
                ],
            ),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color="#66000000", # Bóng đen mờ
                offset=ft.Offset(0, 4),
            ),
            ink=True,
            expand=True
        )

    # --- UI COMPONENT: THẺ NGƯỜI CHƠI ---
    def create_player_card(p):
        money_val = int(p['money'])
        money_color = "#2E7D32" if money_val >= 0 else "#C62828" 
        money_bg = "#E8F5E9" if money_val >= 0 else "#FFEBEE"
        
        return ft.Container(
            padding=15,
            border_radius=15,
            bgcolor=COLOR_CARD,
            border=ft.border.all(1, "#E0E0E0"),
            shadow=ft.BoxShadow(blur_radius=10, color=COLOR_SHADOW, offset=ft.Offset(2, 4)),
            content=ft.Row([
                # Avatar & Tên
                ft.Row([
                    ft.Container(
                        # Dùng chuỗi tên icon thay vì ft.icons.PERSON
                        content=ft.Icon(name="person", size=28, color="white"),
                        padding=8,
                        bgcolor=COLOR_GOLD, 
                        border_radius=50,
                    ),
                    ft.Column([
                        ft.Text(p["name"], weight="bold", size=16, color=COLOR_TEXT_MAIN),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(name="edit", size=12, color="grey"),
                                ft.Text("Đổi tên", size=12, color="grey")
                            ], spacing=3),
                            on_click=lambda e, x=p: goto_rename(x),
                            padding=ft.padding.only(top=2, bottom=2)
                        )
                    ], spacing=2),
                ]),
                # Hiển thị tiền
                ft.Container(
                    content=ft.Text(f"{money_val:,} k", color=money_color, weight="bold", size=16),
                    bgcolor=money_bg,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=8,
                    border=ft.border.all(1, money_color) # Viền màu theo tiền
                )
            ], alignment="spaceBetween")
        )

    # --- LOGIC (GIỮ NGUYÊN) ---
    def commit_log(title, result_details):
        timestamp = datetime.now().strftime("%H:%M")
        final = []
        if state["current_logs"]:
            final.append("--- Diễn biến ---")
            final.extend(state["current_logs"])
            final.append("--- Kết quả ---")
        final.extend(result_details)
        state["history"].insert(0, {"time": timestamp, "title": title, "details": final})
        state["current_logs"] = []

    # --- MÀN HÌNH CHÍNH ---
    def view_dashboard():
        page.clean()
        
        # 1. Header Sang Trọng
        header = ft.Container(
            padding=ft.padding.symmetric(vertical=20, horizontal=15),
            border_radius=ft.border_radius.only(bottom_left=25, bottom_right=25),
            gradient=ft.LinearGradient(
                colors=["#1F2937", "#111827"], 
                begin=ft.alignment.top_left, end=ft.alignment.bottom_right
            ),
            shadow=ft.BoxShadow(blur_radius=15, color="black", offset=ft.Offset(0, 5)),
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("MỨC CƯỢC", size=11, color="#9CA3AF", weight="bold"),
                        ft.Text(f"{int(state['bet']):,} K", size=24, weight="bold", color="white")
                    ], horizontal_alignment="center", expand=True),
                    
                    ft.Container(width=1, height=40, bgcolor="#374151"), 
                    
                    ft.Column([
                        ft.Text("QUỸ GÀ", size=11, color=COLOR_GOLD, weight="bold"),
                        ft.Text(f"{int(state['pot']):,} K", size=32, weight="bold", color=COLOR_GOLD)
                    ], horizontal_alignment="center", expand=True),
                ])
            ])
        )

        # 2. Danh sách người chơi
        list_view = ft.Column(spacing=12, scroll=ft.ScrollMode.HIDDEN)
        for p in state["players"]:
            list_view.controls.append(create_player_card(p))
        
        body = ft.Container(
            content=list_view,
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            expand=True 
        )

        # 3. Khu vực nút bấm
        actions = ft.Container(
            padding=20,
            bgcolor="white",
            border_radius=ft.border_radius.only(top_left=25, top_right=25),
            shadow=ft.BoxShadow(blur_radius=20, color=COLOR_SHADOW),
            content=ft.Column([
                ft.Row([
                    create_3d_btn("NỘP GÀ", lambda e: goto_selector("AI BỊ ĂN?", state["players"], on_nop_ga_auto), COLOR_BTN_ORANGE),
                    create_3d_btn("XỬ LÝ Ù", lambda e: goto_selector("AI Ù?", state["players"], on_u_selected), COLOR_BTN_DANGER),
                ], spacing=15),
                
                ft.Container(height=5),
                
                ft.Row([
                    create_3d_btn("XẾP HẠNG VÁN ĐẤU", lambda e: goto_selector("AI VỀ NHẤT?", state["players"], on_nhat_selected), COLOR_BTN_PRIMARY),
                ]),
                
                ft.Container(height=5),
                
                ft.Row([
                    create_3d_btn("LỊCH SỬ", view_history, COLOR_BTN_GREY, height=45, text_size=13),
                    create_3d_btn("CÀI ĐẶT", goto_settings, "#78909C", height=45, text_size=13),
                    create_3d_btn("RESET", reset_game, "#78909C", height=45, text_size=13),
                ], spacing=10)
            ])
        )

        page.add(ft.Column([header, body, actions], spacing=0, expand=True))
        page.update()

    # --- MÀN HÌNH CHỌN ---
    def goto_selector(title, items, callback, multi=False):
        page.clean()
        
        controls = []
        controls.append(ft.Container(
            content=ft.Text(title, size=22, weight="bold", color=COLOR_TEXT_MAIN),
            padding=ft.padding.only(top=10, bottom=20),
            alignment=ft.Alignment(0, 0)
        ))

        if not multi:
            for p in items:
                btn = ft.Container(
                    content=ft.Text(p["name"], size=16, weight="bold", color=COLOR_BTN_PRIMARY),
                    padding=15,
                    border_radius=10,
                    bgcolor="white",
                    border=ft.border.all(1, COLOR_BTN_PRIMARY),
                    shadow=ft.BoxShadow(blur_radius=5, color=COLOR_SHADOW),
                    on_click=lambda e, x=p: callback(x),
                    alignment=ft.Alignment(0, 0),
                    ink=True
                )
                controls.append(btn)
        else:
            checks = []
            for p in items:
                cb = ft.Checkbox(label=p["name"], fill_color=COLOR_BTN_PRIMARY)
                con = ft.Container(
                    content=cb, padding=12, border_radius=10, bgcolor="white",
                    border=ft.border.all(1, "#E0E0E0"), shadow=ft.BoxShadow(blur_radius=2, color=COLOR_SHADOW)
                )
                checks.append({"cb": cb, "val": p})
                controls.append(con)
            
            def submit(e): callback([x["val"] for x in checks if x["cb"].value])
            controls.append(create_3d_btn("XÁC NHẬN", submit, "#00C853"))

        controls.append(ft.Container(height=10))
        controls.append(ft.TextButton("Quay lại", on_click=lambda e: (callback(None) if not multi else callback([])), style=ft.ButtonStyle(color="grey")))
        
        page.add(ft.SafeArea(ft.Container(
            content=ft.Column(controls, spacing=12, scroll=ft.ScrollMode.AUTO),
            padding=20
        )))
        page.update()

    # --- LOGIC ---
    def on_nop_ga_auto(p):
        if not p: return view_dashboard()
        count = sum(1 for log in state["current_logs"] if log.startswith(f"{p['name']}"))
        if count >= 3:
            page.snack_bar = ft.SnackBar(ft.Text(f"{p['name']} đã nộp đủ 3 lần!", color="white"), bgcolor="red")
            page.snack_bar.open = True; page.update(); return view_dashboard()
        
        lan_thu = count + 1
        he_so = 4 if lan_thu == 3 else (2 if lan_thu == 2 else 1)
        amt = state["bet"] * he_so
        p["money"] -= amt; state["pot"] += amt
        state["current_logs"].append(f"{p['name']} bị ăn cây {lan_thu}: -{int(amt)}k (Gà +{int(amt)}k)")
        page.snack_bar = ft.SnackBar(ft.Text(f"Thu {p['name']} cây thứ {lan_thu}: {int(amt)}k"), bgcolor="#00C853")
        page.snack_bar.open = True; view_dashboard()

    def on_nhat_selected(nhat):
        if not nhat: return view_dashboard()
        temp_data.clear(); temp_data["nhat"] = nhat
        goto_selector("AI BỊ MÓM (NẾU CÓ):", [p for p in state["players"] if p != nhat], on_mom_selected, multi=True)

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
        nhat, moms = temp_data["nhat"], temp_data["moms"]
        normal_losers = []
        if "nhi" in temp_data: normal_losers.append(temp_data["nhi"])
        if "ba" in temp_data: normal_losers.append(temp_data["ba"])
        accounted = [nhat] + moms + normal_losers
        normal_losers.extend([p for p in state["players"] if p not in accounted])

        total_win = 0
        details = []
        for p in moms:
            amt = state["bet"] * 4; p["money"] -= amt; total_win += amt
            details.append(f"{p['name']} (Móm): -{int(amt)}k")
        for i, p in enumerate(normal_losers):
            amt = state["bet"] * (i + 1); p["money"] -= amt; total_win += amt
            rank = ["Nhì", "Ba", "Bét"][i] if i < 3 else "Bét"
            details.append(f"{p['name']} ({rank}): -{int(amt)}k")
        nhat["money"] += total_win
        details.insert(0, f"{nhat['name']} (Nhất): +{int(total_win)}k")
        commit_log("Tổng kết ván", details); temp_data.clear(); view_dashboard()

    def on_u_selected(u):
        if not u: return view_dashboard()
        temp_data["u"] = u
        goto_selector("CÓ AI ĐỀN LÀNG KHÔNG?", [p for p in state["players"] if p != u], on_den_selected)

    def on_den_selected(den):
        u = temp_data["u"]
        tien = state["bet"] * 5; details = []
        if den:
            phat = tien * 3; den["money"] -= phat; u["money"] += phat
            details.append(f"{den['name']} đền: -{int(phat)}k")
        else:
            for p in state["players"]:
                if p != u: p["money"] -= tien; u["money"] += tien; details.append(f"{p['name']}: -{int(tien)}k")
        if state["pot"] > 0:
            u["money"] += state["pot"]; details.append(f"Ăn gà: +{int(state['pot'])}k"); state["pot"] = 0
        details.insert(0, f"{u['name']} Ù"); commit_log("Ván Ù", details); view_dashboard()

    def view_history(e):
        page.clean()
        controls = [ft.Text("LỊCH SỬ ĐẤU", size=22, weight="bold", color=COLOR_TEXT_MAIN)]
        if not state["history"]: controls.append(ft.Text("Chưa có dữ liệu", italic=True, color="grey"))
        else:
            for log in state["history"]:
                lines = []
                for ln in log["details"]:
                    clr = "black"
                    if "---" in ln: clr = "grey"
                    elif "+" in ln: clr = "green"
                    elif "-" in ln: clr = "red"
                    lines.append(ft.Text(ln, size=13, color=clr))
                controls.append(ft.Container(
                    padding=10, border_radius=10, bgcolor="white", border=ft.border.all(1, "#E0E0E0"),
                    content=ft.Column([
                        ft.Row([ft.Text(log["title"], weight="bold"), ft.Text(log["time"], color="grey")], alignment="spaceBetween"),
                        ft.Divider(height=1), ft.Column(lines, spacing=2)
                    ])
                ))
        controls.append(ft.Container(height=10))
        controls.append(create_3d_btn("QUAY LẠI", lambda e: view_dashboard(), COLOR_BTN_GREY))
        page.add(ft.SafeArea(ft.Container(content=ft.Column(controls, scroll=ft.ScrollMode.AUTO), padding=20)))
        page.update()

    def goto_rename(p):
        page.clean()
        tf = ft.TextField(label="Tên mới", value=p["name"], text_size=18, text_align="center", autofocus=True)
        def save(e): 
            if tf.value.strip(): p["name"] = tf.value.strip()
            view_dashboard()
        page.add(ft.SafeArea(ft.Container(
            padding=30, alignment=ft.Alignment(0, 0),
            content=ft.Column([ft.Text("ĐỔI TÊN", size=20, weight="bold"), tf, ft.Container(height=20), create_3d_btn("LƯU", save, "#00C853")])
        ))); page.update()

    def goto_settings(e):
        page.clean()
        tf = ft.TextField(label="Mức cược", value=str(int(state["bet"])), text_size=18, text_align="center", keyboard_type="number")
        def save(e):
            try: state["bet"] = float(tf.value)
            except: pass
            view_dashboard()
        page.add(ft.SafeArea(ft.Container(
            padding=30, alignment=ft.Alignment(0, 0),
            content=ft.Column([ft.Text("CÀI ĐẶT", size=20, weight="bold"), tf, ft.Container(height=20), create_3d_btn("LƯU", save, "#00C853")])
        ))); page.update()

    def reset_game(e):
        for p in state["players"]: p["money"] = 0
        state["pot"] = 0; state["history"] = []; state["current_logs"] = []
        view_dashboard()

    ft.app(target=main)
